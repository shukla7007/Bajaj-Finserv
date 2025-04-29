import cv2
import pytesseract
import re
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import logging

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()


class LabTest(BaseModel):
    test_name: str
    test_value: float
    bio_reference_range: str
    test_unit: str
    lab_test_out_of_range: bool

class LabTestResponse(BaseModel):
    is_success: bool
    data: List[LabTest]


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh


def extract_text(image):
    return pytesseract.image_to_string(image)


def parse_text(text):
    tests = []
    pattern = r"^(.*?)\s+(\d+\.?\d*)\s*([a-zA-Z/]+)?\s*([\d\.\- ]+.*)$"
    matches = re.findall(pattern, text, re.MULTILINE)
    
    for match in matches:
        test_name, value, unit, ref_range = match
        test_name = test_name.strip()
        try:
            value = float(value)
        except ValueError:
            continue
        
        unit = unit.strip() if unit else ""
        ref_range = ref_range.strip()
        
        # Clean up the reference range
        ref_range_clean = ref_range
        if unit and ref_range.endswith(unit):
            ref_range_clean = ref_range[: -len(unit)].strip()
        elif " " in ref_range:
            ref_range_clean = " ".join(ref_range.split()[:2])
        
        # Calculate if out of range
        out_of_range = is_out_of_range(value, ref_range_clean)
        
        tests.append(LabTest(
            test_name=test_name,
            test_value=value,
            bio_reference_range=ref_range_clean,
            test_unit=unit,
            lab_test_out_of_range=out_of_range
        ))
    
    return tests


def is_out_of_range(value, ref_range):
    try:
        if "up to" in ref_range.lower():
            max_val = float(ref_range.lower().replace("up to", "").strip())
            return value > max_val
        
        if "-" in ref_range:
            bounds = ref_range.split("-")
            min_val = float(bounds[0].strip())
            max_val = float(bounds[1].strip().split()[0])
            return value < min_val or value > max_val
        
        return False
    except Exception:
        return False


@app.post("/get-lab-tests", response_model=LabTestResponse)
async def get_lab_tests(file: UploadFile = File(...)):
    try:
        
        contents = await file.read()
        image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to decode the image")

        
        preprocessed_image = preprocess_image(image)
        
        
        text = extract_text(preprocessed_image)
        logger.info(f"Extracted text: {text}")

        
        tests = parse_text(text)
        
        
        response = {
            "is_success": True,
            "data": tests
        }
        return response

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        
        await file.close()

@app.get("/")
def read_root():
    return {"message": "Lab Test Extraction API is running. Visit /docs for Swagger UI."}
