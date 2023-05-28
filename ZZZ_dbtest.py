from dbmanager.crud import CRUD
from dbmanager.configs import POSTGRES_CONFIG, SCHEMA_NAME, TABLE_NAME, ALL_COLUMNS
from dbmanager.utils import initialize_db_structures


#######################
# This is just for test
# made by JP 
########################

if __name__ == "__main__":
    db = CRUD(POSTGRES_CONFIG)
    reset_flag = False
    initialize_db_structures(db=db, reset_flag=reset_flag)

    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME
    column_list = ALL_COLUMNS
    num_table = len(table_name)

    '''
    for i in range(num_table):
        db.drop_table(schema_name, table_name[i])
        db.create_table(schema_name, table_name[i], ALL_COLUMNS_INFO[i])

    for i in range(num_table):
        db.addPK(schema_name, table_name[i], PK_LIST[i])

    for i in range(len(FK_LIST)):
        db.addFK(schema = schema_name,
                 table_PK=FK_LIST[i][0], 
                 column_PK=FK_LIST[i][1],
                 table_FK=FK_LIST[i][2],
                 column_FK=FK_LIST[i][3])
    '''
    ### CREATE gt_ID needed
    if reset_flag:
        db.insertDB(schema = schema_name,
                    table = table_name[0],
                    columns = column_list[0], 
                    data = [1, 1,"Van",0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1])
        db.insertDB(schema = schema_name,
                    table = table_name[0],
                    columns = column_list[0], 
                    data = [2, 2,"Car",0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2])
        db.insertDB(schema = schema_name,
                    table = table_name[0],
                    columns = column_list[0], 
                    data = [3, 3,"Cyclist",0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2])
        print(db.readDB(schema=schema_name, table=table_name[0], columns=["gt_id", "gt_object"]))

        db.updateDB(schema=schema_name, table=table_name[0], column="gt_object", value="Bus",condition="gt_object='Car'")
        print(db.readDB(schema=schema_name, table=table_name[0], columns=["gt_id", "gt_object"]))

        db.deleteDB(schema=schema_name, table=table_name[0], condition ="gt_object='Bus'")
        print(db.readDB(schema=schema_name, table=table_name[0], columns=["gt_id", "gt_object"]))



