
import os
import cv2
import numpy as np
import torch
import argparse
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from utils.models.maniqa import MANIQA
from config import Config
from utils.inference_process import ToTensor, Normalize
from tqdm import tqdm
from torchvision.transforms.functional import pil_to_tensor 
from typing import List

from QC_help import Image

#for a single image
def iqa(model, img: Image, num_crops) -> int: 
   avg_score = 0
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


def object_detection(imgfie_path_list: List):
    return None
 

def main():
   parser = argparse.ArgumentParser(
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument('-p', '--path',
                        help='File path of images to QC')
   parser.add_argument('-o', '--output', 
                        help='File path for the result of MOS')
   parser.add_argument('-c', '--checkpoint', 
                        help='Checkpoint of the model')
   args = parser.parse_args()
   
   #config file
   config = {
    # image path
    'image_path': [args.path], #['./data/'],

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

   # Multiple paths
   mos_scores = []
   mos_dict = {}
   for images_path in config['image_path']:
      for img in os.listdir(images_path):
         img_path = images_path + img
         # data load
         Img = Image(image_path=img_path,
            transform=transforms.Compose([Normalize(0.5, 0.5), ToTensor()]),
            num_crops=config['num_crops'])
         print('----IQA----')
         mos = iqa(model, Img, config['num_crops'])
         mos_scores.append(mos)
      mos_dict['images_path'] = mos_scores
   print(mos_dict)



if __name__ == '__main__':
   main()