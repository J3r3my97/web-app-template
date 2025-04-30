import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

import dental_image_processing as dip  # Import our image processing module

# Create the FastAPI app
app = FastAPI(
    title="Dental Radiograph Annotation API",
    description="A simple API that annotates teeth in dental radiographs",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """Simple welcome endpoint"""
    return {"message": "Welcome to the Dental Radiograph Annotation API"}

@app.post("/annotate/")
async def annotate_image(image: UploadFile = File(...)):
    """
    Upload a dental radiograph and get back an annotated version
    
    Parameters:
    - image: The dental radiograph file (JPEG or PNG)
    
    Returns:
    - Annotated image and teeth data
    """
    # Check if the file is an image
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read the image file
        image_bytes = await image.read()
        
        # Process the image
        annotated_image_bytes, annotations_data = dip.process_dental_image(image_bytes)
        
        # Return the annotated image as a response
        return Response(
            content=annotated_image_bytes,
            media_type="image/png",
            headers={"X-Teeth-Count": str(annotations_data["teeth_count"])}
        )
    
    except Exception as e:
        # Log the error (in a real app, use proper logging)
        print(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing the image")

@app.post("/annotate-with-data/")
async def annotate_image_with_data(image: UploadFile = File(...)):
    """
    Upload a dental radiograph and get back an annotated version with detailed data
    
    Parameters:
    - image: The dental radiograph file (JPEG or PNG)
    
    Returns:
    - JSON with image data (base64) and teeth annotations
    """
    # Check if the file is an image
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read the image file
        image_bytes = await image.read()
        
        # Process the image
        annotated_image_bytes, annotations_data = dip.process_dental_image(image_bytes)
        
        # Convert image to base64 for JSON response
        import base64
        image_base64 = base64.b64encode(annotated_image_bytes).decode('utf-8')
        
        # Return both the image and data
        return {
            "image": image_base64,
            "annotations": annotations_data
        }
    
    except Exception as e:
        # Log the error
        print(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing the image")

if __name__ == "__main__":
    # Run the application with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)