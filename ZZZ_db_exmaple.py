from dbmanager.crud import CRUD
from dbmanager.configs import POSTGRES_CONFIG, SCHEMA_NAME, TABLE_NAME, ALL_COLUMNS
from dbmanager.utils import initialize_db_structures, insert_user, insert_draft_dataset, load_list_view_default
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

    # Just check 
    tmp_info = {"PATH": '../../04_sampledata/',
                "USER_NAME": 'jeongsik',
                "PW": '123',
                "TITLE": 'test'}
    insert_user(db = db, unzipped_dataset_info=tmp_info)
    ###########

    unzipped_dataset_info = {"PATH": '../04_sampledata/',
                             "USER_NAME": 'tester',
                             "PW": '123',
                             "TITLE": 'kitti_1'}
    
    inserted_info1 = insert_draft_dataset(db=db, unzipped_dataset_info=unzipped_dataset_info)

    unzipped_dataset_info = {"PATH": '../04_sampledata/',
                             "USER_NAME": 'SeongGu',
                             "PW": '123',
                             "TITLE": 'kitti_2'}


    inserted_info2 = insert_draft_dataset(db=db, unzipped_dataset_info=unzipped_dataset_info)

    # print(inserted_info1)
    # print()
    # print()
    # print(inserted_info2.head(62))

    list_view_default_result = load_list_view_default(db=db)
    print(list_view_default_result)
