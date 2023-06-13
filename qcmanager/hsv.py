import pandas as pd
from dbmanager.configs import SCHEMA_NAME, ALL_COLUMNS
from dbmanager.utils import find_img_id_with_dataset_id
import cv2
import os
import numpy as np


def hsv(db, dataset_id_list):
  '''
  calculate the hsv

  [input]
  - target db object (CRUD)
  - df: pd.DataFrame - ['img_id', 'image_path', 'image_width', 'image_height',
                        'qc_id', 'qc_start_date', 'qc_score', 'object_count', 'qc_end_date', 'product_id', 'price']
  
  [output]
  - result = ('average_hue', 'average_saturation', 'average_value')
  '''

  schema_name = SCHEMA_NAME
  img_dataset_df = find_img_id_with_dataset_id(db, dataset_id_list)
  img_id_list = list(img_dataset_df['img_id'])


  col_ft = ALL_COLUMNS[5]
  sql_ft = f"select * from {schema_name}.features f where f.img_id in {tuple(img_id_list)};"
  res_ft = db.execute(sql_ft)
  df_ft = pd.DataFrame(data=res_ft, columns=col_ft)    
  df_tmp3 = df_ft[['image_path', 'img_id']]

  col_gt = [*ALL_COLUMNS[0], *ALL_COLUMNS[2], *ALL_COLUMNS[7]]
  sql_gt = f"select * from {schema_name}.GroundTruth g \
              left join {schema_name}.QC q on q.qc_id = g.img_id \
              left join {schema_name}.object o on o.gt_object_id = g.gt_object_id \
              where g.img_id in {tuple(img_id_list)};"
  res_gt = db.execute(sql_gt)
  df_gt = pd.DataFrame(data=res_gt, columns=col_gt)

  df_gt = pd.merge(df_gt, df_tmp3, how='left', on='img_id')
  
  target_col_gt = ['image_path', 'gt_object', 'gt_height', 'gt_width', 'gt_length',
      'gt_Xordinate', 'gt_Yordinate', 'gt_Zordinate', 'gt_Xrotate',
      'gt_Yrotate', 'gt_Zrotate', 'gt_state', 'gt_occlusion',
      'gt_occlusion_kf', 'gt_truncation', 'gt_amt_occlusion',
      'gt_amt_occlusion_kf', 'gt_amt_border_l', 'gt_amt_border_r',
      'gt_amt_border_kf', 'qc_score', 'object_count', 
      'bbox_left', 'bbox_right', 'bbox_top','bbox_bottom']

  df_gt = df_gt[target_col_gt]
  img_path_list = list(df_gt['image_path'])

  file = _hsv(ground_truth=df_gt, padding = 10)
  return file


def _hsv(ground_truth: pd.DataFrame, padding: int):
  '''
  Return the average of hsv of the image.
  
  [Input]
  - ground_truth: pd.DataFrame, generated from DB's groundtruth
  - padding: edge of the images to pad

  [Output]
  - file: a updated dataframe with average hsv values appended
  '''

  file = ground_truth
  
  # Set files_path
  
  hue = []
  saturation = []
  value = []
  for i in range(len(file)):
    img_path= str(file['image_path'][i])
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