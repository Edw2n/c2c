from dbmanager.configs import SCHEMA_NAME, TABLE_NAME

def crud_basic_ex(db):
    # crud basic examples
    schema_name = SCHEMA_NAME
    table_name = TABLE_NAME

    db.insertDB(schema=schema_name, table=table_name, columns=["Name", "Age"], data=["Eunsu", 25])
    db.insertDB(schema=schema_name, table=table_name, columns=["Name", "Age"], data=["Joopyo", 30])
    db.insertDB(schema=schema_name, table=table_name, columns=["Name", "Age"], data=["Edw2n", 25])
    print(db.readDB(schema=schema_name, table=table_name, columns=["Name"]))

    db.updateDB(schema=schema_name, table=table_name, column="Name", value="Shurul",condition="Age=25")
    print(db.readDB(schema=schema_name, table=table_name, columns=["Name", "Age"]))

    db.deleteDB(schema=schema_name, table=table_name, condition ="Age != 30")
    print(db.readDB(schema=schema_name, table=table_name, columns=["Name"]))