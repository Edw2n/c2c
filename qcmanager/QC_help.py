import os
import cv2
import numpy as np
import torch
import pandas as pd
import hashlib
from torch.utils.data import DataLoader
from torchvision import transforms
from .utils.inference_process import ToTensor, Normalize
from tqdm import tqdm
from torch.autograd import Variable
from PIL import Image as P_Image

from .utils.models.maniqa import MANIQA
from .utils.models.models import Darknet

from .utils.utils import *
from .utils.datasets import *
from .utils.parse_config import *

from collections import defaultdict
from functools import reduce

os.environ['KMP_DUPLICATE_LIB_OK']='True'
FILE_DIR = os.path.dirname(os.path.realpath(__file__))

#Class for processing images
class Image(torch.utils.data.Dataset):
    def __init__(self, image_path, transform, num_crops=20):
        super(Image, self).__init__()
        self.img_name = image_path.split('/')[-1]
        self.img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.img = np.array(self.img).astype('float32') / 255
        self.img = np.transpose(self.img, (2, 0, 1))

        self.transform = transform

        c, h, w = self.img.shape
        print(self.img.shape)
        new_h = 224
        new_w = 224
        
        #fix bug
        h = new_h if h<=new_h else h
        w = new_w if w<=new_w else w
        self.img = np.resize(self.img, (c,h,w))

        self.img_patches = []

        for i in range(num_crops):
            try: # exeption for randint(0,0)
               top = np.random.randint(0, h - new_h)
               left = np.random.randint(0, w - new_w)
            except Exception as e:
               print("randint error", e)
               top = 0
               left = 0

            patch = self.img[:, top: top + new_h, left: left + new_w]
            self.img_patches.append(patch)
        
        self.img_patches = np.array(self.img_patches)

    def get_patch(self, idx):
        patch = self.img_patches[idx]
        sample = {'d_img_org': patch, 'score': 0, 'd_name': self.img_name}
        if self.transform:
            sample = self.transform(sample)
        return sample

class IQA():
   #config file
   configs = {
   # valid times
   'num_crops': 20,

   # model
   'patch_size': 8,
   'img_size': 224,
   'embed_dim': 768,
   'dim_mlp': 768,
   'num_heads': [4, 4],
   'window_size': 4,
   'depths': [2, 2],
   'num_outputs': 1,
   'num_tab': 2,
   'scale': 0.8,

   # checkpoint path
   "ckpt_path": FILE_DIR + "/ckpt_koniq10k.pt",
   }

   model = None

   def __init__(self, configs=None) -> None:
      if configs:
         self.configs = configs
      self.load_model_iqa()

   #for loading a model for IQA with appropriate checkpoint
   def load_model_iqa(self):
      '''
      This function generates a model for Image Quality Assessment (IQA) 
      
      [output]
      - model: model for IQA
      '''

      #Model Definition
      DEVICE = torch.device("cpu") 
      self.model = MANIQA(embed_dim=self.configs['embed_dim'], num_outputs=self.configs['num_outputs'], dim_mlp=self.configs['dim_mlp'],
         patch_size=self.configs['patch_size'], img_size=self.configs['img_size'], window_size=self.configs['window_size'],
         depths=self.configs['depths'], num_heads=self.configs['num_heads'], num_tab=self.configs['num_tab'], scale=self.configs['scale'])
      
      #path = 'ckpt_koniq10k.pt'
      ckpt = torch.load(self.configs['ckpt_path'], map_location=torch.device("cpu"))
      self.model.load_state_dict(ckpt, strict=False)

   def iqa_help(self, num_crop, img: Image) -> float: 
      '''
      This function returns the mos score of a single image
      
      [input]
      - model: a model for processing IQA
      - num_crop: number of crops to enforce on the image
      - img: a image that needs to be processed for IQA
      
      [output]
      - mos_score: mos_score of the image
      '''
      avg_score = 0
      num_crops = num_crop
      for i in tqdm(range(num_crops)):
         with torch.no_grad():
            self.model.eval()
            patch_sample = img.get_patch(i)
            patch = patch_sample['d_img_org']
            patch = patch.unsqueeze(0)
            score = self.model(patch)
            avg_score += score
      mos_score = avg_score / num_crops
      return mos_score.item()

   def get_iqa(self, img_path: str, num_crops: int, model: object) -> list:
      '''
      get num_crops iqa results of img_path

      [input]
      - img_path: target img_path, string
      - num_crops: number of crops for iqa, int
      - model: iqa model, torch model

      [output]
      - mos_score: iqa score of image (for img_path)
      '''
      
      mos_scores = []
      # data load
      Img = Image(image_path=img_path,
         transform=transforms.Compose([Normalize(0.5, 0.5), ToTensor()]),
         num_crops=num_crops)
      print('----IQAing----')
      mos_score = self.iqa_help(num_crops, Img)
      return mos_score
      
   #for a list of image paths
   def get_scores(self, img_path_list: list) -> dict:
      '''
      By getting a list of path of images,
      this function returns a dictionary with a key of one of the path of images
      and an item of the list of mos scores of images in the path.
      
      [input]
      - img_path_list: a list of paths that contains user's images (each item can be a image path or directory)
      
      [output]
      - mos_dict: a dictionary with key value as a path of image and item as a mos scores(int) of image that matched to image path
      '''
      num_crops = 10
      
      # Multiple paths
      mos_dict = {}
      for target_path in img_path_list:
         if os.path.isdir(target_path):
            for index, img in enumerate(os.listdir(target_path)):
               img_path = target_path + '/' + img
               mos_dict[img_path] = self.get_iqa(img_path, num_crops, self.model)
         else:
            mos_dict[target_path] = self.get_iqa(target_path, num_crops, self.model)
      return mos_dict

class ObjectCounter():
   model = None
   configs = {
      # model
      'batch_size': 1,
      'iou_thres': 0.5,
      'conf_thres': 0.8,
      'nms_thres': 0.4,
      'n_cpu': 0,
      'img_size': 416,
      'use_cuda': False,
      'model_config_path': FILE_DIR + "/utils/yolov3-kitti.cfg",
      'data_config_path': FILE_DIR + "/utils/kitti.data",
      'class_path': FILE_DIR + "/utils/kitti.names",
      'img_size': 416,
      # checkpoint path
      "ckpt_path": FILE_DIR + "/yolov3-kitti.weights",
   }

   def __init__(self, configs=None) -> None:
      if configs:
         self.configs = configs
      self.load_model_object_count()

   #for loading a model for object count with appropriate checkpoint
   def load_model_object_count(self):
      '''
      This function generates a model for counting number of objects in the image
      
      [output]
      - model: model for object count
      '''
      #Model Definition
      DEVICE = torch.device("cpu") 
      self.model = Darknet(self.configs['model_config_path'], img_size=self.configs['img_size'])
      
      #Load checkpoint
      self.model.load_weights(self.configs['ckpt_path'])

   # for an image
   def object_count_one(self, img_path: str) -> int:
      '''
      load img tesor from the img_path and returns the count of objects in the image

      [input]
      - img_path: img_path, string
      
      [output]
      - object_count: the number of objects in the image of img_path, dictionary {IMG_PATH(str): OBJECT_COUNT(int)}
      '''
      # Extract image
      img = np.array(P_Image.open(img_path))
      if img.ndim !=3:
         img = img[:,:,np.newaxis]
      h, w, _ = img.shape
      dim_diff = np.abs(h - w)
      # Upper (left) and lower (right) padding
      pad1, pad2 = dim_diff // 2, dim_diff - dim_diff // 2
      # Determine padding
      pad = ((pad1, pad2), (0, 0), (0, 0)) if h <= w else ((0, 0), (pad1, pad2), (0, 0))
      # Add padding
      input_img = np.pad(img, pad, 'constant', constant_values=127.5) / 255.
      # Resize and normalize
      input_img = resize(input_img, (self.configs['img_size'], self.configs['img_size'], 3), mode='reflect')
      # Channels-first
      input_img = np.transpose(input_img, (2, 0, 1))
      # As pytorch tensor
      input_img = torch.from_numpy(input_img).float().unsqueeze(0)  

      # Configure input
      input_img = Variable(input_img.type(torch.FloatTensor))

      num_objects_dict = {}
      num_objects = [] # 이건 뭐임?

      # Get detections
      with torch.no_grad():
         detections = self.model(input_img)
         detections = non_max_suppression(detections, 80, self.configs['conf_thres'], self.configs['nms_thres']) #80: num_classes
         if detections[0] is None:
            num_objects_dict[img_path] = 0
            # num_objects.append(0)
         else:
            num_objects_dict[img_path] = detections[0].shape[0]
            # num_objects.append(detections[0].shape[0])
      return num_objects_dict

   #for image directory
   def object_count_help(self, dir_path: str) -> list:
      '''
      This function returns the dictionary {"IMAGE_PATH(str)": count of obejcts(int)}
      
      [input]
      - dir_path: a directory that contains images which need to be processed for object count
      
      [output]
      - num_objects_dict: object count information for target directory, {"IMAGE_PATH(str)": count of obejcts(int)}
      '''
      

      folder = ImageFolder(dir_path, img_size=self.configs['img_size'])
      dataloader = DataLoader(folder,
                              batch_size=self.configs['batch_size'], shuffle=False, num_workers=self.configs['n_cpu'])
      
      num_objects = []
      num_objects_dict = {}
      for batch_i, (img_paths, input_imgs) in enumerate(dataloader):
         # Configure input
         input_imgs = Variable(input_imgs.type(torch.FloatTensor))

         # Get detections
         with torch.no_grad():
            detections = self.model(input_imgs)
            detections = non_max_suppression(detections, 80, self.configs['conf_thres'], self.configs['nms_thres']) #80: num_classes
            if detections[0] is None:
               num_objects_dict[img_paths[0]] = 0
               num_objects.append(0)
            else:
               num_objects_dict[img_paths[0]] = detections[0].shape[0]
               num_objects.append(detections[0].shape[0])
      return num_objects_dict

   #for a list of images paths or dirs
   def object_count(self, img_path_list: list) -> dict:
      '''
      By getting a list of path of images,
      this function returns a dictionary with a key of one of the path of images
      and an item of the list of count of object of the images in the path.
      
      [input]
      - img_path_list: a list of paths(or dirs) that contains user's images
      
      [output]
      - object_dict: a dictionary with key value as a path of images and item as a list of count of of images in the path
      '''
      
      object_dict = {}
      
      for path in img_path_list:
         print('----Object_counting----')
         if os.path.isdir(path):
            object_dict.update(self.object_count_help(path))
         else:
            object_dict.update(self.object_count_one(path))

      return object_dict


#for showing the list of images that are duplicates and to be removed
def duplicates(img_path_list: list) -> list:
   '''
   By getting a list of path of images,
   this function returns a list of paths that needed to be removed as it is the duplicates
   
   [input]
    - img_path_list: a list of paths that contains user's images (each item can be a directory or an image path)
   
   [output]
    - duplicates: a list of duplicate paths that needed to be removed
   '''
   file_path = img_path_list
   hash_keys = defaultdict(list)
   duplicates = []

   for images_path in file_path:
      if os.path.isdir(images_path):
         img_dir = os.listdir(images_path)
         # load the input image and compute the hash
         for index, img in enumerate(img_dir):
            path = images_path + '/' + img
            with open(path, 'rb') as f:
               filehash = hashlib.md5(f.read()).hexdigest()
               hash_keys[filehash].append(path)
      else:
         with open(images_path, 'rb') as f:
            filehash = hashlib.md5(f.read()).hexdigest()
            hash_keys[filehash].append(images_path)

   duplicates = reduce(lambda x, y: x + y[1:] if len(y)>1 else x, hash_keys.values(), [])
   print('----Duplicates----')
   return duplicates


class HSV():
   def read_file(self, file_name: str) -> dict:
      ''' 
      [Input]
      - file_name: csv file to read
      [Output]
      - coordinate_dict: a nested dictionary of key - type of object, item - a list of ground truth coordinates of bounding box of the object
         e.g) {'Car': [280, 170, 420, 285], 'Truck': [599.41, 156.40, 629.75, 189.25]}
      '''
      file = pd.read_csv(file_name)

      keys = sorted([*set(file['filename'][i] for i in range(len(file)))])

      file_coordinate_dict = {key: None for key in keys}
      obj_coordinate_dict = {}
      for i in range(len(file)):
         image_file = file['filename'][i]
         object_name = file['object'][i]
         left, top, right, bottom = file['Xordinate'][i], file['Yordinate'][i], file['height'][i], file['weight'][i]
         bbox = [left, top, right, bottom]
         obj_coordinate_dict[object_name] = bbox
         if file_coordinate_dict[image_file] is None:
            file_coordinate_dict[image_file] = obj_coordinate_dict
         else:
            file_coordinate_dict[image_file].update(obj_coordinate_dict)

      return file_coordinate_dict

   def hsv(self, img_path_list, ground_truth: str, padding: int)->dict:
      '''
      Return the average of hsv of the image.

      [Input]
      - img_path_list: a list of paths(or dirs) that contains user's images
      - ground_truth: a csv file of grouth truth of images in the img_path_list
      - padding: edge of the images to pad

      [Output]
      - hsv_dict: a nested dictionary indicating the object as a key and the average of hsv values of the image as an item
         e.g) {'0000001.png': {'Car': [103.59013633923779, 68.72063982823403, 109.96038003220612]}, {'Person': [120.0123, 68.7346, 100.765432]}, ...}
      '''
      # Set ground truth
      grouth_truth_dict = self.read_file(ground_truth)

      # Set files_path
      files_path = ImageFolder(img_path_list, img_size=375).files #img_size: irrelavent 

      keys = sorted([*set((os.path.basename(path).split('/')[-1]) for path in files_path)])
      file_hsv_dict = {key: None for key in keys}

      for path in files_path:
         img = cv2.imread(path, cv2.IMREAD_COLOR) 
         hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
         filename = (os.path.basename(path).split('/')[-1])
         gt_list = grouth_truth_dict[filename]
         hsv_dict = {}
         for obj, bbox in gt_list.items():
            left, right, top, bottom = int(bbox[0]+padding), int(bbox[2]-padding), int(bbox[1]+padding), int(bbox[3]-padding)
            area = hsv[top:bottom, left:right]
            hsv_list = np.mean(area, axis=(0, 1)).tolist()
            hsv_dict[obj] = hsv_list
            if file_hsv_dict[filename] is None:
               file_hsv_dict[filename] = hsv_dict
            else:
               file_hsv_dict[filename].update(hsv_dict)
      return file_hsv_dict
   

