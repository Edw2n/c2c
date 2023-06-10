from dbmanager.crud import CRUD
from dbmanager.configs import POSTGRES_CONFIG, SCHEMA_NAME, TABLE_NAME, ALL_COLUMNS
from dbmanager.utils import initialize_db_structures, insert_user, insert_draft_dataset, identify_user, \
    load_list_view, update_multiple_columns, update_columns_af_duplicate, load_detailed_view, load_list_view_search, \
    insert_tx_info, load_list_view_tx_buyer, load_list_view_tx_seller, create_download_file, update_tx_availability, \
    copy_db, restore_db, get_user_point
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


    flag = identify_user(db, "jeongsik", '123', 'login' )
    print(flag)


    flag = identify_user(db, "jeongsik1", '123', 'upload' )
    print(flag)

    flag = identify_user(db, "jeongsik1", '123', 'login' )
    print(flag)


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

    print(inserted_info2)

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
            'qc_id', 'qc_start_date', 'qc_score', 'object_count', 'qc_end_date', 'product_id', 'price']
    data = [[1, 'path_1', 12, 13, 1, '2023-05-01 11:11:11', 12, 13, '2023-05-01 22:22:22', 1, 1000], 
            [2, 'path_2', 22, 23, 2, '2023-05-02 11:11:11', 22, 23, '2023-05-02 22:22:22', 2, 2000],
            [3, 'path_3', 32, 33, 3, '2023-05-03 11:11:11', 32, 33, '2023-05-03 22:22:22', 3, 3000],
            [40, 'path_3', 42, 43, 40, '2023-05-03 11:11:11', 42, 43, '2023-05-03 22:22:22', 40, 40000],

           ]
    df = pd.DataFrame(data=data, columns=cols)    
    #### FOR TEST ONLY ####
    mode_list= ["img_path", "img_WH", "start_QC", "QC_score", "object_count", "end_QC", "price"]
    for i in range(len(mode_list)):
        update_multiple_columns(db, df, mode = mode_list[i])

    max_page, list_view = load_list_view(db=db, page=1, item_per_page=2)
    print("# of max page: ", max_page)
    print(list_view)
    print()


    max_page, list_view = load_list_view(db=db, page=2, item_per_page=2)
    print("# of max page: ", max_page)
    print(list_view)
    print()

    max_page, list_view = load_list_view(db=db, page=1, item_per_page=1, user_idName = 'SeongGu')
    print("# of max page: ", max_page)
    print(list_view)
    print()


    #############################################
    #### Testing detailed list view ####
    #############################################

    #### FOR TEST ONLY #### 
    overlapping_ids = [i+32 for i in range(31)]
    #### FOR TEST ONLY ####
    update_columns_af_duplicate(db, qc_ids = overlapping_ids)

    max_page, list_view_test = load_list_view(db=db, page=1, item_per_page=10)
    print("# of max page: ", max_page)
    print(list_view_test[list_view_test['dataset_id']==2])
    print()
    #test = list_view_test[list_view_test['dataset_id']==2]
    test = list_view_test

    #### FOR TEST ONLY #### 

    print('--------------detailed_view--------------')
    detailed_view, all_data= load_detailed_view(db, test, K=10)
    print(detailed_view)
    print()
    print(all_data)
    #### FOR TEST ONLY #### 

    ######################################
    ### Testing load_list_view_search ####
    ######################################

    print()
    print('--------------search_view--------------')
    condition_filter = {
    "BASIC_INFO": 'asdasdasdasd', 
    "QUALITY_INFO": {"qc_state": ['Done'],
                     "qc_score": ['Low', 'Medium','High'],
                     "objects": ['Car','Truck','Pedestrian', 'Sitter', 'Cyclist', 'Tram', 'Misc']
                    },
    "SENSOR_INFO": {"roll": (1,1), "pitch": (3,4), "yaw": (5,6),
                    "wx": (7,8), "wy": (9,10), "wz": (11,12),
                    "vf": (13,14), "vl": (15,16), "vu": (17,18),
                    "ax": (19,20), "ay": (21,22), "az": (23,24)
                   },
    "CUSTOM_FILTERING": "asdasdasd",
    }

    condition_filter = {
    "QUALITY_INFO": {"qc_state": ['Done'], 
                     "objects": ['Car','Truck','Pedestrian', 'Sitter', 'Tram', 'Misc']},
    "SENSOR_INFO": {"roll": ('null',1), "pitch": (-1,'null'), "yaw": (-2,1),
                   },
    "CUSTOM_FILTERING": "asdasdasd",
    }


    max_page_num, result = load_list_view_search(db, condition_filter, page=1, item_per_page=10, user_idName = None)
    print(max_page_num, result)

    # print()
    # print('--------------readDB_join_filtering--------------')

    ##########################################
    #### Testing db.readDB_join_filtering ####
    ##########################################

    #### FOR TEST ONLY #### 
    # join = [["LEFT JOIN", table_name[5], table_name[2], "qc_id", "qc_id"]]
    # condition = "dataset_id='1'"

    # result = db.readDB_join_filtering(schema = schema_name, table = table_name[5], columns = "*", join = join, condition = condition)
    # print(result)
    # print(result[0])
    #### FOR TEST ONLY #### 


    ################################
    #### Testing insert_tx_info ####
    ################################

    buyer_id = 'jeongsik'
    img_id_list = [1,3,5,7,9,40,45]
    buyer_defined_dataset_name = 'jeongsik'
    insert_tx_info(db, buyer_id, img_id_list, buyer_defined_dataset_name)

    copy_db(db)
    restore_db(db)


    ###################################
    #### Testing load_list_view_tx ####
    ###################################

    print("------- load_list_view_tx -------")
    print("seller is jeongsik, the output should be None, 0")
    page_num, result = load_list_view_tx_seller(db, page=1, item_per_page=10, user_idName = 'jeongsik')
    print(page_num)
    print(result)
    print()

    print("seller is tester")
    page_num, result = load_list_view_tx_seller(db, page=1, item_per_page=10, user_idName = 'tester')
    print(page_num)
    print(result)
    print()

    print("seller is SeongGu")
    page_num, result = load_list_view_tx_seller(db, page=1, item_per_page=10, user_idName = 'SeongGu')
    print(page_num)
    print(result)
    print(result.columns)
    print()

    user_point = get_user_point(db, 'jeongsik')
    print(user_point)

    print("buyer is Jeongsik")
    page_num, result = load_list_view_tx_buyer(db, page=1, item_per_page=10, user_idName = 'jeongsik')
    print(page_num)
    print(result)
    print(result[1].columns)
    print()



    print("------- create_download_file -------")

    df_ft, df_gt, df_pt = create_download_file(db, img_id_list)


    print("------- update_tx_availabilty -------")
    txp_id = 1
    flag = True
    downlaod_file_path = "./tmp.zip"
    update_tx_availability(db, txp_id, flag, downlaod_file_path)
