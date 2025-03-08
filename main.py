from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from paper2blog.converter import PaperConverter
from paper2blog.types import ConversionResponse
import uvicorn
import traceback
import logging
import sys
from datetime import datetime
import os
import uuid
from pathlib import Path
import json


# Configure logging
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = os.path.join(
    log_directory, f"paper2blog_{datetime.now().strftime('%Y%m%d')}.log"
)

# Configure logging settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Create base directory for all papers
PAPERS_BASE_DIR = Path("/home/dongpeijie/workspace/Paper2Blog/tmp")
PAPERS_BASE_DIR.mkdir(parents=True, exist_ok=True)

# Create temporary upload directory
UPLOAD_DIR = Path("/home/dongpeijie/workspace/Paper2Blog/tmp/uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Create directory for saving markdown files
SAVED_MD_DIR = Path("/home/dongpeijie/workspace/Paper2Blog/tmp/saved_md")
SAVED_MD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Paper2Blog API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving images
app.mount(
    "/tmp",
    StaticFiles(directory="/home/dongpeijie/workspace/Paper2Blog/tmp"),
    name="static",
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Paper2Blog API server")
    logger.info(f"Logging to file: {log_filename}")


@app.post("/convert", response_model=ConversionResponse)
async def convert_paper(
    file: UploadFile = File(None),
    url: str = Form(None),
    language: str = Form("english"),
):
    logger.info(
        f"Received conversion request - File: {file.filename if file else None}, URL: {url}, Language: {language}"
    )

    try:
        if not file and not url:
            logger.error("Neither file nor URL provided")
            raise HTTPException(
                status_code=400, detail="Either file or URL must be provided"
            )

        converter = PaperConverter()
        logger.info("Initialized PaperConverter")

        if file:
            try:
                # Generate paper_id from filename without extension
                paper_id = Path(file.filename).stem
                # Create paper-specific directory structure
                paper_dir = PAPERS_BASE_DIR / paper_id
                figures_dir = paper_dir / "figures"
                paper_dir.mkdir(parents=True, exist_ok=True)
                figures_dir.mkdir(parents=True, exist_ok=True)

                # Save the uploaded file
                original_extension = Path(file.filename).suffix
                paper_filepath = paper_dir / f"{paper_id}{original_extension}"
                
                logger.info(f"Saving uploaded file to: {paper_filepath}")
                content = await file.read()
                with open(paper_filepath, "wb") as paper_file:
                    paper_file.write(content)

                logger.info(f"Processing PDF file: {paper_filepath}")
                result: ConversionResponse = await converter.convert_from_pdf(
                    str(paper_filepath), language
                )
                logger.info("Successfully converted PDF file")

                # Save the markdown content and metadata
                md_filepath = paper_dir / f"{paper_id}.md"
                with open(md_filepath, "w") as md_file:
                    md_file.write(result.content)
                
                # Save metadata
                metadata = {
                    "paper_id": paper_id,
                    "original_filename": file.filename,
                    "language": language,
                    "conversion_date": datetime.now().isoformat(),
                    "figures": result.figures if hasattr(result, 'figures') else []
                }
                
                metadata_filepath = paper_dir / "metadata.json"
                with open(metadata_filepath, "w") as metadata_file:
                    json.dump(metadata, metadata_file, indent=2)
                
                logger.info(f"Paper content and metadata saved in: {paper_dir}")

            except Exception as e:
                logger.error(f"Error processing PDF file: {str(e)}")
                logger.debug(f"Detailed error: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=400, detail=f"Error processing PDF: {str(e)}"
                )
        else:
            try:
                logger.info(f"Processing URL: {url}")
                result = await converter.convert_from_url(url, language)
                logger.info("Successfully converted URL content")
            except Exception as e:
                logger.error(f"Error processing URL: {str(e)}")
                logger.debug(f"Detailed error: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=400, detail=f"Error processing URL: {str(e)}"
                )
        logger.error(result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /convert endpoint: {str(e)}")
        logger.error(f"Detailed traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Paper2Blog API server")


if __name__ == "__main__":
    logger.info("Starting development server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
