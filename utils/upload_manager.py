import zipfile
import os
from shutil import copyfile, rmtree
import glob
from PIL import Image
from datetime import datetime
from dbmanager.utils import insert_draft_dataset, update_multiple_columns

# support for qc
from qcmanager.QC_help import IQA, ObjectCounter, duplicates
class UploadManager():
  def __init__(self, db):
    self.iqa = IQA()
    self.oc = ObjectCounter()
    self.dupulicates = duplicates
    self.db = db
    
  def upload_dataset(self, f, dataset_info):

    success = False
    
    # save temporal dataset
    f.save(dataset_info["PATH"])

    # path에 있는 거 압축 풀기
    unzipped_dataset_info = self.unzip_dataset(dataset_info)

    #insert draft
    db_info = insert_draft_dataset(db=self.db,
    unzipped_dataset_info=unzipped_dataset_info)

    #store image dataset and update image paths
    success = self.update_image_paths(db_info, unzipped_dataset_info["PATH"] + "Images/")
    if success:
      # delete temporal directory
      rmtree(unzipped_dataset_info["PATH"])
    else:
      return success

    # update image info 
    success = self.update_image_info(db_info)
    
    # do qc
    if not success:
      return success
    success = self.update_qc(db_info)
    print("updated info:")
    print(db_info)

    # object count
    # db count update
    
    # filtering
    # object delte (update)

    # dupulicate filtering

    # request qc (not wait until qc finished)
    
    # qc(data)
    return success

  def unzip_dataset(self, zip_info, unzip_dir="./temporal-datasets/"):
    '''
    unzip uploaded dataset which is located in zip_info["PATH"] to unzip_dir(destination folder)

    [input]
    - zip_info: dataset information with dictionary
    - unzip_dir: destination directory which unzipped folder will be located temporal

    [output]
    - extracted_dataset_info: extracted dataset information with dictionary
    '''

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
      "DESCRIPTIONS": zip_info["DESCRIPTIONS"],
    }

    #print extraxtion info
    print(f"extracted in {extracted_dataset_info}")

    #압축 풀고나면 zip 파일 삭제하기
    os.remove(zip_path)

    return extracted_dataset_info

  def update_image_paths(self, insertion_info, source_dir, target_dir='./images/'):
    '''
    mv imgs from source_dir to target_dir , named following inserted_info and db update("image_path")

    [input]
    - stored_info: target dataset information (pd.dataframe)
    - source_dir(str)
    - target_dir(str)

    [output]
    - success(bool)
    '''
    success = False
    try:
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

      success = update_multiple_columns(self.db, stored_info, "img_path")
    except Exception as e:
      print("Image path update error", e)

    return success
  
  def update_image_info(self, stored_info):
    '''
    udpate image width and height of target dataset(stored_info) to db

    [input]
    stored_info: target dataset information (pd.dataframe)

    [output]
    success: bool
    '''
    success = False
    try:
      stored_info['image_width'] = None
      stored_info['image_height'] = None

      for ind in stored_info.index:
        image = Image.open(stored_info['image_path'][ind])
        stored_info['image_width'][ind], stored_info['image_height'][ind] = image.size
      
      success = update_multiple_columns(self.db, stored_info, "img_WH")
    except Exception as e:
      print("Update image info error", e)
    return success

  def update_qc(self, stored_info):
    success = False
    try:
      now = datetime.now()
      dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
      stored_info['qc_start_date'] = dt_string
      success = update_multiple_columns(self.db, df=stored_info, mode="start_QC")

      if not success:
        return success

      iqa_results = self.iqa.get_scores(list(stored_info['image_path']))
      print(iqa_results)
      stored_info['qc_score'] = stored_info['image_path'].map(iqa_results)
      print(stored_info)
      success = update_multiple_columns(self.db, df=stored_info, mode="QC_score")
    except Exception as e:
      print("Update QC error", e)
    return success

  def update_production_info(self, stored_info):
    return stored_info

  def read_features(self, extracted_dataset_info):
      feature_df = None
      return feature_df