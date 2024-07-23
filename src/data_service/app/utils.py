"""
data_utils.py

Responsability:
- save,find data (works like a repository)
"""

import csv
import logging
import os
import shutil
from typing import List

app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_folder = f"{app_folder}/data"

CSV_HEADER = "nome,email,telefone,idade"

def save_data(data, test=False):
    """Save data to csv. Create fie if not exists."""
    csv_name = "data.csv" if not test else "$.test_data.csv"
    upsert_csv(data, csv_name)

def upsert_csv(data: str, csv_name: str):
    """Upsert line with unique email"""
    csv_file = f"{data_folder}/{csv_name}"
    temp_file = f"{data_folder}/$.temp_data.csv"
    email = data.split(',')[1]

    # create csv with header
    if not os.path.exists(csv_file):
        print("create new csv")
        with open(csv_file, 'a+', newline='', encoding='utf8') as write_file:
            writer = csv.writer(write_file)
            writer.writerow(CSV_HEADER.split(','))

    with (open(csv_file, 'r', newline='', encoding='utf8') as read_file,
          open(temp_file, 'w+', newline='', encoding='utf8') as write_file):
        reader = csv.reader(read_file)
        writer = csv.writer(write_file)

        found = False
        for row in reader:
            print(f"{row[1]} vs {email}")
            if row[1] == email:
                writer.writerow(data.split(','))
                found = True
            else:
                writer.writerow(row)

        if not found:
            writer.writerow(data.split(','))
    shutil.copy(temp_file, csv_file)
    os.remove(csv_file)
    os.rename(temp_file, csv_file)


def search_data(phone: List[str] = None, test=False):
    """Search data in csv"""
    if not phone:
        return []

    csv_name = "data.csv" if not test else "$.test_data.csv"
    csv_path = f"{data_folder}/{csv_name}"
    csv_file = csv.reader(open(csv_path, "r", encoding='utf8'), delimiter=",")
    result: List[dict] = []
    for row in csv_file:
        _name, _email, _phone, _age = row
        if _phone in phone:
            result.append({
                "name": _name,
                "email": _email,
                "phone": _phone,
                "age": _age,
            })
    return result
