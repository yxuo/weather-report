import csv

def save_data(data):
    with open('data/data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data.split(','))
