import pandas as pd
import os

from .utils.models.models import Darknet
from .utils.utils import *
from .utils.datasets import *
from .utils.parse_config import *

from collections import defaultdict
from functools import reduce

from torch.utils.data import DataLoader
from torch.autograd import Variable

os.environ['KMP_DUPLICATE_LIB_OK']='True'
FILE_DIR = os.path.dirname(os.path.realpath(__file__))

class GT_processing():
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
      # gt file path
      #"file_path": FILE_DIR + "/data/GT.csv",
   }
  
  def __init__(self, configs=None):
    if configs:
      self.configs = configs
    self.load_model_bounding_box()
    
  #for loading a model for bounding box processing
  def load_model_bounding_box(self):
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
      
  def load_classes(self, path):
      """
      Loads class labels at 'path'
      """
      fp = open(path, "r")
      names = fp.read().split("\n")[:-1]
      return names

  def add_null(self, df):
    bbox = ['bbox_left', 'bbox_right', 'bbox_top', 'bbox_bottom']
    for box in bbox:
      null = [None] * len(df)
      df[box] = null
  
  def save_csv(self, df, gt_path):
    file_paths = gt_path.split('/')[:-1]
    file_name = os.path.join(*file_paths) + '/' + 'GT_bbox.csv'
    df.to_csv(file_name)

  def gt_processing(self, img_path, gt_csv):
    '''
      By getting a path of image and a csv file of groud truth of images in the path,
      this function returns a new csv file with bounding box inferenced by yolov3-kitti
      
      [input]
      - img_path: a path in which the images of sample resides
      - gt_csv: a csv file with groud truth information before processing
      
      [output]
      - file_df: a new csv file with bounding box [bbox_left, bbox_right, bbox_top, bbox_bottom]
      '''
    
    # Load gt.csv file
    file_df = pd.read_csv(gt_csv)
    self.add_null(file_df)
    
    # Load classes
    classes = self.load_classes(self.configs['class_path']) # Extracts class labels from file

    # Loading data for images
    folder = ImageFolder(img_path, img_size=self.configs['img_size'])
    dataloader = DataLoader(folder,
                            batch_size=self.configs['batch_size'], shuffle=False, num_workers=self.configs['n_cpu'])

    imgs = []           # Stores image paths
    img_detections = [] # Stores detections for each image index

    for batch_i, (img_paths, input_imgs) in enumerate(dataloader): #img_paths = ('sampledata/Images/0000000000.png',)
        print("-----", batch_i)
        # Configure input
        input_imgs = Variable(input_imgs.type(torch.FloatTensor))
        file_name = img_paths[0].split('/')[-1]

        # Get detections
        with torch.no_grad():
            detections = self.model(input_imgs)
            detections = non_max_suppression(detections, 80, self.configs['conf_thres'], self.configs['nms_thres']) #80: num_classes

            # Save image and detections
            imgs.extend(img_paths)
            img_detections.extend(detections)
            
        # Mapping bbox detections with GT.csv
        for i in range(len(file_df)):
          for img_i, (path, detections) in enumerate(zip(imgs, img_detections)):
            # Bounding boxes and labels of detections
            if detections is not None:
              for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:
                  label = classes[int(cls_pred)]
                  if ((file_name == file_df.loc[i]['filename']) & (label == file_df.loc[i]['object'])):
                    file_df['bbox_left'].iloc[i], file_df['bbox_right'].iloc[i] = float(x1), float(x2)
                    file_df['bbox_top'].iloc[i], file_df['bbox_bottom'].iloc[i] = float(y1), float(y2)
                  else:
                    continue
    self.save_csv(file_df, gt_csv)
    return file_df