import zipfile
import os
from shutil import copyfile
import glob
from PIL import Image

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