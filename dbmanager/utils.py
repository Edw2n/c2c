from dbmanager.configs import USER_COLUMNS_INFO, SCHEMA_NAME, TABLE_NAME

# for Austin

def initialize_db_strucutres(db):
    '''
    db 초기 구조 잡는 함수 (table 생성, key 지정 등)

    [input]
    - db : target db object (CRUD)

    [output]
    - success : initalize 성공여부
    '''

    #지금은 스키마만 있는상태에서 만드는건데, 아예 스키마 존재하면 삭제하고 스키마 생성후 주루룩 하는거도 괜찮아 보임

    success = False

    # create table public.user
    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME
    success = db.create_table(schema_name, table_name, USER_COLUMNS_INFO)

    return success

def insert_upload_dataset(db, data):
    # data spec 보고 interface 업뎃할 예정
    pass

def read_user_query(db, filter_info):
    # user query spec 보고 interface 업뎃할 예정
    pass

# 더 추가하면 됨