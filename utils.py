import os
import json
import fitz
import csv
from typing import Dict, List, Union
import re
from llm import llm_res 
from image import vision  
from pdf2image import convert_from_path
from PIL import Image
def save_chunks(file_path: str) -> str:
    """
    Read text content from PDF or image files
    """
    if file_path.endswith('.pdf'):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        if len(text) == 0:
            print("PDF is not selectable.")
        return text
    elif file_path.endswith((".png", ".jpg", ".tiff", ".webp", ".jpeg")):
        text = vision(file_path)
        return text
    else:
        raise ValueError("Unsupported file format")

def get_json(text: str, airport_code: str) -> Dict:
    """
    Get JSON response from LLM
    """
    data = llm_res(text, airport_code)
    pattern = r'\{.*\}'
    match = re.search(pattern, data, re.DOTALL)
    
    if match:
        json_data = match.group(0)
        return json.loads(json_data)
    else:
        print("No JSON data found.")
        return None

def llm_response(airport_code: str) -> None:
    """
    Process files and get LLM responses
    """
    directory = os.path.join(os.getcwd(), 'app/files')
    file_paths = [os.path.join(directory, f) for f in os.listdir(directory)
                 if os.path.isfile(os.path.join(directory, f))]
    
    json_data = []
    for file in file_paths:
        text = save_chunks(file)
        response = get_json(text, airport_code)
        if response:
            json_data.append(response)
    
    try:
        with open('data.json', 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
    except Exception as e:
        print(f"Error assembling JSON: {str(e)}")

def get_csv() -> None:
    """
    Convert JSON data to CSV format
    """
    try:
        with open('data.json', 'r') as json_file:
            data = json.load(json_file)
        
        # Create CSV directory if it doesn't exist
        csv_dir = os.path.join(os.getcwd(), 'csv_data')
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
            
        csv_file_path = os.path.join(csv_dir, 'flights_data.csv')
        
        # Define CSV headers based on your data structure
        headers = [
            'passenger_name', 'flight_no', 'source_location',
            'departure_date', 'departure_time', 'arrival_date',
            'arrival_time', 'arrival_location', 'airline_name',
            'trip_type'
        ]
        
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for entry in data:
                if 'single_trip' in entry:
                    row = entry['single_trip']
                    row['trip_type'] = 'single'
                    writer.writerow(row)
                elif 'round_trip' in entry:
                    row = entry['round_trip']
                    row['trip_type'] = 'round'
                    writer.writerow(row)
                    
    except Exception as e:
        print(f"Error creating CSV: {str(e)}")

def validate_file_upload(file) -> bool:
    """
    Validate file upload
    """
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'webp'}
    return '.' in file.filename and \
           file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_pdf_to_single_image(pdf_path, output_image_path):
    # Convert PDF to images (one image per page)
    images = convert_from_path(pdf_path)

    # Create a blank image with enough height to fit all pages stacked vertically
    total_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)
    
    # Create a new blank image
    combined_image = Image.new('RGB', (total_width, total_height))

    # Paste each image onto the new combined image
    y_offset = 0
    for img in images:
        combined_image.paste(img, (0, y_offset))
        y_offset += img.height

    # Save the resulting image
    combined_image.save(output_image_path)