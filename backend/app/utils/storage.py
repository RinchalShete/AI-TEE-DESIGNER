import os
import cloudinary
import cloudinary.uploader
from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

# Configure Cloudinary with env vars
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

def upload_image_to_cloudinary(file_path: str) -> str:
    """
    Uploads an image file to Cloudinary and returns the secure URL.
    Deletes the local file after successful upload.
    Raises Exception on failure.
    """
    try:
        result = cloudinary.uploader.upload(file_path)
        url = result.get("secure_url")
        os.remove(file_path)  # Clean up local file
        return url
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")

