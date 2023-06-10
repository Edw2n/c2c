from flask import Flask, request
from pandas.io import json
from flask_cors import CORS #comment this on deployment
import pandas as pd
from werkzeug.utils import secure_filename

from dbmanager.crud import CRUD
from dbmanager.configs import POSTGRES_CONFIG
from dbmanager.utils import initialize_db_structures, identify_user, copy_db, restore_db
from utils.upload_manager import UploadManager
from utils.read_manager import ReadManager

imgfile_path_list = []
UPLOAD_ROOTDIR = "./uploads/"
app = Flask(__name__)
CORS(app)
db = None
upload_manager = None
read_manager = None
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
            print(identify_user(db, user_name, pw, case = "upload"))
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

        try:
            # qeury = get_query_info(request.form~~~~)
            # read_manager.encode_formdata(request.form, "search")
            
            #TODO: get custom file
            
            # read data from db (read all data)
            success, datasets = read_manager.read_searched_data(query)
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
        #TODO: get manage data of identified user and set success == True
        success_manage, manage_data = read_manager.read_manage_data(user_name)

    print(manage_data)
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
                    - "page_info": 페이지수 정보
                - "transactions": a list of dict
                    - "rows": a list of dict
                    - "page_info": 페이지수 정보
        - "success_transaction": main_data 읽어온 결과 성공여부 (bool),
        - "success_manage": manage_data 읽어온 결과 성공여부 (bool),
    '''

    manage_data = []
    success_transaction = False
    success_manage = False
    max_page_num_info = []

    if request.method =="POST":
        try:
            #TODO: transaction pipeline
            pass
        except Exception as e:
            print("trasaction error:", e)

    if success_transaction:
        #TODO: get manager data of identified user and set success == True
            # _, manage_data, max_page_num_info = read_manage_data(user_name)
            # success_manage == True
        pass

    result = {
        "manage_data": manage_data,
        "success_transaction": success_transaction,
        "success_manage": success_manage,
        "manage_page_info": max_page_num_info,
    }

    return json.dumps(result)

def qc1(target_image): #qc interaction
    qced_image = None
    return qced_image

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

        # run flask server
        app.run(host="0.0.0.0", port=3000)
    except Exception as e:
        print("Server Running Error!!!!!", e)
