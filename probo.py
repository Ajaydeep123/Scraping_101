import requests
import json
import time
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator

class ProbabilityData(BaseModel):
    text: str
    value: int

class ProboEvent(BaseModel):
    id: int
    name: str
    display_name: str
    image_url: str
    yes_price: str
    no_price: str
    trading_info: str
    traders_count_numeric: int
    expiry_date: str
    expiry_date_time_stamp: str
    probability_data: ProbabilityData
    type: str = Field(default="probabilistic")
    is_event_active: bool = Field(default=True)
    available_yes_price: Optional[float] = None
    available_no_price: Optional[float] = None
    
    @validator('yes_price', 'no_price')
    def clean_price(cls, v):
        """Remove '₹ ' prefix from price strings"""
        return v.replace('₹ ', '')

def fetch_homefeed(page: int) -> dict:
    """Fetch homefeed data from the API for the given page number."""
    url = f"https://prod.api.probo.in/api/v2/feed/public/homefeed?page={page}"
    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://probo.in/',
        'Content-type': 'application/json',
        'x-device-os': 'DESKTOP',
        'x-version-name': '10',
        'appid': 'in.probo.pro',
        'Authorization': 'Bearer undefined',
        'Origin': 'https://probo.in',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Priority': 'u=4',
        'TE': 'trailers'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    return data

def validate_and_clean_records(records: List[Dict]) -> List[ProboEvent]:
    """Validate and clean records using Pydantic model."""
    validated_records = []
    for record in records:
        try:
            event = ProboEvent.model_validate(record)
            validated_records.append(event)
        except Exception as e:
            print(f"Failed to validate record {record.get('id', 'unknown')}: {e}")
    return validated_records

def normalize_and_save_to_csv(events: List[ProboEvent], timestamp: str) -> None:
    """Normalize the response data and save it to a new CSV file."""
    if events:
        # Convert Pydantic models to dictionaries
        data = [event.model_dump() for event in events]
        df = pd.json_normalize(data)
        filename = f'homefeed_data_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data extracted for this iteration.")

def get_total_pages(response: dict) -> int:
    """Calculate total pages based on total count and records per page."""
    total_count = response['data']['total_count']
    records_per_page = len(response['data']['records'])
    return -(-total_count // records_per_page)  # Ceiling division

while True:
    try:
        all_events: List[ProboEvent] = []
        first_page = fetch_homefeed(1)
        total_pages = get_total_pages(first_page)
        
        print(f"Found {first_page['data']['total_count']} total records across {total_pages} pages")
        
        # Validate and add records from first page
        validated_records = validate_and_clean_records(first_page['data']['records'])
        all_events.extend(validated_records)
        print(f"Validated and fetched {len(validated_records)} records from page 1")
        
        # Fetch remaining pages
        for page in range(2, total_pages + 1):
            try:
                response_data = fetch_homefeed(page)
                validated_records = validate_and_clean_records(response_data['data']['records'])
                print(f"Validated and fetched {len(validated_records)} records from page {page}")
                all_events.extend(validated_records)
                time.sleep(1)  # Polite delay between requests
            except Exception as e:
                print(f"Error processing page {page}: {e}")
                continue
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        normalize_and_save_to_csv(all_events, timestamp)
        print(f"Total valid records collected: {len(all_events)}")
        print("Waiting for 5 minutes before the next iteration...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    time.sleep(300)
