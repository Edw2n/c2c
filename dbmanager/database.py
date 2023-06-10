import psycopg2
from datetime import datetime
from pytz import timezone
import os

class PostgrestDB():
    def __init__(self, db_config):
        self.db_config = db_config
        # connect flask - postgresql => db object
        self.db = psycopg2.connect(
            host=db_config["C2C_HOST"],
            dbname=db_config["C2C_DB"],
            user=db_config["C2C_USER"],
            password=db_config["C2C_PASSWORD"],
            port=db_config["C2C_PORT"],
            )

        # db cursor    
        self.cursor = self.db.cursor()

    def __del__(self): 
        # unlock resource assign
        self.db.close()
        self.cursor.close()
        print("db 가 닫힙니당")

    def execute(self,query,args={}):
        '''
        execute query (excute many 쓰면 query 여러개됨) 

        [input]
        query: string,
        args: values for query string (formatting 형태일떄), dictionary

        [output]
        rows = query 실행 후 결과 전체 row
        '''

        self.cursor.execute(query, args)

        # fetch 할게 없을수 있음
        try:
            rows = self.cursor.fetchall()
        except Exception as e:
            # print("fetch exception handling:", e)
            rows = []
        return rows

    def commit(self):
        ''' All the changes you perform are staged until you commit them 
        to the database with cursor.commit(). This allows you to perform 
        multiple queries at once and automatically roll back the changes
        if one of them fails.'''
        
        self.cursor.commit()