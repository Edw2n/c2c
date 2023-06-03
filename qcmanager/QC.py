import os
import cv2
import torch
import argparse
import hashlib
from torchvision import transforms
from utils.inference_process import ToTensor, Normalize
#from tqdm import tqdm

from QC_help import *

os.environ['KMP_DUPLICATE_LIB_OK']='True'


#for a list of image paths
def iqa(img_path_list: list) -> dict:
   '''
   By getting a list of path of images,
   this function returns a dictionary with a key of one of the path of images
   and an item of the list of mos scores of images in the path.
   
   [input]
    - img_path_list: a list of paths that contains user's images
   
   [output]
    - mos_dict: a dictionary with key value as a path of images and item as a list of mos scores of images in the path
   '''
   model = load_model_iqa()
   num_crops = 10
   
   # Multiple paths
   mos_scores = []
   mos_dict = {}
   for images_path in img_path_list:
      for index, img in enumerate(os.listdir(images_path)):
         img_path = images_path + '/' + img
         # data load
         Img = Image(image_path=img_path,
            transform=transforms.Compose([Normalize(0.5, 0.5), ToTensor()]),
            num_crops=num_crops)
         print('----IQAing----')
         mos = iqa_help(model, num_crops, Img)
         mos_scores.append(mos)
      mos_dict[img_path] = mos_scores
   return mos_dict
   
#for a list of images paths
def object_count(img_path_list: list) -> dict:
   '''
   By getting a list of path of images,
   this function returns a dictionary with a key of one of the path of images
   and an item of the list of count of object of the images in the path.
   
   [input]
    - img_path_list: a list of paths that contains user's images
   
   [output]
    - object_dict: a dictionary with key value as a path of images and item as a list of count of of images in the path
   '''
   model = load_model_object_count()
   
   for images_path in img_path_list:
      print('----Object_counting----')
      return object_count_help(model, images_path)

   
#for showing the list of images that are duplicates and to be removed
def duplicates(img_path_list: list) -> list:
   '''
   By getting a list of path of images,
   this function returns a list of paths that needed to be removed as it is the duplicates
   
   [input]
    - img_path_list: a list of paths that contains user's images
   
   [output]
    - paths: a list of duplicate paths that needed to be removed
   '''
   file_path = img_path_list
   duplicates = []
   hash_keys = {}
   paths = []
   for images_path in file_path:
      img_dir = os.listdir(images_path)
      # load the input image and compute the hash
      for index, img in enumerate(img_dir):
         path = images_path + '/' + img
         with open(path, 'rb') as f:
            filehash = hashlib.md5(f.read()).hexdigest()
         if filehash not in hash_keys:
            hash_keys[filehash] = index
         else:
            duplicates.append((index, hash_keys[filehash]))
      for index in duplicates:
         path = images_path + '/' + img_dir[index[0]]
         #os.remove(path)
         paths.append(str(path))
   print('----Duplicates----')
   return paths


def main():
   parser = argparse.ArgumentParser(
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument('-p', '--path', 
                        help='File path of images to QC')
   parser.add_argument('-o', '--output', 
                        help='File path for the result of MOS')
   args = parser.parse_args()
   
   image_path = ['data/samples'] #[args.path]
   
   #IQA
   iqa_ = iqa(image_path)
   #Object count
   object_count_ = object_count(image_path)
   #Remove Duplicates
   duplicate_ = duplicates(image_path)
   
   print(iqa_)
   print(object_count_)
   print(duplicate_)



if __name__ == '__main__':
   main()
   
