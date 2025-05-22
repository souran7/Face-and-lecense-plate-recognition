import cv2
import torch
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
from typing import List, Dict, Tuple


class LicenseBlur:
    """
    A class to detect and blur license plates in images using YOLOv8.
    """

    def __init__(
        self,
        model_path: str,
        tile_size: int = 1500,
        overlap: int = 500,
        scales: List[float] = [1.0, 2.0, 4.0],
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.6,
        blur_level: int = 51,
        target_class: int = 0  # Assuming license plate is class 0
    ) -> None:
        self.tile_size = tile_size
        self.overlap = overlap
        self.scales = scales
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.blur_level = self.validate_blur_level(blur_level)
        self.target_class = target_class

        # Load YOLOv8 model
        self.model = self.load_model(model_path)

    @staticmethod
    def validate_blur_level(blur_level: int) -> int:
        """Ensures that the blur level is a positive odd integer."""
        if blur_level % 2 == 0:
            blur_level += 1
        return blur_level

    @staticmethod
    def load_model(model_path: str) -> YOLO:
        """Loads the YOLOv8 model from the specified path."""
        return YOLO(model_path)

    @staticmethod
    def split_image_into_tiles(image: np.ndarray, tile_size: int, overlap: int) -> Tuple[List[np.ndarray], List[Tuple[int, int]]]:
        """Splits the image into overlapping tiles."""
        ih, iw, _ = image.shape
        tiles = []
        coordinates = []

        step = tile_size - overlap
        for y in range(0, ih, step):
            for x in range(0, iw, step):
                tile = image[y: y + tile_size, x: x + tile_size]
                tiles.append(tile)
                coordinates.append((x, y))
        return tiles, coordinates

    @staticmethod
    def adaptive_blur(plate_region: np.ndarray, confidence: float, max_blur_level: int = 251) -> np.ndarray:
        """Applies adaptive blurring based on confidence level."""
        blur_strength = int(max_blur_level * (1.0 - confidence))
        blur_strength = max(3, blur_strength | 1)  # Ensure it's an odd number
        return cv2.GaussianBlur(plate_region, (blur_strength, blur_strength), 0)

    @staticmethod
    def filter_invalid_boxes(boxes: List[List[float]], min_size=50, max_aspect_ratio=5.0) -> List[List[float]]:
        """Filters out boxes with unlikely sizes or aspect ratios to reduce false positives."""
        filtered_boxes = []
        for box in boxes:
            x1, y1, x2, y2 = box
            width, height = x2 - x1, y2 - y1
            aspect_ratio = max(width / height, height / width)
            if width >= min_size and height >= min_size and aspect_ratio <= max_aspect_ratio:
                filtered_boxes.append(box)
        return filtered_boxes
    

    @staticmethod
    def blur_license_plates(image: np.ndarray, boxes: List[List[float]], max_blur_level: int = 251) -> Tuple[np.ndarray, List[Dict[str, int]]]:
        """Blurs the regions of the image where license plates are detected and returns the coordinates of blurred areas."""
        license_coordinates = []

        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            plate_region = image[y1:y2, x1:x2]
            if plate_region.size > 0:
                blurred_plate = cv2.GaussianBlur(plate_region, (max_blur_level, max_blur_level), 0)
                image[y1:y2, x1:x2] = blurred_plate
                license_coordinates.append({"X1": x1, "Y1": y1, "X2": x2, "Y2": y2})

        return image, license_coordinates

    @staticmethod
    def merge_boxes(boxes: List[List[float]]) -> List[List[float]]:
        """Merges overlapping bounding boxes into a single bounding box."""
        if not boxes:
            return []

        merged_boxes = []
        boxes = sorted(boxes, key=lambda box: box[0])

        current_box = boxes[0]
        for next_box in boxes[1:]:
            if current_box[2] >= next_box[0] and current_box[3] >= next_box[1]:
                current_box = [
                    min(current_box[0], next_box[0]),
                    min(current_box[1], next_box[1]),
                    max(current_box[2], next_box[2]),
                    max(current_box[3], next_box[3])
                ]
            else:
                merged_boxes.append(current_box)
                current_box = next_box
        merged_boxes.append(current_box)
        return merged_boxes


    def process_image(self, image: np.ndarray) -> Tuple[np.ndarray, bool, List[Dict[str, int]]]:
        """Processes the input image to detect and blur license plates."""
        detections_all = []

        # Multi-scale detection
        for scale in self.scales:
            resized_image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR) if scale != 1.0 else image.copy()
            results = self.model(resized_image, conf=self.conf_threshold, iou=self.iou_threshold)
            detections = results[0].boxes

            for det in detections:
                box, conf, cls = det.xyxy[0].tolist(), det.conf.item(), det.cls.item()
                if cls == self.target_class and conf >= self.conf_threshold:
                    x1, y1, x2, y2 = map(int, box)
                    detections_all.append([x1, y1, x2, y2, conf, cls])

        # Image tiling for additional detection
        tiles, coords = self.split_image_into_tiles(image, self.tile_size, self.overlap)
        for idx, tile in enumerate(tiles):
            if tile.size == 0:
                continue
            for scale in self.scales:
                resized_tile = cv2.resize(tile, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR) if scale != 1.0 else tile.copy()
                results = self.model(resized_tile, conf=self.conf_threshold, iou=self.iou_threshold)
                detections = results[0].boxes

                for det in detections:
                    box, conf, cls = det.xyxy[0].tolist(), det.conf.item(), det.cls.item()
                    if cls == self.target_class and conf >= self.conf_threshold:
                        x1 = int(box[0] / scale) + coords[idx][0]
                        y1 = int(box[1] / scale) + coords[idx][1]
                        x2 = int(box[2] / scale) + coords[idx][0]
                        y2 = int(box[3] / scale) + coords[idx][1]
                        detections_all.append([x1, y1, x2, y2, conf, cls])

        # Filter and merge detections to reduce false positives
        filtered_boxes = self.filter_invalid_boxes([d[:4] for d in detections_all])
        detections_merged = self.merge_boxes(filtered_boxes)

        # Blur license plates and capture the coordinates of blurred areas
        processed_image, license_coordinates = self.blur_license_plates(image.copy(), detections_merged)

        license_plate_detected = len(license_coordinates) > 0
        return processed_image, license_plate_detected, license_coordinates




# Integration with GUI
def run_license_algorithm(image_path: str, model_path: str) -> Tuple[np.ndarray, bool]:
    """Runs the license plate detection and blurring on the selected image."""
    lb = LicenseBlur(model_path=model_path)
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Failed to load image from {image_path}")

    processed_image, license_plate_detected, license_coordinates = lb.process_image(image)
    print(license_plate_detected)
    return processed_image, license_plate_detected, license_coordinates

















































































