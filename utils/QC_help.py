
import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from utils.models.maniqa import MANIQA
from config import Config
from utils.inference_process import ToTensor, Normalize
from tqdm import tqdm
from torchvision.transforms.functional import pil_to_tensor 
from typing import List


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
'''
#Amend: put a separate function for iqa of a single image and iqa for a list of images
def iqa(imgfile_path_list: List) -> List: 
   #config file
   config = Config({
    # image path
    "image_path": imgfile_path_list,

    # valid times
    "num_crops": 20,

    # model
    "patch_size": 8,
    "img_size": 224,
    "embed_dim": 768,
    "dim_mlp": 768,
    "num_heads": [4, 4],
    "window_size": 4,
    "depths": [2, 2],
    "num_outputs": 1,
    "num_tab": 2,
    "scale": 0.8,

    # checkpoint path
    "ckpt_path": "utilis/ckpt_koniq10k.pt",
   })
   
   #Model Definition
   DEVICE = torch.device("cpu") 
   model = MANIQA(embed_dim=config.embed_dim, num_outputs=config.num_outputs, dim_mlp=config.dim_mlp,
        patch_size=config.patch_size, img_size=config.img_size, window_size=config.window_size,
        depths=config.depths, num_heads=config.num_heads, num_tab=config.num_tab, scale=config.scale)
   
   ckpt = torch.load(config.ckpt_path, map_location=torch.device("cpu"))
   model.load_state_dict(ckpt, strict=False)

   mos_scores = []
   
   for img in os.listdir(config.image_path):
      img_path = config.image_path + img
      # data load
      Img = Image(image_path=config.image_path,
         transform=transforms.Compose([Normalize(0.5, 0.5), ToTensor()]),
         num_crops=config.num_crops)

      avg_score = 0
      for i in tqdm(range(config.num_crops)):
         with torch.no_grad():
            model.eval()
            patch_sample = Img.get_patch(i)
            patch = patch_sample['d_img_org']
            patch = patch.unsqueeze(0)
            score = model(patch)
            avg_score += score
      mos_scores.append(avg_score / config.num_crops)
      
   return mos_scores



#for a single path of image
def iqa_help(img_path: str) -> List: 
   
   #Model Definition
   DEVICE = torch.device("cpu") 
   model = MANIQA(embed_dim=config.embed_dim, num_outputs=config.num_outputs, dim_mlp=config.dim_mlp,
        patch_size=config.patch_size, img_size=config.img_size, window_size=config.window_size,
        depths=config.depths, num_heads=config.num_heads, num_tab=config.num_tab, scale=config.scale)
   
   ckpt = torch.load(config.ckpt_path, map_location=torch.device("cpu"))
   model.load_state_dict(ckpt, strict=False)

   mos_scores = []
   
   for img in os.listdir(config.image_path):
      img_path = config.image_path + img
      # data load
      Img = Image(image_path=config.image_path,
         transform=transforms.Compose([Normalize(0.5, 0.5), ToTensor()]),
         num_crops=config.num_crops)

      avg_score = 0
      for i in tqdm(range(config.num_crops)):
         with torch.no_grad():
            model.eval()
            patch_sample = Img.get_patch(i)
            patch = patch_sample['d_img_org']
            patch = patch.unsqueeze(0)
            score = model(patch)
            avg_score += score
      mos_scores.append(avg_score / config.num_crops)
      
   return mos_scores

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
   mos_score = avg_score / config.num_crops
   return mos_score


def object_detection(imgfie_path_list: List):
    return None
    '''