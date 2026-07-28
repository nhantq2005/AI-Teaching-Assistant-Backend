import cloudinary.uploader
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

async def upload_file_to_cloudinary(file: UploadFile, folder: str = "documents") -> dict:
    """
    Uploads a file to Cloudinary and returns the response dictionary.
    """
    result = await run_in_threadpool(
        cloudinary.uploader.upload,
        file.file,
        folder=folder,
        resource_type="auto"
    )
    return result
