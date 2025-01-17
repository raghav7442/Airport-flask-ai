# Airport Flask AI

This project is a Flask-based web application designed to handle file uploads, extract data from PDFs and images, and store the extracted data in a MySQL database. The application also generates CSV files from the extracted data and provides an API endpoint for handling these operations.

## Features

- **File Upload Handling**: Supports both local files and URLs for PDFs and images.
- **Data Extraction**: Extracts text from PDFs using fitz (PyMuPDF) and processes images using a custom vision module.
- **LLM Integration**: Uses a custom `llm_res` function to process extracted text and generate structured data.
- **Database Storage**: Stores extracted flight data in a MySQL database with tables for travel entries and flight details.
- **CSV Generation**: Generates CSV files from the extracted flight data for easy export and analysis.
- **REST API**: Provides a `/upload` endpoint to handle file uploads and data extraction via JSON requests.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.8+
- MySQL Server

## Setup

### Install Required Python Libraries

Install the required libraries using:
```bash
pip install -r requirements.txt
```

### Clone the Repository

```bash
git clone https://github.com/raghav7442/Airport-flask-ai.git
cd Airport-flask-ai
```

### Configure the Database

Update the `DB_CONFIG` dictionary in the code with your MySQL database credentials.

Run the application once to initialize the database and create the required tables.

### Environment Variables

Set the following environment variables or update the `DB_CONFIG` dictionary directly:

- `DB_HOST`: MySQL host (default: localhost)
- `DB_USER`: MySQL username (default: root)
- `DB_PASSWORD`: MySQL password (default: "")
- `DB_NAME`: Database name (default: flights_db)

### Run the Application

```bash
python app.py
```

The application will start on `http://0.0.0.0:5000`.

## API Endpoint

### Upload and Process Files

- **Endpoint**: `/upload`
- **Method**: `POST`
- **Request Body (JSON)**:
    ```json
    {
        "iTravelEntryID": 12345,
        "iEventID": 67890,
        "iPlannerID": 54321,
        "iUserID": 98765,
        "airportCode": "JFK",
        "fileUploads": [
            "http://example.com/path/to/file.pdf",
            "/local/path/to/image.jpg"
        ]
    }
    ```
- **Response**:
    ```{
    "single_trip": {
        "flight_no": "IndiGo 6E 77",
        "passenger_name": "MR VERNON ANTONIO FERNANDES",
        "source_location": "Kolkata",
        "departure_date": "May 09, 2017",
        "departure_time": "20:45",
        "arrival_date": "May 10, 2017",
        "arrival_time": "00:55",
        "arrival_location": "Bangkok",
        "airline_name": "IndiGo"
    },
    "round_trip": {
        "flight_no": "SpiceJet SG 88",
        "passenger_name": "MR VERNON ANTONIO FERNANDES",
        "source_location": "Bangkok",
        "departure_date": "May 17, 2017",
        "departure_time": "03:50",
        "arrival_date": "May 17, 2017",
        "arrival_time": "06:25",
        "arrival_location": "Delhi",
        "airline_name": "SpiceJet"
    }}

    ```

## Folder Structure

- `uploads/`: Contains uploaded files and generated CSVs.
- `pdfs/`: Stores uploaded PDF files.
- `images/`: Stores uploaded image files.
- `csv/`: Stores generated CSV files.
- `app.py`: Main Flask application file.
- `llm.py`: Custom module for processing extracted text (to be implemented by the user).
- `image.py`: Custom module for processing images (to be implemented by the user).

## Database Schema

### `travel_entries` Table

| Column         | Type         | Description                      |
|----------------|--------------|----------------------------------|
| iTravelEntryID | BIGINT(20)   | Primary key for travel entries   |
| iEventID       | BIGINT(20)   | Event ID                         |
| iPlannerID     | BIGINT(20)   | Planner ID                       |
| iUserID        | BIGINT(20)   | User ID                          |
| airportCode    | VARCHAR(10)  | Airport code                     |
| created_at     | TIMESTAMP    | Timestamp of entry creation      |

### `flights` Table

| Column           | Type         | Description                      |
|------------------|--------------|----------------------------------|
| id               | INT          | Primary key for flights          |
| iTravelEntryID   | VARCHAR(50)  | Foreign key to travel_entries    |
| trip_type        | VARCHAR(20)  | Type of trip (single/round)      |
| flight_no        | VARCHAR(20)  | Flight number                    |
| passenger_name   | VARCHAR(100) | Passenger name                   |
| source_location  | VARCHAR(100) | Source location                  |
| departure_date   | VARCHAR(50)  | Departure date                   |
| departure_time   | VARCHAR(20)  | Departure time                   |
| arrival_date     | VARCHAR(50)  | Arrival date                     |
| arrival_time     | VARCHAR(20)  | Arrival time                     |
| arrival_location | VARCHAR(100) | Arrival location                 |
| airline_name     | VARCHAR(100) | Airline name                     |
| created_at       | TIMESTAMP    | Timestamp of flight creation     |

## Custom Modules

### `llm.py`

This module should contain the `llm_res` function, which processes extracted text and returns structured flight data.

### `image.py`

This module should contain the `vision` function, which processes images and extracts text.

## Example Workflow

1. Upload a PDF or image file via the `/upload` endpoint.
2. The application extracts text from the file.
3. The extracted text is processed using the `llm_res` function.
4. The structured data is saved to the database and a CSV file is generated.
5. The response includes the extracted data, CSV filename, and any errors.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Repository

GitHub: https://github.com/raghav7442/Airport-flask-ai.git