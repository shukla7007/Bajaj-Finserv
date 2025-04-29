import os
import cv2
import pytesseract
import re
import json


IMAGE_FOLDER = "/Users/anshulshukla/bajaj finserv/process_data"


def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    
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
        
        
        ref_range_clean = ref_range
        if unit and ref_range.endswith(unit):
            ref_range_clean = ref_range[: -len(unit)].strip()
        elif " " in ref_range:
            ref_range_clean = " ".join(ref_range.split()[:2])
        
        
        out_of_range = is_out_of_range(value, ref_range_clean)
        
        tests.append({
            "test_name": test_name,
            "test_value": value,
            "bio_reference_range": ref_range_clean,
            "test_unit": unit,
            "lab_test_out_of_range": out_of_range
        })
    
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


def process_images():
    results = {"is_success": False, "data": []}
    
    if not os.path.exists(IMAGE_FOLDER):
        print(f"Error: Folder {IMAGE_FOLDER} does not exist.")
        return
    
    for filename in os.listdir(IMAGE_FOLDER):
        if filename.lower().endswith('.png'):
            image_path = os.path.join(IMAGE_FOLDER, filename)
            print(f"Processing image: {filename}")
            
            
            preprocessed_image = preprocess_image(image_path)
            text = extract_text(preprocessed_image)
            
            
            tests = parse_text(text)
            if tests:
                results["is_success"] = True
                results["data"].append({"is_success": True, "data": tests})
    
    
    if not results["data"]:
        results["is_success"] = False
        print("No valid lab test data found in any image.")
    else:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    process_images()