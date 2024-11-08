import pandas as pd
import requests

# Custom date parser function to convert to string in the desired format


def custom_date_parser(date_str):
    # Convert the string to a datetime object
    parsed_date = pd.to_datetime(date_str)
    # Convert the datetime object to a string in ISO 8601 format
    return parsed_date.strftime('%e/%m/%Y %H:%M')

# Function to read Excel and yield batches of 1000 rows as a list of dictionaries


def read_csv_in_batches(file_path, batch_size=1000):
    df = pd.read_csv(file_path, header=0, parse_dates=[
                     'timestamp'])
    df["timestamp"] = pd.to_datetime(
        df['timestamp'], dayfirst=True)

    df["timestamp"] = df["timestamp"].apply(lambda x: str(x))

    batch = []
    for _, row in df.iterrows():
        batch.append(row.to_dict())
        if len(batch) == batch_size:
            yield batch
            batch = []
    # Yield any remaining rows in the last batch
    if batch:
        yield batch

# Function to send a batch of data to the API


def send_batch_to_api(batch, api_url):
    try:
        response = requests.post(api_url, json=batch)
        if response.status_code == 201:
            print(f"Batch sent successfully: {response.status_code}")
        else:
            print(
                f"Failed to send batch: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending batch: {e}")

# Main function to read CSV, batch data, and send to API


def process_csv_and_send(file_path, api_url, batch_size=1000):
    for batch in read_csv_in_batches(file_path, batch_size):
        send_batch_to_api(batch, api_url)


if __name__ == "__main__":
    # Specify the file path to your CSV file and API URL
    csv_file_path = r'aws_debug\data\6706464197dc20dce6cbaa3b_CONS.csv'
    api_url = r'http://localhost:8030/pods/measurements'

    # Process the CSV and send data in batches
    process_csv_and_send(csv_file_path, api_url, batch_size=1000)

