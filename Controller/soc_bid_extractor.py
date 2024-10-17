import csv
from collections import defaultdict

def extract_soc_bid_data(file_path):
    """
    Extracts SoC_bid[%] data from a CSV file and organizes it in a dictionary
    where the keys are tuples of (year, month, day, hour) and the values are lists of SoC_bid[%] values.
    
    Args:
    file_path (str): Path to the CSV file.

    Returns:
    dict: A dictionary with time keys and lists of SoC_bid[%] values.
    """
    # Initialize the dictionary to store data
    soc_bid_data = defaultdict(list)

    # Read the CSV file
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Extract necessary columns
            year = row['year']
            month = row['month']
            day = row['day']
            hour = row['hour']
            soc_bid = row['SoC_bid[%]']
            
            # Create the key as a tuple of (year, month, day, hour)
            time_key = (year, month, day, hour)
            
            # Append the SoC_bid value to the list corresponding to the key
            soc_bid_data[time_key].append(soc_bid)
    
    return dict(soc_bid_data)
