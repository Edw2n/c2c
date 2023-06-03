from dbmanager.crud import CRUD
from dbmanager.configs import SCHEMA_NAME, TABLE_NAME, POSTGRES_CONFIG, ALL_COLUMNS_INFO, PK_LIST, FK_LIST, ALL_COLUMNS
import pandas as pd
from datetime import datetime
from pytz import timezone
# for Austin

def initialize_db_structures(db):
    '''
    DB 초기화한 이후, 
    DB 초기 구조 잡는 함수 (table 생성, key 지정 등)

    [input]
    - db : target db object (CRUD)

    [output]
    - success : initalize 성공여부
    '''
    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME
    all_columns_info = ALL_COLUMNS_INFO
    pk_list = PK_LIST
    fk_list = FK_LIST
    num_table = len(table_name)

    success = False

    for i in range(num_table):
        success = db.drop_table(schema_name, table_name[i])
        success = db.create_table(schema_name, table_name[i], all_columns_info[i])
        # success = db.addPK(schema_name, table_name[i], pk_list[i])

    for i in range(len(fk_list)):
        success = db.addFK(schema = schema_name,
                           table_PK=fk_list[i][0], 
                           column_PK=fk_list[i][1],
                           table_FK=fk_list[i][2],
                           column_FK=fk_list[i][3]
                           )
    #지금은 스키마만 있는상태에서 만드는건데, 아예 스키마 존재하면 삭제하고 스키마 생성후 주루룩 하는거도 괜찮아 보임
    # 0. Object
    print('----Object table')
    objects= ['Car', 'Van', 'Truck', 'Pedestrian', 'Person (sitting)', 'Cyclist', 'Tram', 'Misc']

    for i in range(len(objects)):
        db.insertDB(schema=schema_name, 
                    table=table_name[7],
                    columns = ['gt_object'],
                    data = [objects[i]]
                    )
        
    return success


####################################################
########## USER IDENTIFICATION FUNCTIONS ###########
####################################################
def identify_user(db, user_idname, user_password, case = "upload"):
    '''
    check user's info and return its validity 

    [Inputs]
    - db            : target db object (CRUD)
    - user_id       : string, user's id
    - user_password : string, user's passward 
    - case          : string, scenario flag
        > "upload"  : when uploading dataset
        > "login"   : when a user just does login

    [output]
    - valid: boolean based on scenario 

    '''
    if case == "upload":
        valid = _identify_user_upload_scenario(db, user_idname, user_password)
    elif case == "login":
        valid = _identify_user_login_scenario(db, user_idname, user_password)
    else:
        print("  identification error occurred")

    return valid

def _identify_user_login_scenario (db, user_idname, user_password):
    '''
    check user's info and return its validity for login scenario

    [Inputs]
    - db: target db object (CRUD)
    - user_id: user's id, from server
    - user_password: user's passward, from server 

    [output]
    - valid: 
        > True  : boolean | id and pw is valid
        > False : boolean | 1) id is existing but pw is not valid
                            2) id is not existing in DB
    '''
    # 1. Setting initial value
    valid = False

    # 2. Search by user_idname
    ##### assuming user_idname is unique

    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME[3]
    column_name = ALL_COLUMNS[3]
    condition = f"user_idName='{user_idname}'"

    result = db.readDB_with_filtering(schema = schema_name, table = table_name, columns = column_name, condition = condition)
    ##### result = [(user_id, user_idName, user_password)]

    # 3. valid: find only True case, which is id and pw is valid
    if len(result[0])>0 and result[0][2]==user_password: # result is not empty and user_password is valid
        valid=True

    return valid

def _identify_user_upload_scenario (db, user_idname, user_password, case="upload"):
    '''
    insert user info into User table in DB for upload scenario

    [Inputs]
    - db: target db object (CRUD)
    - user_id: user's id, from server
    - user_password: user's passward, from server 

    [output]
    - valid: 
        > True  : boolean | 1) id and pw is valid
                            2) id is not existing in DB -> insert user in User Table
        > False : boolean | id is existing but pw is not valid
    '''

    # 1. Setting initial value
    valid = False

    # 2. Search by user_idname
    ##### assuming user_idname is unique

    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME[3]
    column_name = ALL_COLUMNS[3]
    condition = f"user_idName='{user_idname}'"

    result = db.readDB_with_filtering(schema = schema_name,
                                      table = table_name,
                                      columns = column_name,
                                      condition = condition
                                      )
    ##### result = [(user_id, user_idName, user_password)]

    # 3. valid:
    # 3-1. "Not existing": id is not existing (result is empty list)
    if not result:
        valid = insert_user(db, user_idname, user_password) # True
    # 3-2. True:  id and pw is right (result is not empty list)
    elif result[0][2]==user_password:
        valid=True

    return valid

######################################################################################################


def insert_user_unzipped(db, unzipped_dataset_info): ## LEGACY
    '''
    insert user info into User table in DB

    [Inputs]
    - db: target db object (CRUD)
    - unzipped_dataset_info: user가 업로드한 zip file을 풀어놓은 rootdir와 관련 정보, dictionary {"PATH", "USER_NAME", "PW", "TITLE"}

    [output]
    - success: checking "insert" is done or not 
    - user_info_after_insert: returns [user_id, user_idName, user_password]
    '''
    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME[3]
    column_name = ALL_COLUMNS[3][1:]
    user_info = [unzipped_dataset_info["USER_NAME"], unzipped_dataset_info["PW"]]

    success = False
    success = db.insertDB(schema = schema_name, table = table_name,columns = column_name,data = user_info)
    user_info_after_insert = check_user(db, unzipped_dataset_info)

    return success, user_info_after_insert

def insert_user(db, user_idname, user_password):
    '''
    insert user info into User table in DB

    [Inputs]
    - db            : target db object (CRUD)
    - user_idname   : user's id to insert  
    - user_password : user's id to insert

    [output]
    - success: checking "insert" is done or not 
    '''

    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME[3]
    column_name = ALL_COLUMNS[3][1:]
    user_info = [user_idname, user_password]

    success = False
    success = db.insertDB(schema = schema_name, table = table_name,columns = column_name,data = user_info)

    return success

def check_user(db, unzipped_dataset_info):
    '''
    Check whether the user is already registered in DB or not
    with user_name only

    [inputs]
    - target db object (CRUD)
    - unzipped_dataset_info: user가 업로드한 zip file을 풀어놓은 rootdir와 관련 정보, dictionary {"PATH", "USER_NAME", "PW", "TITLE"}
    
    [output]
    - result: if user is new, then output is True, 
              else returns [(user_id, user_idName, user_password)]
    '''
    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME[3]
    column_name = ALL_COLUMNS[3]
    user_idname = unzipped_dataset_info["USER_NAME"]
    condition = f"user_idName='{user_idname}' "

    result = True

    result = db.readDB_with_filtering(schema = schema_name,
                                      table = table_name,
                                      columns = column_name,
                                      condition = condition
                                      )
    if not result:
        result = True
    print(result)
    return result

def insert_draft_dataset(db, unzipped_dataset_info):
    '''
    insert draft of user upload dataset 

    [inputs]
    - target db object (CRUD)
    - unzipped_dataset_info: user가 업로드한 zip file을 풀어놓은 rootdir와 관련 정보, dictionary {"PATH", "USER_NAME", "PW", "TITLE", "DESCRIPTIONS"}
    
    [output]
    - inserted_info: insertion information of upload dataset, pd.DataFrame 
        cols: 'img_id', 'qc_id', 'product_id', 'user_id', 'dataset_id', 'filename'
    '''
    
    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME
    column_list = ALL_COLUMNS

    last_img_id = db.find_last_img_id(schema_name)
    upload_time = datetime.now(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')

    # 1. User
    ## checking whether the user is new, if new -> insert into User table
    print('-----user------')
    user_info = check_user(db=db, unzipped_dataset_info=unzipped_dataset_info)
    user_info = user_info[0]
    user_id = user_info[0]
    # print(user_info)
    # print(user_id)
    print()

    # 2. DatasetInfo
    print('-----dataset------')
    dataset_name = unzipped_dataset_info["TITLE"]
    dataset_description = unzipped_dataset_info["DESCRIPTIONS"]
    db.insertDB(schema=schema_name, 
                table=table_name[4],
                columns = column_list[4][1:],
                data = [dataset_name, dataset_description, 0]
                )
    dataset_res = db.readDB_with_filtering(schema=schema_name, 
                                           table=table_name[4],
                                           columns = column_list[4],
                                           condition = f"dataset_name='{dataset_name}' AND dataset_description='{dataset_description}'"
                                           )

    dataset_id = dataset_res[0][0]
    # print(dataset_res)
    # print(dataset_res[0][0])
    print()


    # 3. read Feature.csv
    features = unzipped_dataset_info["PATH"] + 'Features.csv'
    df_features = pd.read_csv(features)
    num_row = len(df_features)

    # 4. ProductInfo
    print('----ProductInfo----')
    for i in range(num_row):
        db.insertDB(schema=schema_name, 
                    table=table_name[1],
                    columns = ['sold_count'],
                    data = [0]
                    )
    pi_res = db.readDB(schema=schema_name, table=table_name[1], columns=column_list[1])
    #pi_id = [i[0] + last_img_id for i in pi_res]
    pi_id = [i + 1 + last_img_id for i in range(num_row)]
  
    print()

    # 5. QC
    print('----QC-----')
    # df_qc = pd.DataFrame(columns=ALL_COLUMNS[2][1:])
    # df_qc['qc_status'] = ["uploaded" for _ in range(num_row)]
    # df_qc['qc_start_date'] = ["1993-08-27 00:00:01" for _ in range(num_row)] ##### need to fix
    # df_qc['qc_end_date'] = ["1993-08-27 00:00:01" for _ in range(num_row)] ##### need to fix
    # df_qc['qc_score'] = [0 for _ in range(num_row)] ##### need to fix
    # df_qc['object_type'] = ['' for _ in range(num_row)]
    # df_qc['object_count'] = [0 for _ in range(num_row)]
    # df_qc['tag'] = ['' for _ in range(num_row)]

    for i in range(num_row):
        # data = list(df_qc.iloc[i])
        db.insertDB(schema=schema_name, 
                    table=table_name[2],
                    columns=['qc_status'],
                    data=['uploaded']
                    )
        
    qc_res = db.readDB(schema=schema_name, table=table_name[2], columns=column_list[2])
    #qc_id = [i[0] + last_img_id for i in qc_res]
    qc_id = [i + 1 + last_img_id for i in range(num_row)]

    # print(qc_id)
    print()

    # 6. Features
    print('-----Features-----')
    # df_features['product_id'] = [1 for _ in range(num_row)]
    # df_features['image_path'] = ["fixfix" for _ in range(num_row)]
    # df_features['image_width'] = [10000 for _ in range(num_row)]
    # df_features['image_height'] = [10000 for _ in range(num_row)]
    # df_features['upload_date'] = ["1993-08-27 00:00:01" for _ in range(num_row)] ##### need to fix
    # df_features['like_cnt'] = [0 for _ in range(num_row)] ##### need to fix

    ## 6-1. column setting
    col_tmp_features = ['qc_id', 'user_id', 'dataset_id', 'product_id', 'upload_date'] ## image_width, image_height 등 넣어야함
    column_for_features = [*column_list[5][1:31], *col_tmp_features]

    ## 6-2. Insert data
    for i in range(num_row):
        data_from_features_csv = list(df_features.iloc[i])[1:]
        data_tmp_features = [qc_id[i],user_id, dataset_id, pi_id[i], upload_time]
        data = [*data_from_features_csv, *data_tmp_features]
        db.insertDB(schema=schema_name, 
                    table=table_name[5],
                    columns=column_for_features,
                    data=data)
    
    img_id = qc_id.copy()
    print()
    
    # 7. Insert GT 
    print('-----GT-----')
    GroundTruth = unzipped_dataset_info["PATH"] + 'GT.csv'
    df_GT = pd.read_csv(GroundTruth)
    num_row_GT = len(df_GT)
    df_img_id_filename = pd.DataFrame(columns = ['filename', 'img_id'])
    df_img_id_filename['filename'] = df_features['filename']
    df_img_id_filename['img_id'] = img_id
    # print(df_img_id_filename.head())

    object_list = db.readDB(schema=schema_name, table=table_name[7], columns=column_list[7])
    df_object_list = pd.DataFrame(data = object_list, columns = ['gt_object_id', 'object'])
    # print(df_object_list.head())

    df_GT = pd.merge(df_GT, df_img_id_filename, on = 'filename', how='left')
    df_GT = pd.merge(df_GT, df_object_list, on = 'object', how='left')
    gt_col_sorted = ['img_id', 'gt_object_id', 'height', 'weight', 'length', 'Xordinate',
       'Yordinate', 'Zordinate', 'Xrotate', 'Yrotate', 'Zrotate', 'state',
       'occlusion', 'occlusion_kf', 'truncation', 'amt_occulsion',
       'amt_occulsion_kt', 'amt_border_l', 'amt_border_r', 'amt_border_kf',
       ]
    df_GT = df_GT[gt_col_sorted]
    for i in range(num_row_GT):
        data_from_GT_csv = list(df_GT.iloc[i])
        db.insertDB(schema=schema_name, 
                    table=table_name[0],
                    columns=column_list[0][1:],
                    data=data_from_GT_csv)
    print()

    # 8. output
    images = df_features["filename"]
    user_id_list = [user_id for _ in range(num_row)]
    dataset_id_list = [dataset_id for _ in range(num_row)]
    id_list = [img_id, qc_id, pi_id, user_id_list, dataset_id_list, images]
    inserted_info = pd.DataFrame(id_list).transpose()
    inserted_info.columns = ['img_id', 'qc_id', 'product_id', 'user_id', 'dataset_id', 'filename']

    return inserted_info

def load_list_view_default(db):
    '''
    load_list view for main page

    [inputs]
    - target db object (CRUD)
    
    [output]
    - df_result: output from query, pd.DataFrame
      cols = ['dataset_id', 'dataset_name',
              'price_total', 'iamge_count', 'avg_price_per_image',
              'sales_count', 'like_count',
              'qc_state', 'qc_score', 
              'uploader', 'upload_date', 
              'object_list', 'object_count','object_info_in_detail']

      also,
        the value of colmnn "object_list" is *list* of object 
            (e.g., ['Van','Cyclist', 'Pedestrian'])
        the value of column "object_info_in_detail" is dictinary that keys are object's name and value is its count
            (e.g., {'Cyclist': 1, 'Pedestrian': 1, 'Van': 2})
    '''

    result = None

    # dataset information
    sql =  "select res.dataset_id, res.dataset_name,\
                sum(res.price) as price_total,\
                count(res.dataset_id) as total_image_count,\
                sum(res.price) / count(res.dataset_id) as avg_price_per_image, \
                max(res.dataset_selection_cnt) as sales_count,\
                sum(res.like_cnt) as like_count, \
                res.qc_status as qc_state, \
                AVG(res.qc_score) as qc_score, \
                res.user_idname as uploader, \
                res.upload_date as upload_date \
            from( \
                select f.img_id, f.upload_date, f.like_cnt, d.*, p.*, q.qc_status, q.qc_score, u.* \
                from features f \
                left join productinfo p on f.product_id =p.product_id \
                left join datasetinfo d on d.dataset_id =f.dataset_id \
                left join qc q on q.qc_id =f.qc_id \
                left join public.user u on u.user_id =f.user_id\
                ) res \
            group by res.dataset_id, res.dataset_name, res.qc_status, res.user_idname, res.upload_date;"

    result = db.execute(sql)
    columns = ['dataset_id', 'dataset_name', 'price_total', 'iamge_count', 'avg_price_per_image', 'sales_count', 'like_count' ,'qc_state' ,'qc_score', 'uploader' ,'upload_date']
    df_result = pd.DataFrame(data = result, columns=columns)

    # object information
    ## a. df for final result
    df_obj_list_split_by_dataset = pd.DataFrame(columns = ['dataset_id', 'object_list', 'object_count', 'object_info_in_detail'])
    ## b. excute query
    sql =  "select  res.dataset_id, res.gt_object, count(res.gt_object) \
            from ( \
                select o.gt_object, g.gt_height, g.gt_width, dataset.dataset_id \
                from groundtruth g  \
                left join ( \
                    select f.img_id, d.dataset_id \
                    from features f \
                    left join datasetinfo d on d.dataset_id = f.dataset_id \
                ) dataset on dataset.img_id = g.img_id \
                left join public.object o on o.gt_object_id = g.gt_object_id \
                group by o.gt_object, g.gt_height, g.gt_width, dataset.dataset_id \
            ) res \
            group by res.dataset_id, res.gt_object \
            order by res.dataset_id; "    
    result_obj = db.execute(sql)
    col_obj = ['dataset_id', 'gt_object', 'count']
    df_obj = pd.DataFrame(data = result_obj, columns= col_obj)
    
    ## c. update column dataset_ids
    df_obj_unique_dataset_id = df_obj['dataset_id'].unique()
    df_obj_list_split_by_dataset['dataset_id'] = list(df_obj_unique_dataset_id)
    
    ## d. update column object_count
    df_groupby1=df_obj.groupby('dataset_id').sum()
    df_obj_list_split_by_dataset['object_count'] = list(df_groupby1['count'])

    ## e. update column object_list and object_info_in_detail
    tmp_list_for_detail = []
    tmp_list_for_object_list = []
    for i in df_obj_unique_dataset_id:
        df_target = df_obj[df_obj['dataset_id']==i]
        tmp_dict = {}
        df_target_len = len(df_target)
        sub_tmp_list_for_object_list = []
        for j in range(df_target_len):
            tmp_key = df_target['gt_object'].iloc[j]
            tmp_value = df_target['count'].iloc[j]
            tmp_dict[tmp_key] = tmp_value
            sub_tmp_list_for_object_list.append(tmp_key)
        tmp_list_for_detail.append(tmp_dict)
        tmp_list_for_object_list.append(sub_tmp_list_for_object_list)
        
    df_obj_list_split_by_dataset['object_list'] = tmp_list_for_object_list
    df_obj_list_split_by_dataset['object_info_in_detail'] = tmp_list_for_detail

    df_result = pd.merge(df_result,
                         df_obj_list_split_by_dataset,
                         on='dataset_id',
                         how='left'
                         )
    print()

    return df_result


def read_user_query(db, filter_info):
    # user query spec 보고 interface 업뎃할 예정
    pass


def update_multiple_columns(db, df, mode):
    '''
    update multiple columns 
    [inputs]
    - target db object (CRUD)
    - df: pd.DataFrame
    - mode: string, the mode should be one of ["img_path", "img_WH", "start_QC", "QC_score", "object_count", "end_QC"]
    
    [output]
    - success: 

    '''
    # 0. Initial Setting
    success = False 
    schema_name = SCHEMA_NAME
    target_list = [
        ['Features', ['img_id', 'image_path'],], 
        ['Features', ['img_id', 'image_width', 'image_height']],
        ['QC', ['qc_id', 'qc_start_date']],
        ['QC', ['qc_id', 'qc_score']],
        ['QC', ['qc_id', 'object_count']],
        ['QC', ['qc_id', 'qc_end_date']]
        ]

    # 1. Setting mode
    if mode == 'img_path':
        idx = 0
    elif mode == 'img_WH':
        idx = 1
    elif mode == 'start_QC':
        idx = 2
        status = 'QC_start'
    elif mode == 'QC_score':
        idx = 3
        status = "QC_end"
    elif mode == 'object_count':
        idx = 4
        status = "QC_end+obj_cnt"
    elif mode == 'end_QC':
        idx = 5
        status = "QC_end+obj_cnt+duplicate"
    else: 
        print("Invalid mode is selected")
        print('The mode should be one of ["img_path", "img_WH", "start_QC", "QC_score", "object_count", "end_QC"]')
    
    # 2. Select target column to update data 
    target_table = target_list[idx][0]
    target_df = df[target_list[idx][1]]

    columns = target_df.columns
    
    # 3. update data in DB
    for i in range(len(columns[1:])):
        for j in range(len(target_df)):
            condition = f"{columns[0]}='{df[columns[0]][j]}'"
            success = db.updateDB(schema=schema_name, table=target_table, column=columns[i+1], value=df[columns[i+1]][j],condition=condition)
    
    # 4. (optional) udpated QC_status
    if idx in (2,3,4,5):
        for j in range(len(target_df)):
            condition = f"{columns[0]}='{df[columns[0]][j]}'"
            success = db.updateDB(schema=schema_name, table=target_table, column='qc_status', value=status,condition=condition)

    return success 

# duplicate 스키마를 바꿔서 체크를 한다. 
# qc에 obj_type 다 빼고, cnt만 
# 더 추가하면 됨