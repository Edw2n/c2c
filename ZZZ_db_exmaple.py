from dbmanager.crud import CRUD
from dbmanager.configs import POSTGRES_CONFIG, SCHEMA_NAME, TABLE_NAME, ALL_COLUMNS
from dbmanager.utils import initialize_db_structures, insert_user, insert_draft_dataset, \
    load_list_view, update_multiple_columns, update_columns_af_duplicate, _sampling_image
import pandas as pd
import numpy as np

#######################
# This is just for test
# made by JP 
########################

if __name__ == "__main__":
    db = CRUD(POSTGRES_CONFIG)
    initialize_db_structures(db=db)

    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME
    column_list = ALL_COLUMNS
    num_table = len(table_name)

    #### FOR TEST ONLY ####
    testers = [["jeongsik", "123"],
               ["tester", "123"],
               ["SeongGu", "123"]]
    for tester in testers:
        insert_user(db = db, user_idname=tester[0], user_password=tester[1])
    #### FOR TEST ONLY ####

    max_page, list_view = load_list_view(db=db, page=1, item_per_page=2)
    print("# of max page: ", max_page)
    print(list_view)
    print()


    unzipped_dataset_info = {"PATH": '../../04_sampledata/',
                             "USER_NAME": 'tester',
                             "PW": '123',
                             "TITLE": 'kitti_1',
                             "DESCRIPTIONS": "kitti_1_description"}
    
    inserted_info1 = insert_draft_dataset(db=db, unzipped_dataset_info=unzipped_dataset_info)

    unzipped_dataset_info = {"PATH": '../../04_sampledata/',
                             "USER_NAME": 'SeongGu',
                             "PW": '123',
                             "TITLE": 'kitti_2',
                             "DESCRIPTIONS": "kitti_1_description"}

    inserted_info2 = insert_draft_dataset(db=db, unzipped_dataset_info=unzipped_dataset_info)

    #### FOR TEST ONLY #### -> ADDING dataset sold count
    db.updateDB(schema=schema_name, table='DatasetInfo', column='dataset_selection_cnt', value=10, condition="dataset_id=1")
    #### FOR TEST ONLY ####

    max_page, list_view_default_result = load_list_view(db=db, page=1, item_per_page=2)
    print("# of max page: ", max_page)
    print(list_view_default_result)
    print()

    ########################################
    #### Testing load_list_view_default ####
    ########################################

    #### FOR TEST ONLY #### 
    cols = ['img_id', 'image_path', 'image_width', 'image_height',
        'qc_id', 'qc_start_date', 'qc_score', 'object_count', 'qc_end_date']
    data = [[1, 'path_1', 12, 13, 1, '2023-05-01 11:11:11', 12, 13, '2023-05-01 22:22:22'], 
            [2, 'path_2', 22, 23, 2, '2023-05-02 11:11:11', 22, 23, '2023-05-02 22:22:22'],
            [3, 'path_3', 32, 33, 3, '2023-05-03 11:11:11', 32, 33, '2023-05-03 22:22:22']
           ]
    df = pd.DataFrame(data=data, columns=cols)    
    #### FOR TEST ONLY ####
    mode_list= ["img_path", "img_WH", "start_QC", "QC_score", "object_count", "end_QC"]
    for i in range(6):
        update_multiple_columns(db, df, mode = mode_list[i])

    max_page, list_view = load_list_view(db=db, page=1, item_per_page=2)
    print("# of max page: ", max_page)
    print(list_view)
    print()


    max_page, list_view = load_list_view(db=db, page=2, item_per_page=2)
    print("# of max page: ", max_page)
    print(list_view)
    print()

    max_page, list_view_default_result = load_list_view(db=db, page=1, item_per_page=1, user_idName = 'SeongGu')
    print("# of max page: ", max_page)
    print(list_view_default_result)
    print()


    #############################################
    #### Testing update_columns_af_duplicate ####
    #############################################

    #### FOR TEST ONLY #### 
    overlapping_ids = [i+32 for i in range(31)]
    #### FOR TEST ONLY ####
    update_columns_af_duplicate(db, qc_ids = overlapping_ids)

    #### FOR TEST ONLY #### 
    sampled = _sampling_image(db, list_view_default_result, K=2)
#    print(sampled)
    #### FOR TEST ONLY #### 




    ##########################################
    #### Testing db.readDB_join_filtering ####
    ##########################################

    #### FOR TEST ONLY #### 
    join = [["LEFT JOIN", table_name[5], table_name[2], "qc_id", "qc_id"]]
    condition = "dataset_id='1'"

    result = db.readDB_join_filtering(schema = schema_name, table = table_name[5], columns = "*", join = join, condition = condition)
    #print(result)
    # print(result[0])
    #### FOR TEST ONLY #### 