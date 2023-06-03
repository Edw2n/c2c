import os
import cv2
import numpy as np
import torch
import argparse
import hashlib
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from .utils.inference_process import ToTensor, Normalize
from tqdm import tqdm
from torchvision.transforms.functional import pil_to_tensor 
from torch.autograd import Variable

from .utils.models.maniqa import MANIQA
from .utils.models.models import Darknet

from .utils.utils import *
from .utils.datasets import *
from .utils.parse_config import *

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
   '''
   This function generates a model for Image Quality Assessment (IQA) 
   
   [output]
    - model: model for IQA
   '''
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
    "ckpt_path": FILE_DIR + "/ckpt_koniq10k.pt",
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

def iqa_help(model, num_crop, img: Image) -> float: 
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
         model.eval()
         patch_sample = img.get_patch(i)
         patch = patch_sample['d_img_org']
         patch = patch.unsqueeze(0)
         score = model(patch)
         avg_score += score
   mos_score = avg_score / num_crops
   return mos_score

   
#for loading a model for object count with appropriate checkpoint
def load_model_object_count():
   '''
   This function generates a model for counting number of objects in the image
   
   [output]
    - model: model for object count
   '''
   #config file
   config = {
   # model
   'model_config_path': FILE_DIR + "/utils/yolov3-kitti.cfg",
   'data_config_path': FILE_DIR + "/utils/kitti.data",
   'class_path': FILE_DIR + "/utils/kitti.names",
   'img_size': 416,
    # checkpoint path
    "ckpt_path": FILE_DIR + "/yolov3-kitti.weights",
   }
   
   #Model Definition
   DEVICE = torch.device("cpu") 
   model = Darknet(config['model_config_path'], img_size=config['img_size'])
   
   #Load checkpoint
   model.load_weights(config['ckpt_path'])
   
   return model

#for a single image
def object_count_help(model, imgfie_path: str) -> list:
   '''
   This function returns the number of objects in a single image
   
   [input]
    - model: a model for processing object count
    - img: a image that needs to be processed for object count
   
   [output]
    - num_objects: number of objects in a single image
   '''
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
            num_objects_dict[img_paths[0]] = 0
            num_objects.append(0)
         else:
            num_objects_dict[img_paths[0]] = detections[0].shape[0]
            num_objects.append(detections[0].shape[0])
   return num_objects_dict

