import json

def save_json(obj, path):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def merge_datasets(src_paths, dest_path):
    full_json = {}
    for src_path in src_paths:
        full_json |= load_json(src_path)
    save_json(full_json, dest_path)


if __name__ == '__main__':
    src_paths = [
        '../../../Desktop/L1/data.json',
        '../../../Desktop/L1_Additional/data.json',
        '../../../Desktop/L2/data.json',
    ]
    dest_path = '../../../Desktop/pothole_data/region_data.json'
    merge_datasets(src_paths, dest_path)
