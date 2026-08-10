import os
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def start_spaces_client():

    try:
        session = boto3.session.Session()
        client = session.client(
            "s3",
            region_name=os.getenv("region_name"),
            endpoint_url=os.getenv("endpoint_url"),
            config=Config(signature_version=UNSIGNED)
        )
        logger.info("Successfully Started Spaces Client in 'start_spaces_client'")

    except Exception as e:
        logger.critical(f"Exception {e}: Failed to Start Spaces Client in 'start_spaces_client'")
        raise ValueError

    return client


def weight_dir_check():
    """Creates weights directory if not exists"""

    WEIGHT_DIR = Path("ml/sentiment/distilbert_fp16_onnx")
    WEIGHT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Weight Directory Exists in 'weight_dir_check'")

    
def download_spaces_files(spaces_client):
    """Download weights files if they don't exist"""

    local_files = [
        "ml/sentiment/distilbert_fp16_onnx/distilbert_fp16.onnx",
        "ml/sentiment/distilbert_fp16_onnx/tokenizer.json"
    ]

    weights_exists = all(Path(local_file) for local_file in local_files)

    if not weights_exists:
        spaces_files = [
            "distilbert_fp16_onnx/distilbert_fp16.onnx",
            "distilbert_fp16_onnx/tokenizer.json",
        ]

        for file in spaces_files:
            spaces_client.download_file(
                Bucket=os.getenv("Bucket"), 
                Key=file, 
                Filename=f"ml/sentiment/{file}"
            )
        logger.info("Successfully Downloaded Weight Files in 'download_spaces_files'")

    else:
        logger.info("Weight Files Already Exist")