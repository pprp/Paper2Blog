from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from paper2blog.converter import PaperConverter
from paper2blog.models import ConversionResponse
import uvicorn
import traceback

app = FastAPI(title="Paper2Blog API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/convert", response_model=ConversionResponse)
async def convert_paper(
    file: UploadFile = File(None),
    url: str = Form(None),
    language: str = Form("english"),
):
    try:
        if not file and not url:
            raise HTTPException(
                status_code=400, detail="Either file or URL must be provided"
            )

        converter = PaperConverter()

        if file:
            try:
                content = await file.read()
                result = await converter.convert_from_pdf(content, language)
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Error processing PDF: {str(e)}"
                )
        else:
            try:
                result = await converter.convert_from_url(url, language)
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Error processing URL: {str(e)}"
                )

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /convert endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
