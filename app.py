from flask import Flask, request, jsonify
import os
import requests
import shutil
import fitz
import json
import csv
from datetime import datetime
import mysql.connector
from urllib.parse import urlparse
from llm import llm_res
from image import vision

app = Flask(__name__)

# Configuration
PDF_FOLDER = 'uploads/pdfs'
IMAGE_FOLDER = 'uploads/images'
CSV_FOLDER = 'uploads/csv'
for folder in [PDF_FOLDER, IMAGE_FOLDER, CSV_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['PDF_FOLDER'] = PDF_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'flights_db')
}

import mysql.connector

def init_database():
    """Creates necessary database tables if they don't exist"""
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    
    # Create the database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")
    
    # Create the travel_entries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS travel_entries (
        iTravelEntryID BIGINT(20) NOT NULL,
        iEventID BIGINT(20) NOT NULL,
        iPlannerID BIGINT(20) NOT NULL,
        iUserID BIGINT(20) NOT NULL,
        airportCode VARCHAR(10) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (iTravelEntryID)
    )
    ''')
    
    # Create the flights table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INT AUTO_INCREMENT PRIMARY KEY,
        iTravelEntryID VARCHAR(50) NOT NULL,
        trip_type VARCHAR(20),
        flight_no VARCHAR(20),
        passenger_name VARCHAR(100),
        source_location VARCHAR(100),
        departure_date VARCHAR(50),
        departure_time VARCHAR(20),
        arrival_date VARCHAR(50),
        arrival_time VARCHAR(20),
        arrival_location VARCHAR(100),
        airline_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (iTravelEntryID) REFERENCES travel_entries(iTravelEntryID)
    )
    ''')
    
    # Commit changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    
def save_travel_entry(data):
    """Saves travel entry data to database"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    query = '''INSERT INTO travel_entries 
    (iTravelEntryID, iEventID, iPlannerID, iUserID, airportCode) 
    VALUES (%s, %s, %s, %s, %s)'''
    
    try:
        cursor.execute(query, (
            data['iTravelEntryID'],
            data['iEventID'],
            data['iPlannerID'],
            data['iUserID'],
            data['airportCode']
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving travel entry: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def save_to_csv(extracted_data, travel_entry_id):
    """Generates CSV file from extracted flight data"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'flight_data_{travel_entry_id}_{timestamp}.csv'
    filepath = os.path.join(CSV_FOLDER, filename)
    
    headers = ['trip_type', 'flight_no', 'passenger_name', 'source_location', 
               'departure_date', 'departure_time', 'arrival_date', 'arrival_time',
               'arrival_location', 'airline_name']
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for data in extracted_data:
            if isinstance(data, str):
                data = json.loads(data)
            for trip_type in ['single_trip', 'round_trip']:
                if trip_type in data and any(data[trip_type].values()):
                    row = data[trip_type]
                    row['trip_type'] = trip_type
                    writer.writerow(row)
    
    return filename

def save_to_database(extracted_data, travel_entry_id):
    """Saves extracted flight data to database"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    query = '''INSERT INTO flights (
        iTravelEntryID, trip_type, flight_no, passenger_name, source_location,
        departure_date, departure_time, arrival_date, arrival_time,
        arrival_location, airline_name
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    
    for data in extracted_data:
        if isinstance(data, str):
            data = json.loads(data)
        for trip_type in ['single_trip', 'round_trip']:
            if trip_type in data and any(data[trip_type].values()):
                trip_data = data[trip_type]
                try:
                    cursor.execute(query, (
                        travel_entry_id,
                        trip_type,
                        trip_data['flight_no'],
                        trip_data['passenger_name'],
                        trip_data['source_location'],
                        trip_data['departure_date'],
                        trip_data['departure_time'],
                        trip_data['arrival_date'],
                        trip_data['arrival_time'],
                        trip_data['arrival_location'],
                        trip_data['airline_name']
                    ))
                except Exception as e:
                    print(f"Error saving flight data: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()

ALLOWED_EXTENSIONS = {
    'pdf': PDF_FOLDER,
    'jpg': IMAGE_FOLDER,
    'jpeg': IMAGE_FOLDER,
    'png': IMAGE_FOLDER,
    'gif': IMAGE_FOLDER,
    'bmp': IMAGE_FOLDER
}

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def is_allowed_file(filename):
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

def get_destination_folder(filename):
    extension = get_file_extension(filename)
    return ALLOWED_EXTENSIONS.get(extension)

def save_file(file_content, file_name, folder):
    file_path = os.path.join(folder, file_name)
    with open(file_path, 'wb') as f:
        f.write(file_content)
    return file_path

def process_url_file(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_name = url.split("/")[-1]
            if is_allowed_file(file_name):
                dest_folder = get_destination_folder(file_name)
                file_path = save_file(response.content, file_name, dest_folder)
                return file_name, dest_folder, file_path
            else:
                raise ValueError(f"Unsupported file type for {url}")
        else:
            raise ValueError(f"Failed to download file from {url}")
    except Exception as e:
        raise ValueError(f"Error processing URL {url}: {str(e)}")

def process_local_file(file_path):
    if not os.path.exists(file_path):
        raise ValueError(f"Local file not found: {file_path}")
    
    file_name = os.path.basename(file_path)
    if not is_allowed_file(file_name):
        raise ValueError(f"Unsupported file type for {file_path}")
    
    dest_folder = get_destination_folder(file_name)
    dest_path = os.path.join(dest_folder, file_name)
    
    try:
        shutil.copy2(file_path, dest_path)
        return file_name, dest_folder, dest_path
    except Exception as e:
        raise ValueError(f"Error copying local file {file_path}: {str(e)}")

@app.route('/upload', methods=['POST'])
def handle_upload():
    """Handles file upload and data extraction"""
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format."}), 400

    data = request.get_json()
    required_fields = [
        "iTravelEntryID", "iEventID", "iPlannerID", "iUserID", "airportCode", "fileUploads"
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    if not save_travel_entry(data):
        return jsonify({"error": "Failed to save travel entry"}), 500

    file_uploads = data.get("fileUploads", [])
    airport_code = data.get("airportCode")
    travel_entry_id = data.get("iTravelEntryID")
    saved_pdfs = []
    saved_images = []
    extracted_data = []
    errors = []

    for file_entry in file_uploads:
        try:
            if isinstance(file_entry, str):
                if file_entry.startswith(('http://', 'https://')):
                    file_name, dest_folder, file_path = process_url_file(file_entry)
                else:
                    file_name, dest_folder, file_path = process_local_file(file_entry)
                
                if dest_folder == PDF_FOLDER:
                    saved_pdfs.append(file_name)
                    doc = fitz.open(file_path)
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    extracted_content = llm_res(text, airport_code)
                    extracted_data.append(extracted_content)

                elif dest_folder == IMAGE_FOLDER:
                    saved_images.append(file_name)
                    text = vision(file_path)
                    extracted_content = llm_res(text, airport_code)
                    extracted_data.append(extracted_content)
            else:
                errors.append(f"Invalid file entry format: {file_entry}")
        except ValueError as e:
            errors.append(str(e))

    if extracted_data:
        try:
            csv_filename = save_to_csv(extracted_data, travel_entry_id)
            save_to_database(extracted_data, travel_entry_id)
        except Exception as e:
            errors.append(f"Error saving data: {str(e)}")

    response = {
        "extractedData": extracted_data,
        "csvFile": csv_filename if extracted_data else None,
        "travelEntryID": travel_entry_id
    }

    if errors:
        response["errors"] = errors

    status_code = 200 if (saved_pdfs or saved_images) else 400
    return jsonify(response), status_code

if __name__ == '__main__':
    init_database()
    app.run(debug=False, host='0.0.0.0', port=5000)