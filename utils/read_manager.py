from dbmanager.utils import load_list_view, load_detailed_view, load_list_view_search, get_user_point
import pandas as pd
import os
from werkzeug.utils import secure_filename
import zipfile
import sys

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
DATASET_LISTVIEW_SPEC = FILE_DIR + "/specs/dataset_listview_spec.csv"
DETAIL_LISTVIEW_SPEC = FILE_DIR + "/specs/detail_listview_column_spec.csv"

class ReadManager():
    '''
    support search pipeline (db->server)
    '''

    def __init__(self, db, db2_front_dataset_spec=None, db2_front_detail_spec=None ):
        '''
        [input]
        - db2_front_spec: db2fornt spec file path(csv), str
        '''
        self.db = db
        
        # spec match db to front (dataset listview)
        if db2_front_dataset_spec:
            df = pd.read_csv(db2_front_dataset_spec)  
            self.db2front_dataset_list = dict(zip(df["db"], df["front"]))
        else:
            df = pd.read_csv(DATASET_LISTVIEW_SPEC)
            self.db2front_dataset_list = dict(zip(df["db"], df["front"]))


        # spec match db to front (detail listview)
        if db2_front_detail_spec:
            df = pd.read_csv(db2_front_detail_spec)  
            self.db2front_detail_list = dict(zip(df["db"], df["front"]))
        else:
            df = pd.read_csv(DETAIL_LISTVIEW_SPEC)  
            self.db2front_detail_list = dict(zip(df["db"], df["front"]))
    
    def read_searched_data(self, query):
        '''
        read listview data searched following user query

        [input]
        - query: user query , dictionary (not fixed) // if None, read entire data

        [output]
        - success: bool
        - datasets: searched data (a dictionary with below keys)
            - "rows": a list of dictionary(row)
            - "max_page_num": ax page number of queried data
        '''
        datasets = {
            "rows": [],
            "max_page_num": 0
        }

        df_result = None
        success = False
        try:
            if query:
                print("query is not none")
                try:
                    datasets["max_page_num"], df_result = load_list_view_search(self.db, query)
                except Exception as e:
                    print("query search error:", e)
            else: # read all
                try:
                    print("load list view result", load_list_view(self.db))
                    datasets["max_page_num"], df_result = load_list_view(self.db)
                except Exception as e:
                    print("query default load error:", e)
            
            try:
                if df_result is not None:
                    print("df_result:", df_result)
                    datasets["rows"] = self.get_listview_form(df_result)
            except Exception as e:
                print("load front form error", e)

            success = True
        except Exception as e:
            print("read data error:", e)
        return success, datasets
    
    def get_listview_form(self, df_result):
        '''
        append detail view data for datasets in df_result(dataset list) to rows

        [input]
        - df_result: dataset listview data, pd.DataFrame

        [output]
        - rows: listview data (a list of dictionary), each element is matched to a dataset(row: contains dataset information and detail-listview-info(key:"items")
        '''
        rows = []
        cardview_data = None
        listview_data = None

        # load detail view data
        if df_result is None:
            return rows
        try:
            print('detailview error', df_result)
            cardview_data, listview_data = load_detailed_view(self.db, df_result)
        except Exception as e:
            print("db access for detailview data error,", e)
        
        # make data as front listview form
        print("get list view in df", df_result)
        df_result.rename(columns=self.db2front_dataset_list, inplace=True)
        df_result["Objects"] = df_result.apply(lambda x: f"{x.object_count} objects: {x.object_info_in_detail}", axis=1)
        df_result["UploadDate"] = df_result.apply(lambda x: x.UploadDate.strftime("%Y-%m-%d %H:%M:%S"), axis=1)
        df_result["items"] = None
        
        rows = df_result.to_dict("records")

        #add items for detailview (listview, cardview data for each datasets)
        if rows:
            try:
                for row in rows:
                    d_id = row["d_id"]
                    cv_data = cardview_data[d_id]
                    lv_data = listview_data[d_id]

                    print('lv', lv_data)
                    print('cv', cv_data)

                    # make detail_list data as front listview form
                    lv_data.rename(columns=self.db2front_detail_list, inplace=True)
                    lv_data["Objects"] = lv_data.apply(lambda x: f"{x.object_count} objects: {x.object_info_in_detail}", axis=1)
                    cv_data["Objects"] = cv_data.apply(lambda x: f"{str(x.object_info_in_detail).translate({ord('{'): None, ord('}'): None})}", axis=1)
                    row["items"] = {
                        "cardview": cv_data.to_dict("records"),
                        "listview": lv_data.to_dict("records"),
                    }
            except Exception as e:
                print("get detail view data error", e)
        return rows
    
    def transform_data(self, v):
        if '(' in v:
            return tuple(v.translate({ord('('): None, ord(')'):None}).split(','))
        else:
            return v.split(',')
    
    def extract_targetInfo(self, formData, target_keys):
        target_info = {k: self.transform_data(v) for k, v in formData.items() if k in target_keys and 'none' not in v}

        # for only this version,
        target_info = dict(filter(lambda x: not (len(x[1])==1 and x[1][0]=='null'), target_info.items()))
        
        return target_info

    def encode_formdata(self, formdata, mode="search"):
        data = {}
        if mode=="search":
            # get Basic Info
            keyword = formdata["keyword"]
            print('keyword: ', keyword)

            if keyword!="none":
                data["BASIC_INFO"]=keyword

            # get Q Info
            qc_keys_front = ["qc_state", "qc_score", "objects"]
            Q_info = self.extract_targetInfo(formdata, qc_keys_front)
            if len(Q_info)>0:
                data["QUALITY_INFO"] = Q_info
           
            
            # get S Info
            angle_keys_front = ["roll", "pitch", "yaw"]
            angular_keys_front = ["wx", "wy", "wz"]
            v_keys_front = ["vf", "vl", "vu"]
            accel_keys_front = ["ax", "ay", "az"]

            sensor_keys_front = angle_keys_front + angular_keys_front + v_keys_front + accel_keys_front
            S_info = self.extract_targetInfo(formdata, sensor_keys_front)

            if len(S_info)>0:
                data["SENSOR_INFO"] = S_info

            print("query data", data)
        else:
            pass
        return data        
    
    def read_manage_data(self, user_name):
        '''
        read manage data of user

        [input]
        - user_name: str

        [output]
        - success: bool
        - data: searched data (a dictionary with below keys)
            - "rows": a list of dictionary(row)
            - "max_page_num": ax page number of queried data
        '''
        data = {
            "cache": 0,
            "uploaded": {
                "rows":[],
                "max_page_num": 0
            },
            "transactions": {
                "rows":[],
                "max_page_num": 0
            }
        }

        df_result = None
        success = False
        
        #update cache
        data["cache"] = get_user_point(self.db, user_name)['user_point'][0]

        #update uploaded data
        try:
            data["uploaded"]["max_page_num"], df_result = load_list_view(self.db, user_idName=user_name)
            if df_result is not None:
                data["uploaded"]["rows"] = self.get_listview_form(df_result)
            success = True
        except Exception as e:
            print("read uploaded data error:", e)
        
        # TODO: update transactions
        try:
            data["transactions"]["max_page_num"], df_result = load_list_view(self.db, user_idName=user_name)
            if df_result is not None:
                data["transactions"]["rows"] = self.get_listview_form(df_result)
            success = True
        except Exception as e:
            print("read transaction data error:", e)
        return success, data 

    def set_custom_filtering(self, f):
        CUSTOM_DIR = './downloads-temporal'
        file_path = CUSTOM_DIR + secure_filename(f.filename)
        f.save(file_path)

        target_zip = zipfile.ZipFile(file_path)
        # 첫번쨰가 dir name이라 가정하겠음
        dir_name = target_zip.namelist()[0]

        zip_file = zipfile.ZipFile(file_path)
        zip_file.extractall(file_path)
        zip_file.close()

        unzip_dir="./custom-filtering/"

        extracted_dir = unzip_dir + dir_name
        filenames = os.listdir(extracted_dir)
        print("contents:", filenames)

        #압축 풀고나면 zip 파일 삭제하기
        try:
            os.remove(file_path)
        except Exception as e:
            print("zip file is not deleted", e)


        # 파일 경로
        module_path = extracted_dir + './custom.py'

        # 경로에 있는 모듈을 import
        if module_path not in sys.path:
            sys.path.append(module_path)

        # from my_module import my_function
