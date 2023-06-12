from dbmanager.crud import CRUD
from dbmanager.configs import SCHEMA_NAME, TABLE_NAME, POSTGRES_CONFIG, ALL_COLUMNS_INFO, PK_LIST, FK_LIST, ALL_COLUMNS
import pandas as pd
from datetime import datetime
from pytz import timezone
import math 
import random
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
        success = db.drop_table(schema_name, str("copy_"+table_name[i]))
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
    # print('----Object table')
    objects= ['Car', 'Van', 'Truck', 'Pedestrian', 'Person (sitting)', 'Cyclist', 'Tram', 'Misc']

    for i in range(len(objects)):
        db.insertDB(schema=schema_name, 
                    table=table_name[7],
                    columns = ['gt_object'],
                    data = [objects[i]]
                    )
        
    return success

def copy_db(db):
    '''
    db를 복사하는 함수

    [input]
    - db : target db object (CRUD)

    [output]
    - success : initalize 성공여부
    '''

    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME
    for i, table in enumerate(table_name):
        table_copy = f"copy_{table}"
        db.drop_table(schema_name, table_copy)
        success = db.copyTable(schema = schema_name, table = table) 

    return success

def restore_db(db):
    '''
    db를 복구하는 함수

    [input]
    - db : target db object (CRUD)

    [output]
    - success : initalize 성공여부
    '''
    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME
    all_columns_info = ALL_COLUMNS_INFO
    all_columns = ALL_COLUMNS
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

    for i, table in enumerate(table_name):
        success = db.restoreTable2(schema = schema_name, table = table, table_column = all_columns[i])

        # success = db.drop_table(schema_name, table_name[i])
        # success = db.restoreTable(schema_name, table = table)
        # success = db.addPK(schema_name, table_name[i], pk_list[i])


    return success

def get_user_point(db, user_idname):
    '''
    output = pd.dataframe, 그 유저가 가지고 있는 포인트
    '''

    sql = f"select u.user_point from public.user u where u.user_idName = '{user_idname}';"
    data = db.execute(sql)
    result_df = pd.DataFrame(data=data, columns=['user_point'])

    return result_df

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
    if len(result)==0:
        return valid

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
    user_info = [user_idname, user_password, 100000]

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
    user_info = check_user(db=db, unzipped_dataset_info=unzipped_dataset_info)
    user_info = user_info[0]
    user_id = user_info[0]
    print()
    print(f"Uploading {user_info[1]}(user_id : {user_id})'s file")

    # 2. DatasetInfo
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
    print('DatasetInfo table is updated')

    # 3. read Feature.csv
    features = unzipped_dataset_info["PATH"] + 'Features.csv'
    df_features = pd.read_csv(features)
    num_row = len(df_features)

    # 4. ProductInfo
    for i in range(num_row):
        db.insertDB(schema=schema_name, 
                    table=table_name[1],
                    columns = ['sold_count'],
                    data = [0]
                    )
    pi_id = [i + 1 + last_img_id for i in range(num_row)]
  
    print('ProductInfo table is updated')

    # 5. QC
    for i in range(num_row):
        db.insertDB(schema=schema_name, 
                    table=table_name[2],
                    columns=['qc_status', 'qc_duplicate'],
                    data=['uploaded', 0]
                    )
        
    qc_id = [i + 1 + last_img_id for i in range(num_row)]
    print('QC table is updated')

    # 6. Features
    ## 6-1. column setting
    col_tmp_features = ['qc_id', 'user_id', 'dataset_id', 'product_id', 'upload_date'] ## image_width, image_height 등 넣어야함
    column_for_features = [*column_list[5][5:35], *col_tmp_features]

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
    print('Features table is updated')
    
    # 7. Insert GT 
    GroundTruth = unzipped_dataset_info["PATH"] + 'GT.csv'
    df_GT = pd.read_csv(GroundTruth)
    num_row_GT = len(df_GT)
    df_img_id_filename = pd.DataFrame(columns = ['filename', 'img_id'])
    df_img_id_filename['filename'] = df_features['filename']
    df_img_id_filename['img_id'] = img_id

    object_list = db.readDB(schema=schema_name, table=table_name[7], columns=column_list[7])
    df_object_list = pd.DataFrame(data = object_list, columns = ['gt_object_id', 'object'])

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
    print('GT table is updated')

    # 8. output
    images = df_features["filename"]
    user_id_list = [user_id for _ in range(num_row)]
    dataset_id_list = [dataset_id for _ in range(num_row)]
    id_list = [img_id, qc_id, pi_id, user_id_list, dataset_id_list, images]
    inserted_info = pd.DataFrame(id_list).transpose()
    inserted_info.columns = ['img_id', 'qc_id', 'product_id', 'user_id', 'dataset_id', 'filename']

    return inserted_info




########################################
########## LISTVIEW FUNCTIONS ##########
########################################

def load_list_view(db, page=1, item_per_page=10, user_idName = None):
    '''
    load_list view

    [inputs]
    - db            : target db object (CRUD)
    - page: int, page number, default: 1,  if you want load 3rd page, then 3
    - item_per_page: int, default:10, the number of items per page
    - user_idName   : string, default: None, 

    [output]
    - total_count: int, the number of rows
    - df_result: output from query, pd.DataFrame, if df_result is empty pd.DataFrame, returns None
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

    total_count, result_df = _load_list_view_default(db=db, page=page, item_per_page=item_per_page, user_idName=user_idName)
    if total_count == 0:
        return total_count, None
    
    max_page = int(math.ceil(total_count/item_per_page))

    if user_idName is not None:
        print(f"-----Loading {user_idName}'s dataset-----")
        result_df = result_df[result_df['uploader']==str(user_idName)]
        
    return max_page, result_df 

def _load_list_view_default(db, page=1, item_per_page=10, user_idName = None):
    '''
    load_list view 
    if user_idName is not None -> then returns listview for the user's uploaded dataset

    [inputs]
    - db: target db object (CRUD)
    - page: int, page number, default: 1,  if you want load 3rd page, then 3
    - item_per_page: int, default:10, the number of items per page
    - user_idName   : string, default: None, 

    [output]
    - total_count: int, the number of rows
    - df_result: pd.DataFrame, output from query, if df_result is empty pd.DataFrame, returns None
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
    # 1. initial setting and total rows cnt
    result = None
    item_start = 0 + item_per_page * (page - 1)
    if user_idName is not None:
        condition_id = f"where u.user_idName = '{user_idName}' and f.not_show = FALSE"
    else: condition_id = "where f.not_show = FALSE"

    sql = f"select res.dataset_id, res.dataset_name, res.qc_status, res.user_idname, res.upload_date \
            from( \
                select f.img_id, f.upload_date, f.like_cnt, d.*, p.*, q.qc_status, q.qc_score, u.* \
                from features f \
                left join productinfo p on f.product_id =p.product_id \
                left join datasetinfo d on d.dataset_id =f.dataset_id \
                left join qc q on q.qc_id =f.qc_id \
                left join public.user u on u.user_id =f.user_id \
                {condition_id} \
                ) res \
            group by res.dataset_id, res.dataset_name, res.qc_status, res.user_idname, res.upload_date;"
    total_cnt = db.execute(sql)
    # print("###############################", total_cnt)
    total_cnt = len(total_cnt)
    if total_cnt == 0:
        return total_cnt, None

    # 2. dataset information
    sql = f"select res.dataset_id, res.dataset_name,\
                sum(res.price) as price_total,\
                count(res.dataset_id) as total_image_count,\
                sum(res.price) / count(res.dataset_id) as avg_price_per_image, \
                max(res.dataset_selection_cnt) as sales_count,\
                sum(res.like_cnt) as like_count, \
                res.qc_status as qc_state, \
                AVG(res.qc_score) as qc_score, \
                res.user_idname as uploader, \
                res.upload_date as upload_date, \
                res.dataset_description as dataset_description \
            from( \
                select f.img_id, f.upload_date, f.like_cnt, d.*, p.*, q.qc_status, q.qc_score, u.* \
                from features f \
                left join productinfo p on f.product_id =p.product_id \
                left join datasetinfo d on d.dataset_id =f.dataset_id \
                left join qc q on q.qc_id =f.qc_id \
                left join public.user u on u.user_id =f.user_id \
                {condition_id} \
                ) res \
            group by res.dataset_id, res.dataset_name, res.qc_status, res.user_idname, res.upload_date, res.dataset_description\
            order by res.dataset_id limit {item_per_page} offset {item_start};"

    result = db.execute(sql)
    columns = ['dataset_id', 'dataset_name', 'price_total', 'image_count', 'avg_price_per_image', 'sales_count', 'like_count' ,'qc_state' ,'qc_score', 'uploader' ,'upload_date', 'description']
    df_result = pd.DataFrame(data = result, columns=columns)

    to_process_qcState = list(df_result['qc_state'])

    for i in range(len(to_process_qcState)):
        if to_process_qcState[i] == 'uploaded':
            to_process_qcState[i] = 'Pending'
        elif to_process_qcState[i] == 'QC_start':
            to_process_qcState[i] = 'In Progress'
        elif to_process_qcState[i] in ('QC_end','QC_end+obj_cnt','QC_end+obj_cnt+duplicate'):
            to_process_qcState[i] = 'Done'

    df_result['qc_state'] = to_process_qcState

    target_dataset_id = tuple(df_result['dataset_id'])
    
    # 3. object information
    ## a. df for final result and condition settting 
    df_obj_list_split_by_dataset = pd.DataFrame(columns = ['dataset_id', 'object_list', 'object_count', 'object_info_in_detail'])

    if len(target_dataset_id) == 0:
        return df_result
    elif len(target_dataset_id) == 1:
        condition = f"where dataset.dataset_id = '{target_dataset_id[0]}'"
    else:
        condition = f"where dataset.dataset_id in {target_dataset_id}" 
    
    ## b. excute query
    sql = f"select  res.dataset_id, res.gt_object, count(res.gt_object) \
            from ( \
                select o.gt_object, g.gt_height, g.gt_width, dataset.dataset_id \
                from groundtruth g  \
                left join ( \
                    select f.img_id, d.dataset_id \
                    from features f \
                    left join datasetinfo d on d.dataset_id = f.dataset_id \
                ) dataset on dataset.img_id = g.img_id \
                left join public.object o on o.gt_object_id = g.gt_object_id \
                {condition} \
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

    return total_cnt, df_result

def load_detailed_view(db, df, K = 10): 
    '''
    sampling image and load_detailed_view

    [inputs]
    - db    : target db object (CRUD)
    - df    : pd.DataFrame, 샘플 이미지를 추출할 리스트뷰의 값
    - k     : int, number of sampled images, default: 10

    [output]
    - selected_K_img_df: output from query, dictionary, if empty dictionary, returns None
      key: dataset_id
      values: pd.dataframe with cols = ['img_id', 'image_path', 'qc_score', 'dataset_id'
                                        'object_list', 'object_count','object_info_in_detail']
      also,
        the value of colmnn "object_list" is *list* of object 
            (e.g., ['Van','Cyclist', 'Pedestrian'])
        the value of column "object_info_in_detail" is dictinary that keys are object's name and value is its count
            (e.g., {'Cyclist': 1, 'Pedestrian': 1, 'Van': 2})

    - all_img_dict: all data regarding the selected dataset_list, dictionary,

    '''
    # 0. Initial Setting
    success = False
    schema_name = SCHEMA_NAME
    columns = [*ALL_COLUMNS[5], *ALL_COLUMNS[2]]
    result_df = pd.DataFrame(columns=columns)

    # 1. make dataset_id list 
    dataset_id_list = list(df['dataset_id'].unique())
    dataset_id_and_img_id_list = []
    # 2. Create img_ids list and randomly select K images 
    for id in dataset_id_list:
        # 2-1. Create img_ids list of the dataset_id
        condition = f"dataset_id = '{id}'"
        img_ids = db.readDB_with_filtering(schema = schema_name, table = 'Features', columns = ['img_id'], condition = condition)
        img_ids = list(sum(img_ids, ()))
        # 2-2. When K is bigger than len(img_ids), then sampling should be len(img_ids)
        if K > len(img_ids):
            K_to_apply = len(img_ids)
        else:
            K_to_apply = K
        # 2-3. Randomly select K_to_apply images
        random_img_ids = random.sample(img_ids, K_to_apply)
        # 2-4. make dataset_id_and_img_id_list
        dataset_id_and_img_id_list.append([id, img_ids, random_img_ids])

    # 3. Join option and condition
    join = [["JOIN", "Features", "QC", "qc_id", "qc_id"]]

    # 4. read DB with filtering
    for dataset in dataset_id_and_img_id_list:
        img_ids_tuple = tuple(dataset[2])
        condition_ft = f"features.img_id IN {img_ids_tuple}"
        columns = ['image_path']
        result_ft_tmp = db.readDB_join_filtering(schema = schema_name, table = 'Features', columns = '*', join=join, condition=condition_ft )
        for i in result_ft_tmp:
            result_df.loc[len(result_df)] = list(i)

    # 5. object information
    ## a. df for final result and condition settting 
    df_obj_list_split_by_img = pd.DataFrame(columns = ['img_id', 'object_list', 'object_count', 'object_info_in_detail'])
    df_obj_list_split_by_img_tmp = pd.DataFrame(columns = ['img_id', 'object_list', 'object_count', 'object_info_in_detail'])

    for dataset in dataset_id_and_img_id_list:
        img_ids_tuple = tuple(dataset[2])
        for id in img_ids_tuple:
            condition_img_id= f"WHERE dataset.img_id = {id}"
            ## b. excute query
            sql = f"select  res.img_id, res.gt_object, count(res.gt_object) \
                    from ( \
                        select o.gt_object, g.gt_height, g.gt_width, dataset.img_id \
                        from groundtruth g  \
                        left join ( \
                            select f.img_id, d.dataset_id \
                            from features f \
                            left join datasetinfo d on d.dataset_id = f.dataset_id \
                        ) dataset on dataset.img_id = g.img_id \
                        left join public.object o on o.gt_object_id = g.gt_object_id \
                        {condition_img_id} \
                        group by o.gt_object, g.gt_height, g.gt_width, dataset.img_id \
                    ) res \
                    group by res.img_id, res.gt_object \
                    order by res.img_id; "    
            result_obj = db.execute(sql)
            col_obj = ['img_id', 'gt_object', 'count']
            df_obj = pd.DataFrame(data = result_obj, columns= col_obj)
    
            ## c. update column dataset_ids
            df_obj_unique_img_id = df_obj['img_id'].unique()
            df_obj_list_split_by_img_tmp['img_id'] = list(df_obj_unique_img_id)
    
            ## d. update column object_count
            df_groupby1=df_obj.groupby('img_id').sum()
            df_obj_list_split_by_img_tmp['object_count'] = list(df_groupby1['count'])

            ## e. update column object_list and object_info_in_detail
            tmp_list_for_detail = []
            tmp_list_for_object_list = []
            for i in df_obj_unique_img_id:
                df_target = df_obj[df_obj['img_id']==i]
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
                df_obj_list_split_by_img.loc[len(df_obj_list_split_by_img)] = [i, tmp_list_for_object_list[0], list(df_groupby1['count'])[0], tmp_list_for_detail[0]]

    target_cols = ['img_id', 'image_path', 'qc_score', 'dataset_id']
    result_df = result_df[target_cols]
    result_df = pd.merge(result_df,
                         df_obj_list_split_by_img,
                         on='img_id',
                         how='left'
                         )
    
    dataset_list = result_df['dataset_id'].unique()
    selected_K_img_dict = dict()

    for i in dataset_list:
        selected_K_img_dict[i] = result_df[result_df['dataset_id']==i]

    # 6. load all images 
    if len(dataset_id_list) == 1:
        condition_all = f"f.dataset_id = {dataset_id_list[0]}"
    else: 
        condition_all = f"f.dataset_id in {tuple(dataset_id_list)}"

    sql = f"select f.*, q.qc_status as qc_state, q.qc_score, p.price \
            from features f \
            left join qc q on q.qc_id = f.qc_id \
            left join productinfo p on p.product_id = f.product_id \
            where {condition_all};"
    res_all = db.execute(sql)
    columns = [*ALL_COLUMNS[5], 'qc_state', 'qc_score', 'price']
    
    result_all_df = pd.DataFrame(data = res_all, columns=columns)
    ## 6-1. processing result_all_df['qc_state']
    to_process_qcState = list(result_all_df['qc_state'])

    for i in range(len(to_process_qcState)):
        if to_process_qcState[i] == 'uploaded':
            to_process_qcState[i] = 'Pending'
        elif to_process_qcState[i] == 'QC_start':
            to_process_qcState[i] = 'In Progress'
        elif to_process_qcState[i] in ('QC_end','QC_end+obj_cnt','QC_end+obj_cnt+duplicate'):
            to_process_qcState[i] = 'Done'

    result_all_df['qc_state'] = to_process_qcState

    # 7. object information for 6
    df_obj_list_split_by_img = pd.DataFrame(columns = ['img_id', 'object_list', 'object_count', 'object_info_in_detail'])
    df_obj_list_split_by_img_tmp = pd.DataFrame(columns = ['img_id', 'object_list', 'object_count', 'object_info_in_detail'])

    for dataset in dataset_id_and_img_id_list:
        img_ids_tuple = tuple(dataset[1])
        for id in img_ids_tuple:
            condition_img_id= f"WHERE dataset.img_id = {id}"
            ## b. excute query
            sql = f"select  res.img_id, res.gt_object, count(res.gt_object) \
                    from ( \
                        select o.gt_object, g.gt_height, g.gt_width, dataset.img_id \
                        from groundtruth g  \
                        left join ( \
                            select f.img_id, d.dataset_id \
                            from features f \
                            left join datasetinfo d on d.dataset_id = f.dataset_id \
                        ) dataset on dataset.img_id = g.img_id \
                        left join public.object o on o.gt_object_id = g.gt_object_id \
                        {condition_img_id} \
                        group by o.gt_object, g.gt_height, g.gt_width, dataset.img_id \
                    ) res \
                    group by res.img_id, res.gt_object \
                    order by res.img_id; "    
            result_obj = db.execute(sql)
            col_obj = ['img_id', 'gt_object', 'count']
            df_obj = pd.DataFrame(data = result_obj, columns= col_obj)
    
            ## c. update column dataset_ids
            df_obj_unique_img_id = df_obj['img_id'].unique()
            df_obj_list_split_by_img_tmp['img_id'] = list(df_obj_unique_img_id)
    
            ## d. update column object_count
            df_groupby1=df_obj.groupby('img_id').sum()
            df_obj_list_split_by_img_tmp['object_count'] = list(df_groupby1['count'])

            ## e. update column object_list and object_info_in_detail
            tmp_list_for_detail = []
            tmp_list_for_object_list = []
            for i in df_obj_unique_img_id:
                df_target = df_obj[df_obj['img_id']==i]
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
                df_obj_list_split_by_img.loc[len(df_obj_list_split_by_img)] = [i, tmp_list_for_object_list[0], list(df_groupby1['count'])[0], tmp_list_for_detail[0]]

    result_all_df = pd.merge(result_all_df,
                         df_obj_list_split_by_img,
                         on='img_id',
                         how='left'
                         )

    dataset_all_list = result_all_df['dataset_id'].unique()
    all_img_dict = dict()

    for i in dataset_all_list:
        all_img_dict[i] = result_all_df[result_all_df['dataset_id']==i]

    return selected_K_img_dict, all_img_dict

def load_list_view_search(db, condition_filter, page=1, item_per_page=10, user_idName = None):
    '''
    load_list view 
    if user_idName is not None -> then returns listview for the user's uploaded dataset

    [inputs]
    - db: target db object (CRUD)
    - condition_filter: dictionary 
       {"BASIC_INFO": string, 
        "QUALITY_INFO": {"qc_state", "qc_score", "objects"}
        "SENSOR_INFO": {"Roll", "Pitch", "Yaw", "Wx", "Wy", "Wz", "Vf", "Vl", "Vu","Ax", "Ay", "Az"}
        "CUSTOM_FILTERING": WIP
        }
        (e.g.) 
        "BASIC_INFO": 'asdasdasdasd', 
        "QUALITY_INFO": {"qc_state": ['Done'],
                        "qc_score": ['Low', 'Medium','High'],
                        "objects": ['Car','Truck','Pedestrian', 'Sitter', 'Cyclist', 'Tram', 'Misc']
                        },
        "SENSOR_INFO": {"Roll": (1,1), "Pitch": (3,4), "Yaw": (5,6),
                        "Wx": (7,8), "Wy": (9,10), "Wz": (11,12),
                        "Vf": (13,14), "Vl": (15,16), "Vu": (17,18),
                        "Ax": (19,20), "Ay": (21,22), "Az": (23,24)
                    },
        "CUSTOM_FILTERING": "asdasdasd"
        }
    - page: int, page number, default: 1,  if you want load 3rd page, then 3
    - item_per_page: int, default:10, the number of items per page
    - user_idName   : string, default: None, 

    [output]
    - total_count: int, the number of rows
    - df_result: pd.DataFrame, output from query, if df_result is empty pd.DataFrame, returns None
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
    # 0. cleansing condition_filter
    condition_filter = _cleansing_condition_filter(condition_filter)
    keys = list(condition_filter.keys())

    # 1. initial setting and make conditions
    result = None
    item_start = 0 + item_per_page * (page - 1)

    ## make conditions 
    condition_list = []
    if 'BASIC_INFO' in keys:
        string_b = f"(d.dataset_description like '%%{condition_filter['BASIC_INFO']}%%')"
        condition_list.append(string_b)

    if 'QUALITY_INFO' in keys:
        quality_info_dict = condition_filter['QUALITY_INFO']
        quality_info_keys = list(quality_info_dict.keys())
        for key in quality_info_keys:
            value_q = quality_info_dict[key]
            if key =='qc_status':
                if len(value_q)==1:
                    string_q = f"(q.{key}='{value_q[0]}')"
                    condition_list.append(string_q)
                else:
                    string_q = f"(g.{key} in {tuple(value_q)})"
                    condition_list.append(string_q)
            elif key == 'gt_object_id':
                if len(value_q)==1:
                    string_q = f"(g.{key}='{value_q[0]}')"
                    condition_list.append(string_q)
                else:
                    string_q = f"(g.{key} in {tuple(value_q)})"
                    condition_list.append(string_q)
            else:
                tmp_score_list = []
                for value in value_q:
                    string_q_tmp = f"(q.{key} between {float(value[0])} and {float(value[1])})"
                    tmp_score_list.append(string_q_tmp)
                string_q = "("+" or ".join(tmp_score_list)+")"
                condition_list.append(string_q)

    if 'SENSOR_INFO' in keys:
        sensor_info_dict = condition_filter['SENSOR_INFO']
        sensor_info_keys = list(sensor_info_dict.keys())
        sensor_string_list = []
        for key in sensor_info_keys:
            value_s = sensor_info_dict[key]
            if value_s[0] == 'null':
                string_s = f"(f.{key} < {value_s[1]})"
            elif value_s[1] == 'null':
                string_s = f"(f.{key} >= {value_s[0]})"
            else:
                string_s = f"(f.{key} between {value_s[0]} and {value_s[1]})"
            condition_list.append(string_s)
            sensor_string_list.append(string_s)
        
    if 'CUSTOM_FILTERING' in keys:
        pass

    if user_idName is not None:
        string_id = f"u.user_idName = '{user_idName}'"
        condition_list.append(string_id)

    if not condition_list:
        # print("#####", condition_list)
        condition = " "
    else: 
        condition = "WHERE "+" and ".join(condition_list)

    # 1. total rows cnt
    sql = f"select res.dataset_id, res.dataset_name, res.qc_status, res.user_idname, res.upload_date \
            from( \
                select f.img_id, f.upload_date, f.like_cnt, d.*, p.*, q.qc_status, q.qc_score, u.* \
                from features f \
                left join productinfo p on f.product_id =p.product_id \
                left join datasetinfo d on d.dataset_id =f.dataset_id \
                left join qc q on q.qc_id =f.qc_id \
                left join public.user u on u.user_id =f.user_id \
                join public.GroundTruth g on g.img_id=f.img_id \
                {condition} \
                ) res \
            group by res.dataset_id, res.dataset_name, res.qc_status, res.user_idname, res.upload_date;"
    total_cnt = db.execute(sql)
    # print(total_cnt)
    total_cnt = len(total_cnt)
    if total_cnt == 0:
        return total_cnt, None

    # 2. dataset information
    sql = f"select res.dataset_id, res.dataset_name,\
                sum(res.price) as price_total,\
                count(distinct res.img_id) as total_image_count,\
                sum(res.price) / count(res.dataset_id) as avg_price_per_image, \
                max(res.dataset_selection_cnt) as sales_count,\
                sum(res.like_cnt) as like_count, \
                res.qc_status as qc_state, \
                AVG(res.qc_score) as qc_score, \
                res.user_idname as uploader, \
                res.upload_date as upload_date, \
                res.dataset_description as dataset_description \
            from( \
                select f.img_id, f.upload_date, f.like_cnt, d.*, p.*, q.qc_status, q.qc_score, u.* \
                from features f \
                left join productinfo p on f.product_id =p.product_id \
                left join datasetinfo d on d.dataset_id =f.dataset_id \
                left join qc q on q.qc_id =f.qc_id \
                left join public.user u on u.user_id =f.user_id \
                join public.GroundTruth g on g.img_id=f.img_id \
                {condition} \
                ) res \
            group by res.dataset_id, res.dataset_name, res.qc_status, res.user_idname, res.upload_date, res.dataset_description \
            order by res.dataset_id limit {item_per_page} offset {item_start};"

    result = db.execute(sql)
    columns = ['dataset_id', 'dataset_name', 'price_total', 'image_count', 'avg_price_per_image', 'sales_count', 'like_count' ,'qc_state' ,'qc_score', 'uploader' ,'upload_date', 'description']
    df_result = pd.DataFrame(data = result, columns=columns)

    to_process_qcState = list(df_result['qc_state'])

    for i in range(len(to_process_qcState)):
        if to_process_qcState[i] == 'uploaded':
            to_process_qcState[i] = 'Pending'
        elif to_process_qcState[i] == 'QC_start':
            to_process_qcState[i] = 'In Progress'
        elif to_process_qcState[i] in ('QC_end','QC_end+obj_cnt','QC_end+obj_cnt+duplicate'):
            to_process_qcState[i] = 'Done'

    df_result['qc_state'] = to_process_qcState


    target_dataset_id = tuple(df_result['dataset_id'])
    
    # 3. object information
    ## a. df for final result and condition settting 
    df_obj_list_split_by_dataset = pd.DataFrame(columns = ['dataset_id', 'object_list', 'object_count', 'object_info_in_detail'])

    if len(target_dataset_id) == 0:
        return df_result
    elif len(target_dataset_id) == 1:
        condition = f"where dataset.dataset_id = '{target_dataset_id[0]}'"
    else:
        condition = f"where dataset.dataset_id in {target_dataset_id}" 
    
    ## b. excute query
    sql = f"select  res.dataset_id, res.gt_object, count(res.gt_object) \
            from ( \
                select o.gt_object, g.gt_height, g.gt_width, dataset.dataset_id \
                from groundtruth g  \
                left join ( \
                    select f.img_id, d.dataset_id \
                    from features f \
                    left join datasetinfo d on d.dataset_id = f.dataset_id \
                ) dataset on dataset.img_id = g.img_id \
                left join public.object o on o.gt_object_id = g.gt_object_id \
                {condition} \
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

    return total_cnt, df_result

def _cleansing_condition_filter(condition_filter):
    key_dict={
        'qc_state': 'qc_status',
        'qc_score': 'qc_score',
        'objects': 'gt_object_id',
        'roll': 'roll',
        'pitch': 'pitch',
        'yaw': 'yaw',
        'wx': 'ang_x',
        'wy': 'ang_y',
        'wz': 'ang_z',
        'vf': 'velo_forward',
        'vl': 'velo_leftward',
        'vu': 'velo_upward',
        'ax': 'accel_x',
        'ay': 'accel_y',
        'az': 'accel_z',
        'Pending': 'uploaded',
        'In Progress': 'QC_start',
        'Done': 'QC_end+obj_cnt+duplicate',
        'Low': (50, 70),
        'Medium':(70, 90),
        'High':(90, 100),
        'Car': 1,
        'Van': 2,
        'Truck': 3,
        'Pedestrian': 4,
        'Sitter': 5,
        'Cyclist': 6,
        'Tram': 7,
        'Misc': 8,
    }
    keys = list(condition_filter.keys())

    if 'QUALITY_INFO' in keys:
        temp = condition_filter['QUALITY_INFO']
        sensor_key_bf = list(temp.keys())
        for key in sensor_key_bf:
            for idx, item in enumerate(temp[key]):
                temp[key][idx] = key_dict[item]
            temp[key_dict[key]] = temp.pop(str(key))
            
        condition_filter['QUALITY_INFO'] = temp

    if 'SENSOR_INFO' in keys:
        temp = condition_filter['SENSOR_INFO']
        sensor_key_bf = list(temp.keys())
        for key in sensor_key_bf:
            temp[key_dict[key]] = temp.pop(str(key))
            
        condition_filter['SENSOR_INFO'] = temp
    
    return condition_filter




######################################
########## UPDATE FUNCTIONS ##########
######################################

def update_multiple_columns(db, df, mode):
    '''
    update multiple columns 

    [inputs]
    - target db object (CRUD)
    - df: pd.DataFrame - ['img_id', 'image_path', 'image_width', 'image_height',
                          'qc_id', 'qc_start_date', 'qc_score', 'object_count', 'qc_end_date', 'product_id', 'price']
    - mode: string, the mode should be one of ["img_path", "img_WH", "start_QC", "QC_score", "object_count", "end_QC", "price"]
            if mode is start_QC     : qd_status in DB becomes "QC_start"
            if mode is QC_score     : qd_status in DB becomes "QC_end"
            if mode is object_count : qd_status in DB becomes "QC_end+obj_cnt"
            if mode is end_QC       : qd_status in DB becomes "QC_end+obj_cnt+duplicate"

    [output]
    - success: 성공여부
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
        ['QC', ['qc_id', 'qc_end_date']],
        ['ProductInfo', ['product_id', 'price']]
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
    elif mode == 'price':
        idx = 6
    else: 
        print("Invalid mode is selected")
        print('The mode should be one of ["img_path", "img_WH", "start_QC", "QC_score", "object_count", "end_QC", "price"]')
    
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

def update_columns_af_duplicate(db, qc_ids):
    '''
    update columns after duplicate function,
    The default value of qc_duplicate column is 0 and if the image is overlapping, the value becomes 1

    [inputs]
    - db        : target db object (CRUD)
    - qc_ids    : list, list of the ids that overlaps 

    [output]
    - success: 성공 여부
    '''
    
    # 0. Initial Setting
    success = False 

    # 1. defining target columns
    schema_name = SCHEMA_NAME
    table_name = "QC"
    target_column = "qc_duplicate"

    # 3. update data in DB
    for id in qc_ids:
        condition = f"qc_id='{id}'"
        success = db.updateDB(schema=schema_name, table=table_name, column=target_column, value=1,condition=condition)

    return success 

def update_tx_availability (db, txp_id, flag, download_file_path):
    schema_name = SCHEMA_NAME
    table = 'transactionproduct'
    columns = ['availability',  'product_path']
    values = [flag, download_file_path]
    condition = f"txp_id={txp_id}"
    success = False
    for idx, column in enumerate(columns):
        success =  db.updateDB(schema=schema_name, table = table, column=column, value = values[idx], condition = condition)

    return success

def update_like_count(db, img_id_list):
    '''
    update like count

    [input]
    - db: db object (CRUD)
    - img_id_lis: list, list of img_ids
    [output]
    img_id_like_cnt: pd.DataFrame, column: img_id, like_count
    
    '''
    if len(img_id_list) == 0:
        return None
    elif len(img_id_list) == 1:
        condition = f"features.img_id = '{img_id_list[0]}'"
    else:
       condition = f"features.img_id in {tuple(img_id_list)}"
    data = db.readDB_with_filtering(schema = 'public', table = 'features', columns = ['img_id', 'like_cnt'], condition = condition)    

    img_id_like_cnt = pd.DataFrame(data=data, columns=['img_id', 'like_count'])
    img_id_like_cnt['like_count'] += 1

    for i in range(len(img_id_like_cnt)):
        condition_1 = f"features.img_id = '{img_id_like_cnt['img_id'].iloc[i]}'"
        db.updateDB(schema = 'public', table='features', column = 'like_cnt', value = img_id_like_cnt['like_count'].iloc[i], condition = condition_1)

    return img_id_like_cnt





###############################
######### TRANSACTION #########
###############################

def insert_tx_info(db, buyer_name, img_id_list, buyer_defined_dataset_name):
    '''
    insert 
    [inputs]
    - db          : target db object (CRUD)
    - buyer_name  : string,
    - img_id_list : list, list of img_id
    - buyer_defined_dataset_name: string, dataset_name made by buyer

    [output]
    - success: 성공 여부

    '''
    # 0. initial setting
    success = False
    schema_name = SCHEMA_NAME
    table_name = "transaction"
    tx_time = datetime.now(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')

    # 1. insert data in transactionProduct table
    success = db.insertDB(schema = schema_name, table = 'TransactionProduct', columns = ["buyer_defined_dataset_name"], data = [buyer_defined_dataset_name])
    
    last_txp_id = db.find_last_txp_id(schema_name)

    # 2. find buyer's id 
    condition_buyer = f"user_idName='{buyer_name}'"
    buyer_id = db.readDB_with_filtering(schema=schema_name, table = 'User', columns = ['user_id'], condition = condition_buyer)
    buyer_id = buyer_id[0][0]

    # 3. find seller's id 
    condition_img = f"img_id in {tuple(img_id_list)}"
    sellers = db.readDB_with_filtering(schema = schema_name, table = 'Features', columns = ['DISTINCT user_id', 'img_id', 'dataset_id'], condition = condition_img)
    df_tmp = pd.DataFrame(data = sellers, columns=['seller_id', 'img_id', 'dataset_id'])
    df_tmp2= df_tmp.groupby(['seller_id','dataset_id']).size().reset_index(name='img_id')
    seller_id_list = df_tmp['seller_id'].unique()
    sellers_dict = dict()

    # 3-b. update dataset_selction_cnt
    dataset_list = list(df_tmp2['dataset_id'].unique())

    sql = f"select * from datasetinfo d "
    data = db.execute(sql)
    ds_sel_cnt = pd.DataFrame(data=data, columns = ['dataset_id', 'dataset_name', 'dataset_description', 'dataset_selection_cnt'])
    for i, id in enumerate(dataset_list):
        value = int(ds_sel_cnt[ds_sel_cnt['dataset_id']==id]['dataset_selection_cnt'] + 1)
        sql_tmp = f"update public.datasetinfo set dataset_selection_cnt = {value} where dataset_id='{id}'"
        db.execute(sql_tmp)

    # 4. make sellers_dict {'seller_id': 'img_id'}
    for s_id in seller_id_list:
        s_img_list = list(df_tmp[df_tmp['seller_id']==s_id]['img_id'])
        sellers_dict[s_id] = f"[{', '.join(map(str, s_img_list))}]"

    # 5. calculate price
    total_price_per_dataset = _calculate_total_price_selected(db, img_id_list)
    df_tmp2 = pd.merge(df_tmp2, total_price_per_dataset, how = 'inner', on='dataset_id')

    # 6. insert data
    for seller_id in seller_id_list:
        dataset_id = df_tmp2[df_tmp2['seller_id']==seller_id]['dataset_id'].iloc[0]
        price = df_tmp2[df_tmp2['seller_id']==seller_id]['totalprice'].iloc[0]
        if price == None:
            price = 0

        data = [tx_time, buyer_id, dataset_id, sellers_dict[seller_id], seller_id, price, last_txp_id]
        target_column = ["tx_date", "buyer_id", "dataset_id", "img_id_list", "seller_id", "price", "txp_id"]
        success = db.insertDB(schema=schema_name,
                            table=table_name,
                            columns=target_column,
                            data=data)

    # 6. plus minus point 
    for seller_id in seller_id_list:
        price = df_tmp2[df_tmp2['seller_id']==seller_id]['totalprice'].iloc[0]
        if price == None:
            price = 0

        buyer_point = db.readDB_with_filtering(schema = schema_name, table = 'user', columns = ['user_point'], condition = f"user_id = '{buyer_id}'") 
        seller_point = db.readDB_with_filtering(schema = schema_name, table = 'user', columns = ['user_point'], condition = f"user_id = '{seller_id}'") 

        buyer_point = buyer_point[0][0] - price 
        seller_point = seller_point[0][0] + price

        # buyer
        db.updateDB(schema = SCHEMA_NAME, table = 'user', column = 'user_point' , value = buyer_point, condition=f"user_id = '{buyer_id}'" )
        # seller
        db.updateDB(schema = SCHEMA_NAME, table = 'user', column = 'user_point' , value = seller_point, condition=f"user_id = '{seller_id}'" )

    return success

def _calculate_total_price_selected (db, img_id_list):
    sql =  f"select f.dataset_id, sum(p.price) \
            from features f \
            left join productinfo p on p.product_id = f.product_id \
            where f.img_id in {tuple(img_id_list)} \
            group by f.dataset_id; "
    
    result = db.execute(sql)
    result_df = pd.DataFrame(data=result, columns = ['dataset_id', 'totalprice'])
    return result_df

def load_list_view_tx(db, page=1, item_per_page=10, user_idName=None):
    col = ['id', 'dataset_name', 'price_total', 'image_count',
            'avg_price_per_image','sales_count', 'like_count',
            'qc_state', 'qc_score', 'uploader', 'date', 'availability',
            'object_list', 'object_count', 'object_info_in_detail', 'product_path', 'flag']
    
    cnt_buy, df_buy = _load_list_view_tx_buyer(db, page, item_per_page, user_idName)
    col_buy = ['txp_id', 'dataset_name', 'price_total', 'image_count',
            'avg_price_per_image','sales_count', 'like_count',
            'qc_state', 'qc_score', 'uploader', 'upload_date', 'availability',
            'object_list', 'object_count', 'object_info_in_detail', 'product_path']

    if df_buy is not None:
        df_buy = df_buy[col_buy]
        df_buy['flag'] = 'buy'
    else:
        df_buy = pd.DataFrame(columns=[*col_buy, 'flag'])
    df_buy.columns = col
#    print(df_buy)

    cnt_sell, df_sell = _load_list_view_tx_seller(db, page, item_per_page, user_idName)
    col_sell = ['dataset_id', 'dataset_name', 'price_total', 'image_count',
            'avg_price_per_image', 'sales_count', 'like_count',
            'qc_state', 'qc_score', 'uploader', 'upload_date', 'availability',
            'object_list','object_count', 'object_info_in_detail', 'product_path']
    if df_sell is not None:
        df_sell = df_sell[col_sell]
        df_sell['flag'] = 'sell'
    else:
        df_sell = pd.DataFrame(columns=[*col_sell, 'flag'])
    df_sell.columns = col
#    print(df_sell)

    df_concat = pd.concat([df_buy, df_sell], axis=0)
    df_concat.columns = col

 #   print(df_concat)

    return cnt_buy+cnt_sell, df_concat

def _load_list_view_tx_buyer(db, page=1, item_per_page=10, user_idName = None):
    '''
    load_list view of transaction
    if user_idName is not None -> then returns listview for the user's uploaded dataset

    [inputs]
    - db: target db object (CRUD)
    - page: int, page number, default: 1,  if you want load 3rd page, then 3
    - item_per_page: int, default:10, the number of items per page
    - user_idName   : string, default: None, 

    [output]
    - total_count: int, the number of rows
    - selected_K_img_df: output from query, dictionary, if empty dictionary, returns None
      key: dataset_id
      values: pd.dataframe with cols = ['img_id', 'image_path', 'qc_score', 'dataset_id'
                                        'object_list', 'object_count','object_info_in_detail']  ==> PLEASE FIX
      also,
        the value of colmnn "object_list" is *list* of object 
            (e.g., ['Van','Cyclist', 'Pedestrian'])
        the value of column "object_info_in_detail" is dictinary that keys are object's name and value is its count
            (e.g., {'Cyclist': 1, 'Pedestrian': 1, 'Van': 2})
    '''
    # 1. initial setting and total rows cnt
    result = None
    item_start = 0 + item_per_page * (page - 1)
    if user_idName is not None:
        condition_id = f"where q.qc_status not in ('uploaded', 'QC_start') and u.user_idname = '{user_idName}'"
        condition_id_tmp = f"where u.user_idname = '{user_idName}'"
    else: 
        condition_id = ""
        condition_id_tmp=""

    sql = f"select t.img_id_list, t.dataset_id, u.user_idname , u2.user_idname \
            from public.transaction t \
            left join public.user u on u.user_id=t.buyer_id \
            left join public.user u2 on u2.user_id=t.seller_id {condition_id_tmp};"
    total_cnt = db.execute(sql)
    total_cnt = len(total_cnt)
    if total_cnt == 0:
        return total_cnt, None
    
    ## 1.1 find img_id_list
    sql = f"select tp.txp_id, t.img_id_list\
            from transaction t \
            left join transactionproduct tp on t.txp_id=tp.txp_id \
            left join \"user\" u on u.user_id = t.buyer_id \
            {condition_id_tmp};"
    img_id_list = db.execute(sql)
    
    # 2. make txp_id list 
    df_tmp = pd.DataFrame(data = img_id_list, columns=['txp_id', 'img_id'])

    txp_id_list = list(df_tmp['txp_id'].unique())
    txp_id_and_img_id_list = []
    # 2. Create img_ids list and randomly select K images 
    for id in txp_id_list:
        # 2-1. Create img_ids list of the dataset_id
        condition = f"dataset_id = '{id}'"
        img_ids = db.readDB_with_filtering(schema = 'public', table = 'Features', columns = ['img_id'], condition = condition)
        img_ids = list(sum(img_ids, ()))
        # 2-4. make dataset_id_and_img_id_list
        txp_id_and_img_id_list.append([id, img_ids])

    img_id_list_fin=[]
    for i in txp_id_and_img_id_list:
        img_id_list_fin = [*img_id_list_fin, *i[1]]

    # print(img_id_list_fin)

    condition_img_id_list = f"where q.qc_status not in ('uploaded', 'QC_start') and u.user_idname = '{user_idName}' and f.img_id in {tuple(img_id_list_fin)}"

    # 2. dataset information
    sql = f"select res.txp_id,\
                sum(res.price) as price_total,\
                count(res.dataset_id) as total_image_count,\
                sum(res.price) / count(res.dataset_id) as avg_price_per_image, \
                max(res.dataset_selection_cnt) as sales_count,\
                sum(res.like_cnt) as like_count, \
                res.qc_status as qc_state, \
                AVG(res.qc_score) as qc_score, \
                res.tx_date as transaction_date, \
                res.availability, res.buyer_defined_dataset_name, res.product_path \
            from( \
                select f.img_id, f.upload_date, f.like_cnt, d.*, p.*, t.tx_date, q.qc_status, q.qc_score, u2.user_idname as user_idname, u.user_idname as buyer_idname, tp.txp_id, tp.availability, tp.buyer_defined_dataset_name, tp.product_path \
                from features f \
                left join productinfo p on f.product_id =p.product_id \
                left join datasetinfo d on d.dataset_id =f.dataset_id \
                left join qc q on q.qc_id =f.qc_id \
                left join transaction t on t.dataset_id=f.dataset_id\
                left join public.user u on u.user_id=t.buyer_id \
                left join public.user u2 on u2.user_id=t.seller_id \
                left join TransactionProduct tp on tp.txp_id=t.txp_id \
                {condition_img_id_list} \
                ) res \
            group by res.txp_id, res.qc_status, res.tx_date, res.availability, res.buyer_defined_dataset_name, res.product_path \
            order by res.txp_id limit {item_per_page} offset {item_start};"

    result = db.execute(sql)
    columns = ['txp_id', 'price_total', 'image_count', 'avg_price_per_image', 'sales_count', 'like_count' ,'qc_state' ,'qc_score','upload_date', 'availability', 'dataset_name', 'product_path']
    result_df = pd.DataFrame(data = result, columns=columns)
    # print(result_df)

    to_process_qcState = list(result_df['qc_state'])

    for i in range(len(to_process_qcState)):
        if to_process_qcState[i] == 'uploaded':
            to_process_qcState[i] = 'Pending'
        elif to_process_qcState[i] == 'QC_start':
            to_process_qcState[i] = 'In Progress'
        elif to_process_qcState[i] in ('QC_end','QC_end+obj_cnt','QC_end+obj_cnt+duplicate'):
            to_process_qcState[i] = 'Done'

    result_df['qc_state'] = to_process_qcState


    # 3. object information
    ## a. df for final result and condition settting 
    df_obj_list_split_by_dataset = pd.DataFrame(columns = ['txp_id', 'object_list', 'object_count', 'object_info_in_detail'])

    target_txp_id = tuple(result_df['txp_id'])

    if len(target_txp_id) == 0:
        return result_df
    elif len(target_txp_id) == 1:
        condition = f"where dataset.dataset_id = '{target_txp_id[0]}'"
    else:
        condition = f"where dataset.dataset_id in {target_txp_id}" 
    
    ## b. excute query
    sql = f"select  res.txp_id, res.gt_object, count(res.gt_object) \
            from ( \
                select o.gt_object, g.gt_height, g.gt_width, dataset.txp_id \
                from groundtruth g  \
                left join ( \
                    select f.img_id, d.dataset_id, t.txp_id \
                    from features f \
                    left join datasetinfo d on d.dataset_id = f.dataset_id \
                    left join transaction t on t.seller_id = f.user_id \
                    left join transactionproduct tp on tp.txp_id = t.txp_id \
                ) dataset on dataset.img_id = g.img_id \
                left join public.object o on o.gt_object_id = g.gt_object_id \
                {condition} \
                group by o.gt_object, g.gt_height, g.gt_width, dataset.txp_id \
            ) res \
            group by res.txp_id, res.gt_object \
            order by res.txp_id; "    
    result_obj = db.execute(sql)
    col_obj = ['txp_id', 'gt_object', 'count']
    df_obj = pd.DataFrame(data = result_obj, columns= col_obj)
    # print(df_obj)
    
    ## c. update column dataset_ids
    df_obj_unique_dataset_id = df_obj['txp_id'].unique()
    df_obj_list_split_by_dataset['txp_id'] = list(df_obj_unique_dataset_id)
    
    ## d. update column object_count
    df_groupby1=df_obj.groupby('txp_id').sum()
    df_obj_list_split_by_dataset['object_count'] = list(df_groupby1['count'])

    ## e. update column object_list and object_info_in_detail
    tmp_list_for_detail = []
    tmp_list_for_object_list = []
    for i in df_obj_unique_dataset_id:
        df_target = df_obj[df_obj['txp_id']==i]
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

    # print(df_obj_list_split_by_dataset)

    result_df = pd.merge(result_df,
                         df_obj_list_split_by_dataset,
                         on='txp_id',
                         how='left'
                         )
    

    # 4. uploader list
    sql = f"select t.tx_id, t.seller_id, txp_id, u.user_idname from transaction t left join public.user u on u.user_id = t.seller_id"
    result = db.execute(sql)
    result_uploader_df = pd.DataFrame(data = result, columns = ['tx_id', 'seller_id', 'txp_id', 'uploader']) 

    # print(result_uploader_df)
    seller_df = pd.DataFrame(columns = ['txp_id', 'uploader'])
    id_tmp = []
    seller_tmp = []
    for i, id in enumerate(result_df['txp_id'].unique()):
        # print(i, id)
        seller_list = list(result_uploader_df[result_uploader_df['txp_id']==id]['uploader'])
        id_tmp.append(id)
        seller_tmp.append("["+", ".join(seller_list) + "]")

    seller_df['txp_id'] = id_tmp
    seller_df['uploader'] = seller_tmp

    result_df = pd.merge(result_df,
                         seller_df,
                         on= 'txp_id',
                         how='left')
    
    # dataset_list = result_df['txp_id'].unique()
    # result_dict = dict()

    # for i in dataset_list:
    #     result_dict[i] = result_df[result_df['txp_id']==i]

    return total_cnt, result_df

def _load_list_view_tx_seller(db, page=1, item_per_page=10, user_idName = None):
    '''
    load_list view of transaction
    if user_idName is not None -> then returns listview for the user's uploaded dataset

    [inputs]
    - db: target db object (CRUD)
    - page: int, page number, default: 1,  if you want load 3rd page, then 3
    - item_per_page: int, default:10, the number of items per page
    - user_idName   : string, default: None, 

    [output]
    - total_count: int, the number of rows
    - df_result: pd.DataFrame, output from query, if df_result is empty pd.DataFrame, returns None
      cols = ['dataset_id', 'dataset_name',
              'price_total', 'iamge_count', 'avg_price_per_image',
              'sales_count', 'like_count',
              'qc_state', 'qc_score', 
              'uploader', 'upload_date', availability', 'buyer_defined_dataset_name', 'product_path',
              'object_list', 'object_count','object_info_in_detail']
      also,
        the value of colmnn "object_list" is *list* of object 
            (e.g., ['Van','Cyclist', 'Pedestrian'])
        the value of column "object_info_in_detail" is dictinary that keys are object's name and value is its count
            (e.g., {'Cyclist': 1, 'Pedestrian': 1, 'Van': 2})
    '''
    # 1. initial setting and total rows cnt
    result = None
    item_start = 0 + item_per_page * (page - 1)
    if user_idName is not None:
        condition_id = f"where q.qc_status not in ('uploaded', 'QC_start') and u2.user_idname = '{user_idName}'"
        condition_id_tmp = f"where u2.user_idname = '{user_idName}'"
    else: 
        condition_id = ""
        condition_id_tmp=""

    sql = f"select t.img_id_list, t.dataset_id, u.user_idname , u2.user_idname \
            from public.transaction t \
            left join public.user u on u.user_id=t.buyer_id \
            left join public.user u2 on u2.user_id=t.seller_id {condition_id_tmp};"
    total_cnt = db.execute(sql)
    total_cnt = len(total_cnt)
    if total_cnt == 0:
        return total_cnt, None

    # 2. dataset information
    sql = f"select res.dataset_id, res.dataset_name,\
                sum(res.price) as price_total,\
                count(res.dataset_id) as total_image_count,\
                sum(res.price) / count(res.dataset_id) as avg_price_per_image, \
                max(res.dataset_selection_cnt) as sales_count,\
                sum(res.like_cnt) as like_count, \
                res.qc_status as qc_state, \
                AVG(res.qc_score) as qc_score, \
                res.user_idname as uploader, \
                res.upload_date as upload_date, \
                res.availability, res.buyer_defined_dataset_name, res.product_path \
            from( \
                select f.img_id, f.upload_date, f.like_cnt, d.*, p.*, q.qc_status, q.qc_score, u2.user_idname as user_idname, u.user_idname as buyer_idname, tp.availability, tp.buyer_defined_dataset_name, tp.product_path \
                from features f \
                left join productinfo p on f.product_id =p.product_id \
                left join datasetinfo d on d.dataset_id =f.dataset_id \
                left join qc q on q.qc_id =f.qc_id \
                left join transaction t on t.dataset_id=f.dataset_id\
                left join public.user u on u.user_id=t.buyer_id \
                left join public.user u2 on u2.user_id=t.seller_id \
                left join TransactionProduct tp on tp.txp_id=t.txp_id \
                {condition_id} \
                ) res \
            group by res.dataset_id, res.dataset_name, res.qc_status, res.user_idname, res.upload_date, res.availability, res.buyer_defined_dataset_name, res.product_path \
            order by res.dataset_id limit {item_per_page} offset {item_start};"

    result = db.execute(sql)
    columns = ['dataset_id', 'dataset_name', 'price_total', 'image_count', 'avg_price_per_image', 'sales_count', 'like_count' ,'qc_state' ,'qc_score', 'uploader' ,'upload_date', 'availability', 'buyer_defined_dataset_name', 'product_path']
    df_result = pd.DataFrame(data = result, columns=columns)

    to_process_qcState = list(df_result['qc_state'])

    for i in range(len(to_process_qcState)):
        if to_process_qcState[i] == 'uploaded':
            to_process_qcState[i] = 'Pending'
        elif to_process_qcState[i] == 'QC_start':
            to_process_qcState[i] = 'In Progress'
        elif to_process_qcState[i] in ('QC_end','QC_end+obj_cnt','QC_end+obj_cnt+duplicate'):
            to_process_qcState[i] = 'Done'

    df_result['qc_state'] = to_process_qcState

    target_dataset_id = tuple(df_result['dataset_id'])
    
    # 3. object information
    ## a. df for final result and condition settting 
    df_obj_list_split_by_dataset = pd.DataFrame(columns = ['dataset_id', 'object_list', 'object_count', 'object_info_in_detail'])

    if len(target_dataset_id) == 0:
        return df_result
    elif len(target_dataset_id) == 1:
        condition = f"where dataset.dataset_id = '{target_dataset_id[0]}'"
    else:
        condition = f"where dataset.dataset_id in {target_dataset_id}" 
    
    ## b. excute query
    sql = f"select  res.dataset_id, res.gt_object, count(res.gt_object) \
            from ( \
                select o.gt_object, g.gt_height, g.gt_width, dataset.dataset_id \
                from groundtruth g  \
                left join ( \
                    select f.img_id, d.dataset_id \
                    from features f \
                    left join datasetinfo d on d.dataset_id = f.dataset_id \
                    left join qc q on q.qc_id =f.qc_id \
                    where q.qc_status not in ('uploaded', 'QC_start') \
                ) dataset on dataset.img_id = g.img_id \
                left join public.object o on o.gt_object_id = g.gt_object_id \
                {condition} \
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

    return total_cnt, df_result       

def create_download_file(db, txp_id):
    '''
    다운로드할 파일 추출
    [inputs]
    - db          : target db object (CRUD)
    - txp_id : list, list of img_id

    [output]
    - df_ft : features to download, pd.DataFrame
    - df_gt : groundtruth to download, pd.DataFrame
    - df_pt : image_path to download, pd.DataFrame
    - dataset_name : dataset_name, string
    '''

    sql1 = f"select img_id_list from public.transaction t where t.txp_id={txp_id};"
    data = db.execute(sql1)
    result_df = pd.DataFrame(data = data, columns=['img_id_list'])

    img_id_list = []
    for i in range(len(result_df)):
        tmp = result_df['img_id_list'].iloc[i]
        tmp = eval(tmp)
        img_id_list = [*img_id_list, *tmp]

    sql2 = f"select buyer_defined_dataset_name from public.transactionproduct tp where tp.txp_id={txp_id};"
    dataset_name = db.execute(sql2)
    dataset_name = dataset_name[0][0]

    df_ft, df_gt, df_pt = _create_download_file(db, img_id_list)

    return df_ft, df_gt, df_pt, dataset_name


def _create_download_file (db, img_id_list):
    '''
    다운로드할 파일 추출
    [inputs]
    - db          : target db object (CRUD)
    - img_id_list : list, list of img_id

    [output]
    - df_ft : features to download, pd.DataFrame
    - df_gt : groundtruth to download, pd.DataFrame
    - df_pt : image_path to download, pd.DataFrame
    '''
    # 0. initial setting
    schema_name = SCHEMA_NAME
        
    col_ft = ALL_COLUMNS[5]
    sql_ft = f"select * from {schema_name}.features f where f.img_id in {tuple(img_id_list)};"
    res_ft = db.execute(sql_ft)
    df_ft = pd.DataFrame(data=res_ft, columns=col_ft)
    target_col_ft = ['image_path', 'image_width', 'image_height', 'upload_date',
       'lat', 'lon', 'alt', 'roll', 'pitch', 'yaw', 'velo_north', 'velo_east',
       'velo_forward', 'velo_leftward', 'velo_upward', 'accel_x', 'accel_y',
       'accel_z', 'accel_forward', 'accel_leftward', 'accel_upward', 'ang_x',
       'ang_y', 'ang_z', 'ang_forward', 'ang_leftward', 'ang_upward',
       'pos_accuracy', 'vel_accuracy', 'navstat', 'numsats', 'posmode',
       'velmode', 'orimode']
    
    df_pt = df_ft['image_path']
    df_tmp3 = df_ft[['image_path', 'img_id']]
    df_ft = df_ft[target_col_ft]

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
       'gt_amt_border_kf', 'qc_score', 'object_count']

    df_gt = df_gt[target_col_gt]

    return df_ft, df_gt, df_pt


##########################
######### DELETE #########
##########################


def delete_dataset(db, dataset_id):
    schema = SCHEMA_NAME
    table = 'features'
    condition = f"features.dataset_id={dataset_id}"
    success = db.updateDB(schema=schema, table=table, column='not_show', value=True, condition=condition)

    return success 


def find_img_id_with_dataset_id(db, list_of_dataset_id):
    if len(list_of_dataset_id) == 0:
        condition = ""
    elif len(list_of_dataset_id) == 1:
        condition = f"where f.dataset_id = '{list_of_dataset_id[0]}'"
    else:
        condition = f"where f.dataset_id in {tuple(list_of_dataset_id)}"
    sql = f"select f.img_id, f.dataset_id from features f {condition};"
    data = db.execute(sql)
    dataset_id_with_img_id = pd.DataFrame(data=data, columns=['dataset_id', 'img_id'])

    return dataset_id_with_img_id


