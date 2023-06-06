from sre_constants import SUCCESS
from dbmanager.database import PostgrestDB

class CRUD(PostgrestDB):

    def create_table(self, schema, table, columns_info):
        '''
        columns_info대로 컬럼을 가지는 schema.table을 생성

        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string
        - columns_info : 컬럼 정보, dictionary { "컬럼명" : "타입정보" } 

        [output]
        - success : create 문 실행 결과 (테이블 생성 여부) , bool
        '''
        
        result = []
        success = False

        assert schema is not None, "schema is not allowed None!"
        assert table is not None, "table is not allowed None!"
        assert columns_info is not None, "column is not allowed None!"

        search_sql = f"SELECT COUNT(*) FROM pg_tables WHERE schemaname='{schema}' AND tablename='{table}';"
        schema_table = ".".join([schema, table])

        try:
            result = self.execute(search_sql, "Check Table")
        except Exception as e:
            print("Error Occured in Search Schema!", e)
            return result
        
        if result and result[0][0] > 0: #격하게 고치고 싶다
            print("Table is already exist!")
            success = True
            return success
        
        schema_table = ".".join([schema, table])
        columns = ", ".join([f"{k} {v}" for k,v in columns_info.items()])

        create_sql = "CREATE TABLE {schema_table} ({columns});".format(schema_table=schema_table, columns=columns)
        
        try:
            self.execute(create_sql, "Create Table")
            self.db.commit()
            success = True
            print(f'Table {schema_table} is created')
        except Exception as e :
            print(" create DB err ",e) 
        return success
    
    def drop_table(self, schema, table):
        '''
        해당 table을 제거

        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string

        [output]
        - success : drop 문 실행 결과 (테이블 제거 여부) , bool
        '''
        success = False
        schema_table = ".".join([schema, table])
        sql = "DROP TABLE IF EXISTS {schema_table} CASCADE;".format(schema_table=schema_table)
        
        try:
            self.execute(sql, "Drop Table")
            self.db.commit()
            success = True
            print(f'Table {schema_table} is dropped')
        except Exception as e :
            print(" create DB err ",e) 
        return success

    def insertDB(self, schema, table, columns, data):
        '''
        schema.table에 column 추가 (data 대로)

        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string
        - columns_info : 컬럼 정보, dictionary { "컬럼명" : "타입정보" } 
        - data : columns 데이터 타입에 각각 순서대로 매핑 되는 데이터 리스트, list of variable values

        [output]
        - success : insert 문 실행 성공 여부, bool
        '''

        success = False

        #TODO Insert Query문에 맞게 필요한 Assert 문 작성할 것

        assert schema is not None, "schema is not allowed None!"
        assert table is not None, "table is not allowed None!"
        assert columns is not None, "column is not allowed None!"
        assert data is not None, "data is not allowed None!"
        assert len(columns) == len(data), f"the number of data should be {len(columns)}, but it is {len(data)}"       
        columns = ", ".join(columns)

        data = ', '.join(["'%s'" % x if isinstance(x, str) else str(x) for x in data]) # 아마 string 아니라서 매핑 해줘야 할듯 걍 해도 될지도..?

        sql = f" INSERT INTO {schema}.{table} ({columns}) VALUES ({data}) ;"

        try:
            self.execute(sql, "INSERT ROW")
            self.db.commit()
            success = True
            # print(f'Inserting data into {schema}.{table} is successfully done')
        except Exception as e :
            print(" insert DB err ",e) 
        
        return success

    def readDB(self, schema, table, columns):
        '''
        schema.table에 columns 에 해당하는 열들 다 읽어옴

        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string
        - columns : 컬럼명 list , a list of strings

        [output]
        - result : 읽어온 결과, a list of row(tuple)
        (read db error => return None)
        '''
        
        #TODO READ Query문에 맞게 필요한 Assert 문 작성할 것
        assert schema is not None, "schema is not allowed None!"
        assert table is not None, "table is not allowed None!"
        assert columns is not None, "column is not allowed None!"

        result = None

        columns = ", ".join(columns)
        sql = f" SELECT {columns} from {schema}.{table} ;"

        try:
            result = self.execute(sql)
        except Exception as e :
            print(" read DB err",e)
        
        return result
    
    def readDB_with_filtering(self, schema, table, columns, condition):
        '''
        schema.table에 columns 에 해당하는 열들 중 조건에 맞는 열을 읽어옴

        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string
        - columns : 컬럼명 list , a list of strings
        - condition: string, where 에 들어갈 조건

        [output]
        - result : 읽어온 결과, a list of row(tuple)
        (read db error => return None)
        '''
        
        assert schema is not None, "schema is not allowed None!"
        assert table is not None, "table is not allowed None!"
        assert columns is not None, "column is not allowed None!"

        result = None

        columns = ", ".join(columns)
        sql = f" SELECT {columns} FROM {schema}.{table} WHERE {condition};"

        try:
            result = self.execute(sql)
        except Exception as e :
            print(" read DB err",e)
        
        return result
    
    def readDB_join_filtering(self, schema, table, columns, join, condition):
        '''
        schema.table을 join하여 columns 에 해당하는 열들 중 조건에 맞는 열을 읽어옴

        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string
        - columns : 컬럼명 list , a list of strings
        - join: join할 list, (2D list)
            e.g., join = [["LEFT JOIN", "table1", "table2", "id_1", "id_2"], 
                          ["INNER JOIN", "table2", "table3", "id_2", "id_3"], 
                          ["RIGHT JOIN", "table3", "table4", "id_3", "id_4"], 
                          ["OUTER JOIN", "table4", "table5", "id_4", "id_5"]
                         ]

        - condition: string, where 에 들어갈 조건

        [output]
        - result : 읽어온 결과, a list of row(tuple)
        (read db error => return None)
        '''
        
        assert schema is not None, "schema is not allowed None!"
        assert table is not None, "table is not allowed None!"
        assert columns is not None, "column is not allowed None!"
        assert join is not None, "join option is not allowed None!"

        result = None
        
        join_string = ""
        for target in join:
            join_tmp = f"{target[0]} {target[2]} ON {target[1]}.{target[3]}={target[2]}.{target[4]}"
            join_string = join_string + " " + join_tmp

        columns = ", ".join(columns)
        sql = f" SELECT {columns} FROM {schema}.{table} {join_string} WHERE {condition};"

        try:
            result = self.execute(sql)
        except Exception as e :
            print(" read DB err",e)
        
        return result

    def updateDB(self, schema, table, column, value, condition):
        '''
        schema.table에 condition을 만족하는 row에 한해 column을 다 value로 update
        
        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string
        - column : 컬럼명 , string
        - value : 바꿀 값, column에 해당하는 타입 변수
        - condition : update 대상을 찾는 조건, string

        [output]
        - success : update 문 실행 성공 여부, bool
        '''

        #TODO update Query문에 맞게 필요한 Assert 문 작성할 것
        assert schema is not None, "schema is not allowed None!"
        assert table is not None, "table is not allowed None!"
        assert column is not None, "column is not allowed None!"
        assert value is not None, "column is not allowed None!"

        success = False
        
        
        sql = f" UPDATE {schema}.{table} SET {column}='{value}' WHERE {condition} ;"

        try :
            self.execute(sql)
            self.db.commit()
            success = True
        except Exception as e :
            print(" update DB err",e)
        
        return success

    def deleteDB(self,schema,table,condition):
        '''
        schema.table에 condition을 만족하는 row를 삭제
        
        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string
        - condition : 삭제 대상을 찾는 조건, string
       
        [output]
        - success : delete 문 실행 성공 여부, bool
        '''
        
        #TODO delete Query문에 맞게 필요한 Assert 문 작성할 것
        success = False

        sql = f" DELETE FROM {schema}.{table} WHERE {condition} ; "
        try :
            self.execute(sql)
            self.db.commit()
            success = True
        except Exception as e:
            print( "delete DB err", e)
        
        return success
    

    def addPK(self, schema, table, column):
        '''
        table에 PK 추가
        
        [input]
        - schema : 스키마 명, string
        - table : 테이블 명, string
        - column : PK로 설정할 칼럼, string
       
        [output]
        - success : delete 문 실행 성공 여부, bool
        '''

        success = False

        sql = f"ALTER TABLE {schema}.{table} ADD PRIMARY KEY ({column}); "
        try :
            self.execute(sql)
            self.db.commit()
            success = True
        except Exception as e:
            print( "PK gen err", e)
        
        return success


    def addFK(self, schema, table_PK, column_PK, table_FK, column_FK):
        '''
        schema.table에 condition을 만족하는 row를 삭제
        
        [input]
        - schema : 스키마 명, string
        - table_PK : PK를 가지고 있는 테이블 명, string
        - column_PK: PK에 해당하는 칼럼명
        - table_FK : FK를 설정할 테이블 명, string
        - column_FK: FK에 해당하는 칼럼명

        [output]
        - success : delete 문 실행 성공 여부, bool
        '''

        success = False

        sql = f"ALTER TABLE {schema}.{table_FK} ADD FOREIGN KEY ({column_FK}) REFERENCES {schema}.{table_PK} ({column_PK}); "
        try :
            self.execute(sql)
            self.db.commit()
            success = True
            print(f"Adding FK {table_FK}.{column_FK} is successfully done")
        except Exception as e:
            print( "FK gen DB err", e)
        
        return success
    
    def find_last_img_id(self, schema):
        '''
        마지막 img_id를 찾는 함수
        
        [input]
        - schema : 스키마 명, string
 
        [output]
        - 결과: 실형 성공 여부
        '''

        result = 0

        sql = f"select img_id from {schema}.features order by img_id desc limit 1;"
        try :
            result = self.execute(sql)
            if not result:
                result = 0
            else: result = result[0][0]
        except Exception as e:
            print( "img_id err", e)
        
        return result

