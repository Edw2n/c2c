from dbmanager.utils import load_list_view, load_detailed_view
import pandas as pd
import os

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
DATASET_LISTVIEW_SPEC = FILE_DIR + "/specs/dataset_listview_spec.csv"
DETAIL_LISTVIEW_SPEC = FILE_DIR + "/specs/detail_listview_column_spec.csv"

class ReadManager():
    '''
    support search pipeline (db->server)
    '''

    def __init__(self, db, db2_front_dataset_spec=None, db2_front_detail_spec=None ):
        '''
        [input]
        - db2_front_spec: db2fornt spec file path(csv), str
        '''
        self.db = db
        
        # spec match db to front (dataset listview)
        if db2_front_dataset_spec:
            df = pd.read_csv(db2_front_dataset_spec)  
            self.db2front_dataset_list = dict(zip(df["db"], df["front"]))
        else:
            df = pd.read_csv(DATASET_LISTVIEW_SPEC)
            self.db2front_dataset_list = dict(zip(df["db"], df["front"]))


        # spec match db to front (detail listview)
        if db2_front_detail_spec:
            df = pd.read_csv(db2_front_detail_spec)  
            self.db2front_detail_list = dict(zip(df["db"], df["front"]))
        else:
            df = pd.read_csv(DETAIL_LISTVIEW_SPEC)  
            self.db2front_detail_list = dict(zip(df["db"], df["front"]))
    
    def read_searched_data(self, query):
        '''
        read listview data searched following user query

        [input]
        - query: user query , dictionary (not fixed) // if None, read entire data

        [output]
        - success: bool
        - datasets: searched data (a dictionary with below keys)
            - "rows": a list of dictionary(row)
            - "max_page_num": ax page number of queried data
        '''
        datasets = {
            "rows": [],
            "max_page_num": 0
        }
        success = False
        try:
            if query:
                print("query is not none")
                pass
            else: # read all
                datasets["max_page_num"], df_result = load_list_view(self.db)
                if df_result is not None:
                    datasets["rows"] = self.get_listview_form(df_result)
            success = True
        except Exception as e:
            print("read data error:", e)
        return success, datasets
    
    def get_listview_form(self, df_result):
        '''
        append detail view data for datasets in df_result(dataset list) to rows

        [input]
        - df_result: dataset listview data, pd.DataFrame

        [output]
        - rows: listview data (a list of dictionary), each element is matched to a dataset(row: contains dataset information and detail-listview-info(key:"items")
        '''
        rows = []

        # load detail view data
        cardview_data, listview_data = load_detailed_view(self.db, df_result)
        
        # make data as front listview form
        df_result.rename(columns=self.db2front_dataset_list, inplace=True)
        df_result["Objects"] = df_result.apply(lambda x: f"{x.object_count} objects: {x.object_info_in_detail}", axis=1)
        df_result["items"] = None
        
        rows = df_result.to_dict("records")

        #add items for detailview (listview, cardview data for each datasets)
        for row in rows:
            d_id = row["d_id"]
            cv_data = cardview_data[d_id]
            lv_data = listview_data[d_id]

            # make detail_list data as front listview form
            lv_data.rename(columns=self.db2front_detail_list, inplace=True)
            lv_data["Objects"] = lv_data.apply(lambda x: f"{x.object_count} objects: {x.object_info_in_detail}", axis=1)
            row["items"] = {
                "cardview": cv_data.to_dict("records"),
                "listview": lv_data.to_dict("records"),
            }
        return rows
    