import os
import json
import shutil
import argparse

def is_json(name):
    _, ext = os.path.splitext(name)
    return ext == '.json'

def get_annotation_file_path(src_path):
    for filename in os.listdir(src_path):
        if is_json(filename):
            file_path = os.path.join(src_path, filename)
            return file_path

def get_list_of_image_names(path):
    return [filename for filename in os.listdir(path) if not is_json(filename)]

def copy_images_to_dest_path(src_path, dest_path, src_image_names):
    print('Copying images to destination folder...')

    dest_dir_images = os.path.join(dest_path, 'images')
    os.makedirs(dest_dir_images, exist_ok=True)
    for i, filename in enumerate(src_image_names):
        _, ext = os.path.splitext(filename)
        src_file_path = os.path.join(src_path, filename)
        dest_file_path = os.path.join(dest_dir_images, f'img{i}{ext}')
        try:
            shutil.copy(src_file_path, dest_file_path)
        except shutil.SameFileError:
            print('Source and destination are the same')

def get_image_annotations(image_id, data):
    img_ann = []
    for ann in data['annotations']:
        if ann['image_id'] == image_id:
            img_ann.append(ann)
    return img_ann if len(img_ann) != 0 else None

def get_image_info(filename, data):
    for image_info in data['images']:
        if image_info['file_name'] == filename:
            return image_info

def generate_labels(dest_path, data, src_image_names):
    print('Generating labels...')

    dest_dir_labels = os.path.join(dest_path, 'labels')
    os.makedirs(dest_dir_labels, exist_ok=True)
    for i, filename in enumerate(src_image_names):
        img = get_image_info(filename, data)
        img_id = img['id']
        img_w = img['width']
        img_h = img['height']
        img_ann = get_image_annotations(img_id, data)

        if img_ann is not None:
            image_label_path = os.path.join(dest_dir_labels, f'img{i}.txt')
            with open(image_label_path, 'a') as file_object:
                for ann in img_ann:
                    current_category = ann['category_id'] - 1
                    x, y, w, h = ann['bbox']

                    x_center = (x + (x+w))/2
                    y_center = (y + (y+h))/2

                    x_center = x_center / img_w
                    y_center = y_center / img_h
                    w = w / img_w
                    h = h / img_h

                    x_center = format(x_center, '.6f')
                    y_center = format(y_center, '.6f')
                    w = format(w, '.6f')
                    h = format(h, '.6f')

                    file_object.write(f'{current_category} {x_center} {y_center} {w} {h}\n')
                    
def create_data_file(dest_path, train_rel_dir, val_rel_dir, data):
    print('Creating data file...')

    labels = [d['name'] for d in data['categories'] if d['supercategory'] != 'none']

    data_file_path = os.path.join(dest_path, 'data.yaml')
    with open(data_file_path, 'a') as file_object:
        file_object.write(f'train: {train_rel_dir}\n')
        file_object.write(f'valid: {val_rel_dir}\n')
        file_object.write(f'nc: {len(labels)}\n')
        file_object.write(f'names: {labels}')

def get_subdir_names(path):
    return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True)
    parser.add_argument('--train', type=str, required=True) 
    parser.add_argument('--val', type=str, required=True) 

    args = parser.parse_args()
    global_src_path = os.path.join(os.getcwd(), args.src) 
    global_src_root, global_src_dirname = os.path.split(global_src_path)
    global_dest_path = os.path.join(global_src_root, f'{global_src_dirname}_yolo')

    for i, subdir_name in enumerate(get_subdir_names(global_src_path)):
        print(f'--- {subdir_name} ---')
        src_path = os.path.join(global_src_path, subdir_name)
        dest_path = os.path.join(global_dest_path, subdir_name)
        annotation_file_path = get_annotation_file_path(src_path)
        with open(annotation_file_path) as f:
            data = json.load(f)

        src_image_names = get_list_of_image_names(src_path)
        copy_images_to_dest_path(src_path, dest_path, src_image_names)
        generate_labels(dest_path, data, src_image_names)
        print()

    create_data_file(global_dest_path, args.train, args.val, data)

    print('Done!')
