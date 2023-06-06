from dbmanager.utils import load_list_view_default

class ReadManager():
    '''
    support search pipeline (db->server)
    '''
    db2front = {
            "dataset_id": "d_id", # not required
            "dataset_name": "Title",
            "price_total": "Price",
            "iamge_count": "MatchedData", 
            "avg_price_per_image": "PricePerImage",
            "sales_count": "SalesCount",
            "like_count": "Likes",
            "qc_state": "QCstate",
            "qc_score": "QCscore",
            "uploader": "Uploader",
            "upload_date": "UploadDate",
            "object_list": "object_list", # not required
            "object_count": "object_count", # need to mery with object_list, object_info_in_detail
            "object_info_in_detail": "object_info_in_detail", # not required
        }
    def __init__(self, db, db2_front_spec=None):
        self.db = db

        if db2_front_spec:
            # read file and self.db2_front = ~~~
            pass
    
    def read_searched_data(self, query):
        '''
        read listview data searched following user query

        [input]
        - query: user query , dictionary (not fixed) // if None, read entire data

        [output]
        - success: bool
        - data: searched data (a list of dictionary(row))
        '''
        data = []
        success = False
        try:
            if query:
                pass
            else: # read all
                df_result = load_list_view_default(self.db)
                if df_result:
                    df_result.rename(columns=self.db2front, inplace=True)
                    df_result['Objects'] = df_result.apply(lambda x: f"{x.object_count} objects: {x.object_info_in_detail}", axis=1)
                    data = df_result.to_dict("records")
            success = True
        except Exception as e:
            print("read data error:", e)
        return success, data

            

    