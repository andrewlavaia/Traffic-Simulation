import yaml

def load_map(file_string):
    with open(file_string) as f:
        data_map = yaml.safe_load(f)
    return data_map