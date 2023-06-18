from flask import Flask, request, send_file
from pandas.io import json
from flask_cors import CORS #comment this on deployment
import pandas as pd
from werkzeug.utils import secure_filename

from dbmanager.crud import CRUD
from dbmanager.configs import POSTGRES_CONFIG
from dbmanager.utils import initialize_db_structures, identify_user, copy_db, restore_db, create_download_file, _create_download_file, update_tx_availability, delete_dataset
from utils.transaction_manager import TXManager
from utils.upload_manager import UploadManager
from utils.read_manager import ReadManager

import os
from shutil import copyfile
import zipfile
import glob
import shutil

import sys

imgfile_path_list = []
UPLOAD_ROOTDIR = "./uploads/"
app = Flask(__name__)
CORS(app)
db = None
upload_manager = None
read_manager = None
tx_manager = None
print("service is created")

list_data_num = 10

@app.route("/upload",methods=["POST"])
def upload_data():
    
    print("uploaded")
    global list_data_num
    datasets = None
    
    if request.method =="POST":

        valid = False
        success = False

        try:
            f = request.files["file"]
            file_path = UPLOAD_ROOTDIR + secure_filename(f.filename)
            user_name = request.form["user_name"]
            pw = request.form["pw"]
            title = request.form["title"]
            description = request.form["description"]

            print("descriptions")
            try:
                identify_user(db, user_name, pw, case = "upload")
            except Exception as e:
                print("identify error", e)

            # user validation check (+ create user info)
            if identify_user(db, user_name, pw, case = "upload"):
                
                valid = True
                print("valid")

                target_temp_dataset_info = {
                    "PATH": file_path,
                    "USER_NAME": user_name,
                    "PW": pw,
                    "TITLE": title,
                    "DESCRIPTIONS": description,
                }

                print("f:", f) 

                if upload_manager.upload_dataset(f, target_temp_dataset_info):
                    success = True
                else:
                    #TODO: upload_dataset에서 디비에 추가했던 내용들 다 rollback해서 취소해야함.
                    pass
                    

            print("*******     upload info     ********")
            print(f"file path :{file_path}")
            print(f"user name :{user_name}")
            print(f"pw :{pw}")
            print(f"title :{title}")
            print(f"description :{description}")

            # file name 한글 들어가면 현재 처리 안됨.
            list_data_num = len(f.filename)
        except Exception as e:
            print("read formdata error", e)
    
    # read entire data
    query = None
    try:
        _, datasets = read_manager.read_searched_data(query)

        # for debugging
        '''
        print('after upload, max num pages:', datasets["max_page_num"])
        print('after upload, data:', datasets["rows"])
        print('after upload, success:', success)
        '''
    except Exception as e:
        print("read data error in upload pipeline:", e)

    result = {
        "datasets": datasets,
        "valid": valid,
        "success": success,
    }

    return json.dumps(result)

@app.route("/read",methods=["POST"])
def service_data():
    datasets = None
    query = None
    success = False
    if request.method =="POST":
        print("*******     read info     ********")
        cf = None
        try:
            #TODO: get custom file
            
            # read data from db (read all data)
            if "keyword" in request.form.keys(): # if query is not None
                # custom file save
                query = read_manager.encode_formdata(request.form, "search")
                cf = read_manager.read_custom_filter(request)
            success, datasets = read_manager.read_searched_data(query, custom_filtering=cf)

            # for debugging
            '''
            print('after upload, max num pages:', datasets["max_page_num"])
            print('after upload, data:', datasets["rows"])
            print('after upload, success:', success)
            '''
        except Exception as e:
            print("read data service error:", e)

    result = {
        "datasets": datasets,
        "success": success,
    }

    return json.dumps(result)

@app.route("/login",methods=["POST"])
def check_user():
    '''
    [request.form 에 받을 데이터(key)]
        - "user_name", "pw"

    returns: jsonified dictionary with below items
        - "main_data": list/search view에 뿌릴 리스트 데이터 (홈페이지 처음 받으면 받던 데이터), list of dict
        - "manage_data": user identify 성공시 각 list 뷰에 뿌릴 manage_data, 실패시 빈 list (will be updated)
        - "valid": user identification 결과 (bool),
        - "success_main": main_data 읽어온 결과 성공여부 (bool),
        - "success_manage": manage_data 읽어온 결과 성공여부 (bool),
    '''

    main_data = []
    manage_data = []
    query = None
    valid = False
    success_main = False
    success_manage = False

    if request.method =="POST":
        try:
            user_name = request.form["user_name"]
            pw = request.form["pw"]
            print(user_name, pw)
            if identify_user(db, user_name, pw, case = "login"):
                valid = True
        except Exception as e:
            print("user check error:", e)

    # read entire data
    query = None
    try:
        success_main, main_data = read_manager.read_searched_data(query)
    except Exception as e:
        print("read data error after check user pipeline:", e)

    if valid:
        success_manage, manage_data = read_manager.read_manage_data(user_name)

    result = {
        "main_data": main_data,
        "manage_data": manage_data,
        "valid": valid,
        "success_main": success_main,
        "success_manage": success_manage,
    }

    return json.dumps(result)

@app.route("/buy",methods=["POST"])
def buy_items():
    '''
    [request.form 에 받을 데이터(key:value)] // can be updated
        - "user_name": string
        - "items": a list of img_id(int) of each item
        - "dataset-name": user defined name of dataset bought , string
        

    returns: jsonified dictionary with below items
        - "manage_data": user identify 성공시 각 list 뷰에 뿌릴 manage_data, 실패시 빈 list (will be updated)
            - keys()
                - "cash": 잔여 포인트 (int)
                - "uploaded": 
                    - "rows": a list of dict
                    - "max_page_num": 페이지수 정보
                - "transactions": a list of dict
                    - "rows": a list of dict
                    - "max_page_num": 페이지수 정보
        - "success_transaction": main_data 읽어온 결과 성공여부 (bool),
        - "success_manage": manage_data 읽어온 결과 성공여부 (bool),
    '''

    manage_data = []
    success_transaction = False
    success_manage = False
    max_page_num_info = []

    if request.method =="POST":
        try:
            user_name = request.form["user_name"]
            img_ids = request.form["items"].split(',')
            dataset_name = request.form["dataset-name"]

            transaction_info= {
                "user_name": user_name,
                "img_ids": img_ids,
                "dataset_name": dataset_name
            }
            
            success_transaction = tx_manager.update_transaction(transaction_info)
        except Exception as e:
            print("trasaction error:", e)

    if success_transaction:
        #TODO: get updated manage data user after transaction
        success_manage, manage_data = read_manager.read_manage_data(user_name)

    result = {
        "manage_data": manage_data,
        "success_transaction": success_transaction,
        "success_manage": success_manage,
        "manage_page_info": max_page_num_info,
    }

    return json.dumps(result)

@app.route("/download",methods=["POST"])
def download_dataset():
    '''
    :download dataset()
    [request.form 에 받을 데이터(key:value)] // can be updated
    - "txp_id": 다운 받을 데이터셋의 txp_id
        
    returns:
    - send_file : down load link of dataset
    '''

    if request.method =="POST":
        try:
            txp_id = request.form["txp_id"]
            is_test_mode = request.form["test_mode"]
            try:
                if is_test_mode == "true":
                    print("test mode")
                    img_ids = [1,2,3,4,5]
                    features, gt, img_paths = _create_download_file(db, img_ids)
                    dataset_name = "mine"
                else: 
                    features, gt, img_paths, dataset_name = create_download_file(db, txp_id)

                # dataset 생성
                dataset_dir = f"./downloads-temporal/{dataset_name}" # 압축할 폴더 경로
                imageset_dir = dataset_dir+"/images"
                os.makedirs(dataset_dir, exist_ok=True)
                os.makedirs(imageset_dir, exist_ok=True)
                features.to_csv(dataset_dir+"/features.csv")
                gt.to_csv(dataset_dir+"/gt.csv")
                for src in img_paths:
                    file_name = src.split("images")[-1]
                    dst = imageset_dir + file_name
                    print(dst)
                    copyfile(src, dst)
            
                # 압축 파일 저장 경로
                if not os.path.exists("./available/"):
                    os.makedirs("./available/")
                zip_filename = f"./available/{dataset_name}.zip"

                # 폴더를 압축
                zipf = zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED)
                for root, dirs, files in os.walk(dataset_dir):
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        zipf.write(dir_path, arcname=os.path.relpath(dir_path, dataset_dir))
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, arcname=os.path.relpath(file_path, dataset_dir))
                zipf.close()

                update_tx_availability(db, txp_id, True, zip_filename)

            except Exception as e:
                print("download dataset error,", e)
        except Exception as e:
            print("read formdata in download pipeline,", e)

    # 다운로드 링크 제공
    return send_file(zip_filename, mimetype="zip",  as_attachment=True)

@app.route("/delete",methods=["POST"])
def delete_uploaded_dataset():
    '''
    delete dataset in uploaded dataset / transaction dataset?

    [input]
    - user_name, dataset_id

    returns: jsonified dictionary with below items
        - "main_data": list/search view에 뿌릴 리스트 데이터 (홈페이지 처음 받으면 받던 데이터), list of dict
        - "manage_data": user identify 성공시 각 list 뷰에 뿌릴 manage_data, 실패시 빈 list (will be updated)
        - "success_main": main_data 읽어온 결과 성공여부 (bool),
        - "success_manage": manage_data 읽어온 결과 성공여부 (bool),
    '''
    success = False

    if request.method =="POST":
        try:
            d_id = request.form["d_id"]
            user_name = request.form["user_name"]
            print(d_id)

            success = delete_dataset(db, d_id)
        except Exception as e:
            print("delete datasest error, ", e)
    result = {
        "success": success,
    }

    return json.dumps(result)


@app.route("/feedback",methods=["POST"])
def feedback_qc():
    '''
    feedback qc score from user (front alert: 피드백 감사합니다!)

    [input]
    - qc_feedback
    - txp_id
    - user_id

    returns: jsonified dictionary with below items
        - success:
    '''
    result = {
        "success": True
    }
    return json.dumps(result)

@app.route('/image/<path:image_path>')
def get_image(image_path):
    print(image_path)
    with open(image_path, 'rb') as f:
        return send_file(f, mimetype='image/png')

def connect_db(initialize=False, copy=False, restore=False):
    '''
    db connection + db object 생성, db structure initailization

    [output]
    - db object
    - success (bool)
    '''

    success = False

    # set postgresql connection configurations
    app.config["C2C_USER"] = POSTGRES_CONFIG["C2C_USER"]
    app.config["C2C_PASSWORD"] = POSTGRES_CONFIG["C2C_PASSWORD"]
    app.config["C2C_HOST"] = POSTGRES_CONFIG["C2C_HOST"]
    app.config["C2C_PORT"] = POSTGRES_CONFIG["C2C_PORT"]
    app.config["C2C_DB"] = POSTGRES_CONFIG["C2C_DB"]

    # connect postgresql
    db = CRUD(app.config)
    print("Postgress is connected")

    if copy:
        copy_db(db)

    # if needed, init db
    if restore:
        restore_db(db)
        success = True
    elif initialize:
        if(initialize_db_structures(db)):
            success = True
            print("DB Structure is initailized")
        else:
            success = False
            print("DB Structure initialization is Failed")
    else:
        success = True

    return db, success

if __name__ == "__main__":
    
    try:
        # connect db (연결, 필요시 db 초기 structure 구성)
        db, success = connect_db(copy=False, restore=False, initialize=False)

        # initialize helpers for service pipeline
        if success:
            upload_manager = UploadManager(db)
            read_manager = ReadManager(db)
            tx_manager = TXManager(db)

        # run flask server
        app.run(host="0.0.0.0", port=3000)
    except Exception as e:
        print("Server Running Error!!!!!", e)
