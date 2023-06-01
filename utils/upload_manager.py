import zipfile
import os
from shutil import copyfile
import glob
from PIL import Image

from dbmanager.utils import insert_draft_dataset

def upload_dataset(db, f, dataset_info):

  success = False
  
  # save temporal dataset
  f.save(dataset_info["PATH"])

  # path에 있는 거 압축 풀기
  unzipped_dataset_info = unzip_dataset(dataset_info)
  print(unzipped_dataset_info)

  #insert draft
  inserted_info = insert_draft_dataset(db=db,
   unzipped_dataset_info=unzipped_dataset_info)
  print(inserted_info)

  #store dataet
  stored_info = store_images(inserted_info, unzipped_dataset_info["PATH"] + "Images/")
  print('stored info', stored_info)
  success = True

  #insert file path update

  #do qc

  # request qc (not wait until qc finished)
  
  # qc(data)
  return success

def unzip_dataset(zip_info, unzip_dir="./temporal-datasets/"):

  zip_path = zip_info["PATH"]
  
  target_zip = zipfile.ZipFile(zip_path)
  # 첫번쨰가 dir name이라 가정하겠음
  dir_name = target_zip.namelist()[0]
  zipfile.ZipFile(zip_path).extractall(unzip_dir)
  extracted_dir = unzip_dir + dir_name
  filenames = os.listdir(extracted_dir)
  print("contents:", filenames)

  extracted_dataset_info = {
    "PATH": extracted_dir,
    "USER_NAME": zip_info["USER_NAME"],
    "PW": zip_info["PW"],
    "TITLE": zip_info["TITLE"],
  }

  #print extraxtion info
  print(f"extracted in {extracted_dataset_info}")

  #압축 풀고나면 zip 파일 삭제하기
  os.remove(zip_path)

  return extracted_dataset_info

def store_images(insertion_info, source_dir, target_dir='./images/'):
  '''
  mv imgs from source_dir to target_dir , named following inserted_info

  [input]
  - inserted_info
  - source_dir
  - target_dir

  [output]
  - stroed_info
  '''

  stored_info = insertion_info
  stored_info["image_path"] = None
 
  source_file_nums = len(glob.glob(f"{source_dir}/*.png"))

  assert source_file_nums == len(insertion_info), "Number of stored images is not matched to source_dir"

  for ind in stored_info.index:
    src = source_dir + stored_info['filename'][ind]
    dst = target_dir + str(stored_info['img_id'][ind]) + ".png"
    copyfile(src, dst)
    print(f"copy {src} to {dst}")
    stored_info['image_path'][ind] = dst

  return stored_info
