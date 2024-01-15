import requests
import json

_BASE_URL_ = 'https://query2.finance.yahoo.com'

# Define the fundamentals keys
fundamentals_keys = {
    'financials': [
        # Add all the keys you listed earlier here
        "NetIncome", "TotalRevenue", "GrossProfit",  # etc.
    ]
    # If you have more categories, add them similarly
}

def fetch_financial_data(ticker, keys):
    # Construct the URL for the API request
    url = f"{_BASE_URL_}/v10/finance/quoteSummary/{ticker}?modules=financialData"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        financial_data = data.get('quoteSummary', {}).get('result', [{}])[0].get('financialData', {})

        # Extract and print the specified keys
        extracted_data = {key: financial_data.get(key) for key in keys}
        return extracted_data
    else:
        print("Failed to fetch data")
        return {}

ticker = 'MSFT'  # Replace with your desired ticker
extracted_financials = fetch_financial_data(ticker, fundamentals_keys['financials'])
print(json.dumps(extracted_financials, indent=4))

