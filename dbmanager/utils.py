from dbmanager.crud import CRUD
from dbmanager.configs import SCHEMA_NAME, TABLE_NAME, POSTGRES_CONFIG, ALL_COLUMNS_INFO, PK_LIST, FK_LIST

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
        success = db.addPK(schema_name, table_name[i], pk_list[i])

    for i in range(len(fk_list)):
        success = db.addFK(schema = schema_name,
                        table_PK=fk_list[i][0], 
                        column_PK=fk_list[i][1],
                        table_FK=fk_list[i][2],
                        column_FK=fk_list[i][3])
    #지금은 스키마만 있는상태에서 만드는건데, 아예 스키마 존재하면 삭제하고 스키마 생성후 주루룩 하는거도 괜찮아 보임

    return success

def insert_upload_dataset(db, data):
    # data spec 보고 interface 업뎃할 예정
    pass

def read_user_query(db, filter_info):
    # user query spec 보고 interface 업뎃할 예정
    pass

# 더 추가하면 됨