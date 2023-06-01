import os
import cv2
import numpy as np
import torch
import argparse
import hashlib
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from utils.inference_process import ToTensor, Normalize
from tqdm import tqdm
from torchvision.transforms.functional import pil_to_tensor 
from torch.autograd import Variable

from utils.models.maniqa import MANIQA
from utils.models.models import Darknet

from utils.utils import *
from utils.datasets import *
from utils.parse_config import *

os.environ['KMP_DUPLICATE_LIB_OK']='True'

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

        self.img_patches = []
        for i in range(num_crops):
            top = np.random.randint(0, h - new_h)
            left = np.random.randint(0, w - new_w)
            patch = self.img[:, top: top + new_h, left: left + new_w]
            self.img_patches.append(patch)
        
        self.img_patches = np.array(self.img_patches)

    def get_patch(self, idx):
        patch = self.img_patches[idx]
        sample = {'d_img_org': patch, 'score': 0, 'd_name': self.img_name}
        if self.transform:
            sample = self.transform(sample)
        return sample

#for loading a model for IQA with appropriate checkpoint
def load_model_iqa():
   #config file
   config = {
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
    "ckpt_path": "./ckpt_koniq10k.pt",
   }
   
   #Model Definition
   DEVICE = torch.device("cpu") 
   model = MANIQA(embed_dim=config['embed_dim'], num_outputs=config['num_outputs'], dim_mlp=config['dim_mlp'],
        patch_size=config['patch_size'], img_size=config['img_size'], window_size=config['window_size'],
        depths=config['depths'], num_heads=config['num_heads'], num_tab=config['num_tab'], scale=config['scale'])
   
   #path = 'ckpt_koniq10k.pt'
   ckpt = torch.load(config['ckpt_path'], map_location=torch.device("cpu"))
   model.load_state_dict(ckpt, strict=False)

   return model

#for a single image
def iqa_help(model, num_crop, img: Image) -> float: 
   avg_score = 0
   num_crops = num_crop
   for i in tqdm(range(num_crops)):
      with torch.no_grad():
         model.eval()
         patch_sample = img.get_patch(i)
         patch = patch_sample['d_img_org']
         patch = patch.unsqueeze(0)
         score = model(patch)
         avg_score += score
   mos_score = avg_score / num_crops
   return mos_score

#for a list of image paths
def iqa(img_path_list: list) -> dict:
   '''
   By getting a list of path of images,
   this function returns a dictionary with a key of one of the path of images
   and an item of the list of mos scores of images in the path.
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
      mos_dict['images_path'] = mos_scores
   return mos_dict
   
#for loading a model for object count with appropriate checkpoint
def load_model_object_count():
   #config file
   config = {
   # model
   'model_config_path': "utils/yolov3-kitti.cfg",
   'data_config_path': "utils/kitti.data",
   'class_path': "utils/kitti.names",
   'img_size': 416,
    # checkpoint path
    "ckpt_path": "./yolov3-kitti.weights",
   }
   
   #Model Definition
   DEVICE = torch.device("cpu") 
   model = Darknet(config['model_config_path'], img_size=config['img_size'])
   
   #Load checkpoint
   model.load_weights(config['ckpt_path'])
   
   return model

#for a single image
def object_count_help(model, imgfie_path: str) -> list:
   #config file
   config = {
   # model
   'batch_size': 1,
   'iou_thres': 0.5,
   'conf_thres': 0.8,
   'nms_thres': 0.4,
   'n_cpu': 0,
   'img_size': 416,
   'use_cuda': False,
   }

   folder = ImageFolder(imgfie_path, img_size=config['img_size'])
   dataloader = DataLoader(folder,
                           batch_size=config['batch_size'], shuffle=False, num_workers=config['n_cpu'])
   
   num_objects = []
   num_objects_dict = {}
   for batch_i, (img_paths, input_imgs) in enumerate(dataloader):
      # Configure input
      input_imgs = Variable(input_imgs.type(torch.FloatTensor))

      # Get detections
      with torch.no_grad():
         detections = model(input_imgs)
         detections = non_max_suppression(detections, 80, config['conf_thres'], config['nms_thres']) #80: num_classes
         if detections[0] is None:
            num_objects_dict[img_paths] = 0
            num_objects.append(0)
         else:
            num_objects_dict[img_paths] = detections[0].shape[0]
            num_objects.append(detections[0].shape[0])
   return num_objects

#for a list of images paths
def object_count(img_path_list: list) -> dict:
   model = load_model_object_count()
   
   object_dict = {}
   for images_path in img_path_list:
      print('----Object_counting----')
      object_dict['images_path'] = object_count_help(model, images_path)
   return object_dict
   
#for showing the list of images that are duplicates and to be removed
def duplicates(img_path_list: list) -> list:
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
         paths.append(path)
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
   # print(object_count_)
   print(duplicate_)



if __name__ == '__main__':
   main()
   
'''
def iqa(iamges):
    # images : a list of image paths
    # results : dictionary {key: path, value : score}
    results = {}

    return results
'''