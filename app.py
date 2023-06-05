from flask import Flask, request
from pandas.io import json
from flask_cors import CORS #comment this on deployment
import pandas as pd
from werkzeug.utils import secure_filename

from dbmanager.crud import CRUD
from dbmanager.configs import POSTGRES_CONFIG
from dbmanager.utils import initialize_db_structures, identify_user, load_list_view_default
from utils.upload_manager import UploadManager

imgfile_path_list = []
UPLOAD_ROOTDIR = "./uploads/"
app = Flask(__name__)
CORS(app)
db = None
upload_manager = None
print("service is created")

list_data_num = 10

@app.route("/upload",methods=["POST"])
def upload_data():
    print("uploaded")
    global list_data_num
    
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
    # read every data
    query = {}
    data = read_data(query)
    
    # blablabla

    result = {
        "data": data,
        "valid": valid,
        "success": success,
    }

    return json.dumps(result)

@app.route("/read",methods=["POST"])
def service_data():

    if request.method =="POST":
        print("*******     read info     ********")
        keyword = request.form["keyword"]
        # gender = request.form["Gender"]
        # breed_detail = request.form["Breed_detail"]
        # color = request.form["Color"]
        # neutering = request.form["Neutering"]
        # city = request.form["City"]

        #TODO script file 처리 추가

        print(f"keyword :{keyword}")
        # print(f"gender :{gender}")
        # print(f"breed_detail :{breed_detail}")
        # print(f"color :{color}")
        # print(f"neutering :{neutering}")
        # print(f"city :{city}")

        # read data from db (read all data)
        df_result = load_list_view_default(db)

        query = None # TODO : request information => query 
        data = read_data(query)
        # something process

    result = {
        "data": data,
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
        db, success = connect_db(initialize=True)

        # initialize helpers for service pipeline
        if success:
            upload_manager = UploadManager(db)
            print(upload_manager)

        # run flask server
        app.run(host="0.0.0.0", port=3000)
    except Exception as e:
        print("Server Running Error!!!!!", e)
