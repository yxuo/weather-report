"""utils.py"""

import csv


def save_data(data):
    """Save data to csv. Create fie if not exists."""
    with open('data/data.csv', 'a+', newline='', encoding='utf8') as file:
        writer = csv.writer(file)
        writer.writerow(data.split(','))
