import piexif
from PIL import Image

def get_full_exif_data(image_path):
    """Extract full EXIF data, including GPS, Camera, and other metadata."""
    try:
        with Image.open(image_path) as img:
            exif_data = img.info.get('exif')  # Get raw EXIF data
            if exif_data:
                parsed_exif = piexif.load(exif_data)

                # Ensure all key IFDs are present (for completeness)
                for ifd in ("0th", "Exif", "GPS", "1st"):
                    if ifd not in parsed_exif:
                        parsed_exif[ifd] = {}

                print("EXIF Data Extracted:", parsed_exif)  # Optional debug
                return parsed_exif  # Return structured EXIF data

    except Exception as e:
        print(f"Error extracting EXIF from {image_path}: {e}")
    return None  # Return None if there's an error or no EXIF data

def add_exif_to_image(image_path, exif_data):
    """Add EXIF data back to the processed image."""
    if exif_data is None:
        print(f"No EXIF data to add for {image_path}")
        return  # Skip if there's no EXIF data

    try:
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')  # Convert to RGB for JPEG saving with EXIF
            exif_bytes = piexif.dump(exif_data)  # Convert structured data to bytes
            rgb_img.save(image_path, exif=exif_bytes)  # Save with EXIF data

        print(f"EXIF data successfully added to {image_path}")

    except Exception as e:
        print(f"Error adding EXIF to {image_path}: {e}")
