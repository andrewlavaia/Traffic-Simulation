import csv
import json
import yaml


def load_yaml(filename):
    with open(filename) as f:
        data_map = yaml.safe_load(f)
    return data_map


def save_json(json_data, filename):
    with open(filename, 'w') as outfile:
        json.dump(json_data, outfile)


def load_json(filename):
    with open(filename) as json_file:
        json_data = json.load(json_file,)
    return json_data


def save_bytes(byte_data, filename):
    with open(filename, 'wb') as byte_file:
        byte_file.write(bytes(byte_data))


def load_bytes(filename):
    with open(filename, "rb") as byte_file:
        byte_data = byte_file.read()
    return byte_data


def bytes_to_json(data):
    """converts raw byte stream data to json"""
    encoding = "utf-8"
    if isinstance(data, bytes):
        data = data.decode(encoding)
    json_data = json.loads(data)  # may want to enable parse_floats=decimal.Decimal
    return json_data


def csv_to_dict(filename):
    with open(filename, "rt") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = {row[0]: {header[i]: row[i] for i, val in enumerate(row)} for row in reader}
    return data
