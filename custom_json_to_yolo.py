import os
import json
import shutil
import argparse
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--img_src', type=str, required=True)
parser.add_argument('--json_src', type=str, required=True)
parser.add_argument('--dest', type=str, required=True)


def copy_images_to_dest_path(img_dir_src_path, src_img_names, dest_path):
    print('Copying images to destination folder...')

    dest_dir_images = os.path.join(dest_path, 'images')
    os.makedirs(dest_dir_images, exist_ok=True)

    for i, filename in enumerate(src_img_names):
        ext = get_filename_ext(filename)
        src_file_path = os.path.join(img_dir_src_path, filename)
        dest_file_path = os.path.join(dest_dir_images, f'img{i}{ext}')
        try:
            shutil.copy(src_file_path, dest_file_path)
        except shutil.SameFileError:
            print('Source and destination are the same')

def write_label_files(img_ann, img_dir_src_path, src_img_names, dest_path):
    print('Writing label files...')

    dest_dir_labels = os.path.join(dest_path, 'labels')
    os.makedirs(dest_dir_labels, exist_ok=True)

    for i, filename in enumerate(src_img_names):
        filename_no_ext = get_filename_no_ext(filename)
        if filename_no_ext in img_ann:
            polygons = img_ann[filename_no_ext]
            w, h = get_image_width_and_height(img_dir_src_path, filename)
            write_single_label_file(i, w, h, polygons, dest_dir_labels)

def get_image_width_and_height(img_dir_src_path, img_filename):
    img_file_path = os.path.join(img_dir_src_path, img_filename)
    img = Image.open(img_file_path)
    width = img.width
    height = img.height
    return width, height

def get_filename_no_ext(filename):
    filename_no_ext, _ = os.path.splitext(filename)
    return filename_no_ext

def get_filename_ext(filename):
    _, filename_ext = os.path.splitext(filename)
    return filename_ext

def get_image_annotations(data):
    img_ann = {}
    for filename in data:
        filename_no_ext = get_filename_no_ext(filename)
        file_data = data[filename]
        polygons = []
        for region in file_data['regions']:
            region_attributes = region['shape_attributes']
            x_points = region_attributes['all_points_x']
            y_points = region_attributes['all_points_y']
            polygons.append(zip(x_points, y_points))
        img_ann[filename_no_ext] = polygons
    return img_ann

def write_single_label_file(i, w, h, polygons, dest_dir_labels):
    dest_file_path = os.path.join(dest_dir_labels, f'img{i}.txt')
    with open(dest_file_path, 'a') as file_object:
        for points in polygons:
            points_str = get_points_str(points, w, h)
            file_object.write(f'0 {points_str}\n')
        
def get_points_str(points, w, h):
    norm_points_str_flat = []
    for (x, y) in points:
        x_norm_str = str(format(x / w, '.6f'))
        y_norm_str = str(format(y / h, '.6f'))
        norm_points_str_flat.extend([x_norm_str, y_norm_str])
    points_str = ' '.join(norm_points_str_flat)
    return points_str


if __name__ == '__main__':
    args = parser.parse_args()
    img_src = args.img_src
    json_src = args.json_src
    dest_path = args.dest

    src_img_names = os.listdir(img_src)
    shutil.rmtree(dest_path)

    with open(json_src) as f:
        data = json.load(f)

    img_ann = get_image_annotations(data)
    write_label_files(img_ann, img_src, src_img_names, dest_path)
    copy_images_to_dest_path(img_src, src_img_names, dest_path)

    print('Done!')
