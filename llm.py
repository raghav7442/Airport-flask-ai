from dotenv import load_dotenv
import os

load_dotenv()
from openai import OpenAI

def llm_res(text,airport_code):
    client = OpenAI(api_key=os.getenv('OPENAI_KEY_KEY'))

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are an assistant that returns flight details in JSON format. Based on the document provided below, return the flight details in the following format:
            
            {{
                "single_trip": {{
                    "flight_no": "",
                    "passenger_name":"",
                    "source_location":"",
                    "departure_date":"",
                    "departure_time":"",
                    "arrival_date":"",
                    "arrival_time":"",
                    "arrival_location":"",
                    "airline_name":""
                }},
                "round_trip": {{
                    "flight_no": "",
                    "passenger_name":"",
                    "source_location":"",
                    "departure_date":"",
                    "departure_time":"",
                    "arrival_date":"",
                    "arrival_time":"",
                    "arrival_location":"",
                    "airline_name":""
                }}
            }}
            Instructions:
            1. If you get only single trip information from the context then only provide single_trip field in json.
            2. If you get both single trip and round trip inforamtions from the context then include both single_trip and round_trip field in Json.
            3. If you get only round trip information from the context then only provide round_trip field in json.
            4. You have to figure out the correct airport city using airport code provided by user, retreive airport name from airport_code and get the airport city where this airport is located.
            5. If the airport city or airport name that you retreived not present in the source_location or arrival_location in single_trip or round_trip field , then return the empty json with empty values inside json.
            
               If there are more than two flight tickets in the ticket than use the following instructions.
            1. If you got the airport city then you have to extract the details for single_trip field( above written json field ) where arrival_location is that either airport city or that airport name and extract the round_trip field(above written json field) where source_location is the either airport city or airport name.
            2. arrival_location in single_trip field and source_location in round_trip field should be equal if there are more than two flight informations in the ticket .
               If there are just two flight or one flight details in the ticket, then just give single_trip and round_trip fields information. 
            3. If the airport city or airport name that you retreived not present in the source_location or arrival_location in single_trip or round_trip field , then return the empty json with empty values inside json.
            do not mention json in this, just return the json data in json formate as shown above.
            Answer query from user question
            also do not include the test formatting in the json , like /n or /t or any other formatting. just return row json, as I have mentioned above.

            if you get the airport city from the airport code if you get text where airport city or code is not there so remember very strictly that you have to return the empty json with empty values inside json.
            Answer:
        """
            },
            {
            "role":"user",
            "content":text + f"airport_code: {airport_code} give the detils in json formate, "
            },
        ]
    )
    answer=completion.choices[0].message.content
    print(answer)
    formatted_json = answer.replace("\n", "").replace("\r", "").replace("```", "").replace("   ", "").strip()
    print(formatted_json)
    return formatted_json

