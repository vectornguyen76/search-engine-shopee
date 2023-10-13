from datetime import datetime

from config import settings
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client.http.exceptions import UnexpectedResponse
from src.extractor.feature_extractor import FeatureExtractor
from src.faiss_search.searcher import FaissSearch
from src.qdrant_search.searcher import QdrantSearch
from src.schemas import Product
from src.utils import LOGGER

# Initialize the feature extractor and FaissSearch instances
feature_extractor = FeatureExtractor()
faiss_search = FaissSearch()
qdrant_search = QdrantSearch()

# Create a FastAPI app instance with the specified title from settings
app = FastAPI(title=settings.APP_NAME)

# Config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def healthcheck() -> bool:
    """Check the server's status."""
    return True


@app.post("/search-image", response_model=list[Product])
async def search_image_qdrant(file: UploadFile = File(...)):
    """
    Endpoint to upload an image, extract features, and perform a search.

    Args:
        file (UploadFile): The image file to be uploaded.

    Returns:
        dict: A dictionary containing search results, including item information.
    """
    try:
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
        search_results = await qdrant_search.search(query_vector=feature, top_k=20)

        result = [Product.from_point(point) for point in search_results.result]

        LOGGER.info(f"Search image successfully, file name: {file.filename}")

        return result

    except UnexpectedResponse as e:
        # Handle the case when Qdrant returns an error and convert it to an exception
        # that FastAPI will understand and return to the client
        LOGGER.error("Could not perform search: %s", e)
        raise HTTPException(status_code=500, detail=e.reason_phrase)


@app.post("/search-image-triton", response_model=list[Product])
async def search_image_triton(file: UploadFile = File(...)):
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
    feature = await feature_extractor.triton_extract_feature(image_path=image_path)

    # Perform a search using the extracted feature vector
    search_results = await qdrant_search.search(query_vector=feature, top_k=20)

    result = [Product.from_point(point) for point in search_results.result]

    LOGGER.info(f"Search image successfully, file name: {file.filename}")

    return result


@app.post("/search-image-faiss", response_model=list[Product])
async def upload_image(file: UploadFile = File(...)):
    """
    Endpoint to upload an image, extract features, and perform a search.

    Args:
        file (UploadFile): The image file to be uploaded.

    Returns:
        dict: A dictionary containing search results, including item information.
    """
    try:
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

        LOGGER.info(f"Search image use faiss successfully, file name: {file.filename}")

        return search_results

    except Exception as e:
        LOGGER.error("Could not perform search: %s", e)
        raise HTTPException(status_code=500, detail=e)
