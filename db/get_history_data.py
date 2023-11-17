import requests
import time
from datetime import datetime
import pytz
import pandas as pd

def timestamp_to_datetime(timestamp, timezone='UTC'):
    """
    Convert a Unix timestamp to a datetime object in the specified timezone.

    :param timestamp: Unix timestamp in seconds
    :param timezone: Timezone for the output datetime object (default is 'UTC')
    :return: datetime object in the specified timezone
    """
    # Create a datetime object from the Unix timestamp
    dt = datetime.utcfromtimestamp(timestamp)

    # Convert the datetime object to the specified timezone
    tz = pytz.timezone(timezone)
    return dt.replace(tzinfo=pytz.utc).astimezone(tz)

def get_historical_kline_data(instId, start_time, end_time, bar=None, limit=100):
    """
    Fetch historical K-line data for a given instrument within a time range.

    :param instId: Instrument ID, e.g., 'BTC-USD-200927'
    :param start_time: Start time for data retrieval, format 'YYYY-MM-DD'
    :param end_time: End time for data retrieval, format 'YYYY-MM-DD'
    :param bar: Time granularity, optional
    :param limit: Number of results to return per request, max 100, optional
    :return: List of all historical data within the time range
    """
    # Convert start and end times to timestamps
    start_timestamp = int(time.mktime(datetime.strptime(start_time, '%Y-%m-%d').timetuple())) * 1000
    end_timestamp = int(time.mktime(datetime.strptime(end_time, '%Y-%m-%d').timetuple())) * 1000

    # API endpoint
    url = 'https://www.okx.com/api/v5/market/history-candles'

    # Initialize variables for pagination
    all_data = []
    before = start_timestamp

    # Fetch data in a loop until we reach the end timestamp
    while True:
        # Request parameters
        params = {
            'instId': instId,
            'before': before,
            'after': before + limit*1000*60,
            'bar': bar,
            'limit': limit
        }

        # Send GET request
        response = requests.get(url, params=params)
        # Handle potential errors
        if response.status_code == 200:
            data = response.json().get('data', [])
            if not data:
                break  # Break the loop if no data is returned
            all_data.extend(data)

            # Get the timestamp of the last fetched candle and use it as the 'after' parameter for the next call
            last_ts = int(data[0][0])
            if last_ts >= end_timestamp:
                break  # Break the loop if we have reached the end timestamp

            before = last_ts
            print(timestamp_to_datetime(before/1000))

        else:
            raise Exception(f"Error fetching data: {response.status_code}, {response.text}")

        # Respect the rate limit
        time.sleep(0.1)  # Sleep for 100ms to avoid hitting the rate limit

    return all_data


column_names = [
    "Timestamp", "Open", "High", "Low", "Close", "Volume", "VolumeCurrency", "VolumeCurrencyQuote", "Confirm"
]
# Example usage
# Replace '<exchange_domain>' with the actual domain of the API.
insid = 'BTC-USDT'
historical_data = get_historical_kline_data(insid, '2020-10-11', '2023-11-12', bar='1m')
df = pd.DataFrame(historical_data, columns=column_names)
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
df_sorted = df.sort_values(by='Timestamp', ascending=True)
df_sorted.to_csv(f'./{insid}.csv', index=False)




