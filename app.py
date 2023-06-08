from flask import Flask, request
from pandas.io import json
from flask_cors import CORS #comment this on deployment
import pandas as pd
from werkzeug.utils import secure_filename

from dbmanager.crud import CRUD
from dbmanager.configs import POSTGRES_CONFIG
from dbmanager.utils import initialize_db_structures, identify_user
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
    data = []
    
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
        
            # user validation check (+ create user info)
            if identify_user(db, user_name, pw, case = "upload"):
                valid = True

                target_temp_dataset_info = {
                    "PATH": file_path,
                    "USER_NAME": user_name,
                    "PW": pw,
                    "TITLE": title,
                    "DESCRIPTIONS": description,
                } 

                if upload_manager.upload_dataset(f, target_temp_dataset_info):
                    success = True

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
        _, data, max_page_num = read_manager.read_searched_data(query)
        print('after upload, data:', data)
        print('after upload, success:', success)
    except Exception as e:
        print("read data error in upload pipeline:", e)

    result = {
        "data": data,
        "valid": valid,
        "success": success,
        "max_page_num": max_page_num,
    }

    return json.dumps(result)

@app.route("/read",methods=["POST"])
def service_data():
    data = []
    query = None
    success = False
    if request.method =="POST":
        print("*******     read info     ********")

        try:
            # qeury = get_query_info(request.form~~~~)
            # read_manager.encode_formdata(request.form, "search")
            
            #TODO: get custom file
            
            # read data from db (read all data)
            
            success, data, max_page_num = read_manager.read_searched_data(query)
            # print('after read, data:', data)
            # print('after read, success:', success)
        except Exception as e:
            print("read data service error:", e)

    result = {
        "data": data,
        "success": success,
        "max_page_num": max_page_num,
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
        - "main_max_page_num": main_data 페이지수 (int) (will be updated),
        - "manage_page_info": manage_data 페이지수 정보, (will be updated)
    '''

    main_data = []
    manage_data = []
    query = None
    valid = False
    success_main = False
    success_manage = False
    max_page_num_main = 0
    max_page_num_info = []

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
        _, main_data, max_page_num_main = read_manager.read_searched_data(query)
        success_main = True
    except Exception as e:
        print("read data error after check user pipeline:", e)

    if valid:
        #TODO: get manager data of identified user and set success == True
            # _, manage_data, max_page_num_info = read_manage_data(user_name)
            # success == True
        pass

    result = {
        "main_data": main_data,
        "manage_data": manage_data,
        "valid": valid,
        "success_main": success_main,
        "success_manage": success_manage,
        "main_max_page_num": max_page_num_main,
        "manage_page_info": max_page_num_info,
    }

    return json.dumps(result)


def read_data(query): #db interaction
    queried_data = list(range(list_data_num))
    return queried_data

def qc1(target_image): #qc interaction
    qced_image = None
    return qced_image

def connect_db(initialize=False):
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

    # if needed, init db
    if initialize:
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
        db, success = connect_db(initialize=False)

        # initialize helpers for service pipeline
        if success:
            upload_manager = UploadManager(db)
            read_manager = ReadManager(db)

        # run flask server
        app.run(host="0.0.0.0", port=3000)
    except Exception as e:
        print("Server Running Error!!!!!", e)
