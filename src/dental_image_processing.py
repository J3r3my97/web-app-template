import io

import cv2
import numpy as np
from PIL import Image


def load_image(image_bytes):
    """
    Load an image from bytes data (from uploaded file)
    
    Parameters:
    image_bytes (bytes): The raw image data
    
    Returns:
    numpy.ndarray: The image as a numpy array
    """
    # Convert bytes to numpy array
    image = np.array(Image.open(io.BytesIO(image_bytes)))
    
    # Convert to grayscale if the image is color
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
    print("Image loaded successfully")
    return image

def enhance_image(image):
    """
    Enhance the dental radiograph for better visibility
    
    Parameters:
    image (numpy.ndarray): The input grayscale image
    
    Returns:
    numpy.ndarray: The enhanced image
    """
    # Apply histogram equalization to improve contrast
    enhanced = cv2.equalizeHist(image)
    
    # Apply slight Gaussian blur to reduce noise
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
    
    print("Image enhanced successfully")
    return enhanced

def detect_teeth(image):
    """
    Very simple tooth detection using thresholding
    For beginners, we'll use basic image processing rather than deep learning
    
    Parameters:
    image (numpy.ndarray): The enhanced grayscale image
    
    Returns:
    list: List of detected teeth regions [(x, y, width, height), ...]
    """
    # Apply threshold to separate teeth (brighter) from background
    _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours to find potential teeth
    teeth_regions = []
    for contour in contours:
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter based on size (basic filtering for demonstration)
        if w > 20 and h > 20 and w < 100 and h < 100:
            teeth_regions.append((x, y, w, h))
    
    print(f"Detected {len(teeth_regions)} potential teeth")
    return teeth_regions

def number_teeth(regions):
    """
    Simple tooth numbering based on position
    
    Parameters:
    regions (list): List of teeth regions [(x, y, width, height), ...]
    
    Returns:
    dict: Dictionary mapping region index to tooth number
    """
    # Sort regions from left to right
    sorted_regions = sorted(regions, key=lambda r: r[0])
    
    # Assign numbers (simplified approach)
    tooth_numbers = {}
    for i, region in enumerate(sorted_regions):
        # In a real app, you'd use a more sophisticated approach
        # This is just a placeholder for demonstration
        tooth_numbers[i] = f"Tooth {i+1}"
    
    return tooth_numbers

def annotate_image(original_image, regions, tooth_numbers):
    """
    Draw annotations on the original image
    
    Parameters:
    original_image (numpy.ndarray): The original grayscale image
    regions (list): List of teeth regions [(x, y, width, height), ...]
    tooth_numbers (dict): Dictionary mapping region index to tooth number
    
    Returns:
    numpy.ndarray: The annotated image
    """
    # Convert grayscale to color for annotations
    annotated_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
    
    # Draw rectangles and numbers for each tooth
    for i, (x, y, w, h) in enumerate(regions):
        # Draw rectangle around tooth
        cv2.rectangle(annotated_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Add tooth number
        cv2.putText(
            annotated_image,
            tooth_numbers[i],
            (x, y-5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )
    
    print("Image annotated successfully")
    return annotated_image

def save_image_to_bytes(image):
    """
    Convert the annotated image back to bytes for response
    
    Parameters:
    image (numpy.ndarray): The annotated image
    
    Returns:
    bytes: The image encoded as bytes
    """
    # Convert numpy array to PIL Image
    if len(image.shape) == 2:  # If grayscale
        pil_image = Image.fromarray(image)
    else:  # If color
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='PNG')
    
    return img_byte_arr.getvalue()

def process_dental_image(image_bytes):
    """
    Main function to process a dental radiograph
    
    Parameters:
    image_bytes (bytes): The raw image data
    
    Returns:
    tuple: (annotated_image_bytes, annotations_data)
    """
    # Step 1: Load the image
    original_image = load_image(image_bytes)
    
    # Step 2: Enhance the image
    enhanced_image = enhance_image(original_image)
    
    # Step 3: Detect teeth
    teeth_regions = detect_teeth(enhanced_image)
    
    # Step 4: Number the teeth
    tooth_numbers = number_teeth(teeth_regions)
    
    # Step 5: Annotate the image
    annotated_image = annotate_image(original_image, teeth_regions, tooth_numbers)
    
    # Step 6: Prepare annotations data (for JSON response)
    annotations_data = {
        "teeth_count": len(teeth_regions),
        "teeth": [
            {
                "number": tooth_numbers[i],
                "position": {
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                }
            }
            for i, (x, y, w, h) in enumerate(teeth_regions)
        ]
    }
    
    # Step 7: Convert annotated image to bytes
    annotated_image_bytes = save_image_to_bytes(annotated_image)
    
    return annotated_image_bytes, annotations_data