from fastapi import FastAPI, File, UploadFile
from feature_extractor import FeatureExtractor
from faiss_search import FaissSearch
from datetime import datetime
from config import settings

# Create a FastAPI app instance with the specified title from settings
app = FastAPI(title=settings.APP_NAME)

# Initialize the feature extractor and FaissSearch instances
feature_extractor = FeatureExtractor()
faiss_search = FaissSearch()

@app.post("/search-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Endpoint to upload an image, extract features, and perform a search.

    Args:
        file (UploadFile): The image file to be uploaded.

    Returns:
        dict: A dictionary containing search results, including item information.
    """
    # Prepend the current datetime to the filename
    file.filename = datetime.now().strftime("%Y%m%d-%H%M%S-") + file.filename
    
    # Construct the full image path based on the settings
    image_path = settings.IMAGEDIR + file.filename
    
    # Read the contents of the uploaded file asynchronously
    contents = await file.read()
 
    # Write the uploaded contents to the specified image path
    with open(image_path, "wb") as f:
        f.write(contents)
        
    # Extract features from the uploaded image using the feature extractor
    feature = feature_extractor.extract_feature(image_path=image_path)
    
    # Perform a search using the extracted feature vector
    search_results = faiss_search.search(query_vector=feature, top_k=20)
    
    return search_results