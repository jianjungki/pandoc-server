from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import pypandoc
import os
import io
import tempfile
from typing import Optional

app = FastAPI()

@app.post("/convert")
async def convert_file(
    file: UploadFile = File(...),
    to_format: str = "pdf",
    from_format: Optional[str] = None
):
    input_filename: Optional[str] = file.filename
    if not input_filename:
        input_filename = "temp_input" # Provide a default if filename is missing

    if not from_format:
        _, ext = os.path.splitext(input_filename)
        if ext:
            from_format = ext[1:]

    if not from_format:
        raise HTTPException(status_code=400, detail="Could not determine input format. Please specify 'from_format'.")

    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{from_format}") as temp_input_file:
        await file.seek(0) # Ensure we read from the beginning
        content = await file.read()
        temp_input_file.write(content)
        temp_input_path = temp_input_file.name

    # Create a temporary file for the output
    output_filename_base = os.path.splitext(input_filename)[0]
    output_filename = f"{output_filename_base}.{to_format}"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{to_format}") as temp_output_file:
        temp_output_path = temp_output_file.name

    try:
        pypandoc.convert_file(temp_input_path,
            to=to_format,
            format=from_format,
            outputfile=temp_output_path,
            extra_args=['--standalone']
        )
        
        with open(temp_output_path, 'rb') as f:
            output_content = f.read()

        return StreamingResponse(
            io.BytesIO(output_content),
            media_type=f"application/{to_format}",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )

    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=f"Pandoc conversion failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        # Clean up temporary files
        os.remove(temp_input_path)
        os.remove(temp_output_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)