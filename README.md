# Probo Homefeed Scraper

## Overview
This Python script fetches data from the Probo homefeed API, validates and cleans the data using Pydantic models, and saves the results as a CSV file. It runs in a loop, fetching new data every 5 minutes.

## Features
- Fetches paginated data from the Probo API.
- Uses Pydantic for data validation and cleaning.
- Extracts relevant fields and normalizes the data.
- Saves the cleaned data to a CSV file with a timestamp.
- Implements error handling and logging.
- Includes polite delays between API requests to avoid rate-limiting.

## Requirements
### Dependencies
Ensure you have Python 3 installed along with the following dependencies:

```bash
pip install requests pandas pydantic
```

## Usage
Run the script using:

```bash
python probo_scraper.py
```

The script will continuously fetch data every 5 minutes and store the output CSV files in the current directory.

## File Structure
- `probo_scraper.py`: Main script to fetch, validate, and store Probo homefeed data.
- `homefeed_data_YYYYMMDD_HHMMSS.csv`: Output CSV files containing the fetched data.

## Data Fields
The script captures the following fields:
- `id`: Unique event ID
- `name`: Event name
- `display_name`: Display name
- `image_url`: Event image URL
- `yes_price`: Probability price for "Yes"
- `no_price`: Probability price for "No"
- `trading_info`: Additional trading details
- `traders_count_numeric`: Number of traders
- `expiry_date`: Expiry date
- `probability_data`: Probability data
- `type`: Event type (default: probabilistic)
- `is_event_active`: Event active status
- `available_yes_price`: Available "Yes" price
- `available_no_price`: Available "No" price

## API Details
The script fetches data from:
```
https://prod.api.probo.in/api/v2/feed/public/homefeed?page={page}
```

It uses custom headers to mimic browser requests and fetch data.

## Error Handling
- If an API request fails, the script logs an error and continues to the next request.
- If data validation fails for a record, it logs the issue and skips the record.
- If an exception occurs while fetching a page, the script moves to the next one without stopping execution.


## Author
Ajaydeep Singh Rajpoot

