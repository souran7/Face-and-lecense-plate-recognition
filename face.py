import cv2
import numpy as np
from retinaface import RetinaFace

def validate_blur_level(blur_level):
    if blur_level % 2 == 0:
        blur_level += 1  # Ensure odd blur level for Gaussian blur
    if blur_level <= 0:
        blur_level = 101  # Set a default minimum value
    return blur_level

def dynamic_blur_level(face_width, min_blur=101, max_blur=251):
    blur_level = int(min_blur + (face_width / 500) * (max_blur - min_blur))
    return validate_blur_level(blur_level)

def blur_faces(image, detections):
    """Apply Gaussian blur to all detected faces."""
    for detection in detections:
        bbox = detection.get("facial_area")
        if bbox is None:
            continue

        x1, y1, x2, y2 = [max(0, int(coord)) for coord in bbox]

        # Add padding around the face region
        padding = 10
        x1, y1 = max(0, x1 - padding), max(0, y1 - padding)
        x2, y2 = min(image.shape[1], x2 + padding), min(image.shape[0], y2 + padding)

        face_region = image[y1:y2, x1:x2]
        blur_level = dynamic_blur_level(x2 - x1)
        blurred_face = cv2.GaussianBlur(face_region, (blur_level, blur_level), 0)
        image[y1:y2, x1:x2] = blurred_face

    return image

def non_max_suppression(detections, iou_threshold=0.5):
    detections = sorted(detections, key=lambda x: x["score"], reverse=True)
    selected_detections = []
    
    while detections:
        best_detection = detections.pop(0)
        selected_detections.append(best_detection)
        best_bbox = best_detection["facial_area"]
        
        def compute_iou(bbox1, bbox2):
            x1 = max(bbox1[0], bbox2[0])
            y1 = max(bbox1[1], bbox2[1])
            x2 = min(bbox1[2], bbox2[2])
            y2 = min(bbox1[3], bbox2[3])

            inter_area = max(0, x2 - x1) * max(0, y2 - y1)
            bbox1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
            bbox2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
            iou = inter_area / float(bbox1_area + bbox2_area - inter_area)
            return iou

        detections = [d for d in detections if compute_iou(best_bbox, d["facial_area"]) < iou_threshold]
    
    return selected_detections

def multi_scale_detect(image, conf_threshold=0.9):
    detections = RetinaFace.detect_faces(image)
    all_faces = []

    if isinstance(detections, dict):
        for key in detections:
            identity = detections[key]
            box = identity.get("facial_area")
            score = identity.get("score",  0)
            if box is not None and score >= conf_threshold:
                all_faces.append({"facial_area": box, "score": score})

    return all_faces



def split_image_into_tiles(image, tile_size=1200, overlap=100):  
    ih, iw, _ = image.shape
    tiles = []
    coordinates = []

    step = tile_size - overlap
    for y in range(0, ih, step):
        for x in range(0, iw, step):
            tile = image[y:min(y + tile_size, ih), x:min(x + tile_size, iw)]
            tiles.append(tile)
            coordinates.append((x, y))

    return tiles, coordinates

def resize_image(image, scale_factor):
    height, width = image.shape[:2]
    new_size = (int(width * scale_factor), int(height * scale_factor))
    resized_image = cv2.resize(image, new_size)
    return resized_image



# def process_image(image):
#     """Detect, suppress, and blur faces in the given image."""
#     if image is None:
#         return None, False  # Return None for image and False for flag if input is None

#     scaled_image = resize_image(image, 0.5)
#     detections_original = multi_scale_detect(scaled_image, conf_threshold=0.9)

#     # Rescale detections back to the original image size
#     for detection in detections_original:
#         detection["facial_area"] = [int(coord * 2) for coord in detection["facial_area"]]

#     # Image tiling for additional detections
#     tiles, coords = split_image_into_tiles(image, tile_size=1200, overlap=100)  
#     detections_tiling = []

#     for idx, tile in enumerate(tiles):
#         if tile.size == 0:
#             continue
#         detections = multi_scale_detect(tile, conf_threshold=0.6)
#         for det in detections:
#             bbox = det["facial_area"]
#             score = det.get("score", 1.0)
#             if score >= 0.6:
#                 x1, y1, x2, y2 = bbox
#                 orig_x1 = int(x1 + coords[idx][0])
#                 orig_y1 = int(y1 + coords[idx][1])
#                 orig_x2 = int(x2 + coords[idx][0])
#                 orig_y2 = int(y2 + coords[idx][1])
#                 detections_tiling.append({
#                     "facial_area": [orig_x1, orig_y1, orig_x2, orig_y2],
#                     "score": score
#                 })

#     all_detections = detections_original + detections_tiling
#     unique_detections = non_max_suppression(all_detections, iou_threshold=0.5)

#     # Check if any unique detections were made
#     face_detected = len(unique_detections) > 0

#     if not unique_detections:
#         print("No faces detected.")
#         return image, face_detected  # Return original image and False flag

#     print(f"Detected {len(unique_detections)} unique faces.")

#     # Blur detected faces
#     return blur_faces(image.copy(), unique_detections), face_detected  # Return blurred image and True flag



def process_image(image):
    """Detect, suppress, and blur faces in the given image while returning face coordinates."""
    if image is None:
        return None, False, []  # Return None for image, False for flag, and empty list for coordinates

    scaled_image = resize_image(image, 0.5)
    detections_original = multi_scale_detect(scaled_image, conf_threshold=0.9)

    # Rescale detections back to the original image size
    for detection in detections_original:
        detection["facial_area"] = [int(coord * 2) for coord in detection["facial_area"]]

    # Image tiling for additional detections
    tiles, coords = split_image_into_tiles(image, tile_size=1200, overlap=100)
    detections_tiling = []

    for idx, tile in enumerate(tiles):
        if tile.size == 0:
            continue
        detections = multi_scale_detect(tile, conf_threshold=0.6)
        for det in detections:
            bbox = det["facial_area"]
            score = det.get("score", 0)
            if score >= 0.6:
                x1, y1, x2, y2 = bbox
                orig_x1 = int(x1 + coords[idx][0])
                orig_y1 = int(y1 + coords[idx][1])
                orig_x2 = int(x2 + coords[idx][0])
                orig_y2 = int(y2 + coords[idx][1])
                detections_tiling.append({
                    "facial_area": [orig_x1, orig_y1, orig_x2, orig_y2],
                    "score": score
                })

    all_detections = detections_original + detections_tiling
    unique_detections = non_max_suppression(all_detections, iou_threshold=0.5)

    # Check if any unique detections were made
    face_detected = len(unique_detections) > 0
    face_coordinates = []

    if not unique_detections:
        print("No faces detected.")
        return image, face_detected, face_coordinates  # Return original image, False flag, and empty coordinates

    print(f"Detected {len(unique_detections)} unique faces.")

    # Gather formatted coordinates
    for idx, detection in enumerate(unique_detections):
        x1, y1, x2, y2 = detection["facial_area"]
        face_coordinates.append(f"Face: (X1: {x1}, Y1: {y1}, X2: {x2}, Y2: {y2})")

    # Blur detected faces
    blurred_image = blur_faces(image.copy(), unique_detections)

    

    return blurred_image, face_detected, face_coordinates  # Return blurred image, True flag, and face coordinates
