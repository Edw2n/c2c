import pandas as pd
import cv2
import os
import numpy as np

def hsv(img_path_list: str, ground_truth: str, padding: int)->None:
  '''
  Return the average of hsv of the image.
  
  [Input]
  - img_path_list: a list of paths(or dirs) that contains user's images
  - ground_truth: a csv file of grouth truth of images in the img_path_list
  - padding: edge of the images to pad

  [Output]
  - file: a updated dataframe with average hsv values appended
  '''
  # Read csv file to append average hsv
  file = pd.read_csv(ground_truth)
  
  # Set files_path
  image_file_list = os.listdir(img_path_list)
  
  hue = []
  saturation = []
  value = []
  for i in range(len(file)):
    file_path = str(file['filename'][i])
    img_path = img_path_list + '/' + file_path
    img = cv2.imread(img_path, cv2.IMREAD_COLOR) 
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    left, right, top, bottom = int(file['bbox_left'][i]+padding), int(file['bbox_right'][i]-padding), int(file['bbox_top'][i]+padding), int(file['bbox_bottom'][i]-padding)
    area = hsv[top:bottom, left:right]
    hsv_list = np.mean(area, axis=(0, 1)).tolist()
    hue.append(hsv_list[0])
    saturation.append(hsv_list[1])
    value.append(hsv_list[2])

  file['average_hue'] = hue
  file['average_saturation'] = saturation
  file['average_value'] = value
  return file