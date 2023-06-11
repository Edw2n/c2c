from dbmanager.utils import insert_tx_info

class TXManager():
    '''
    support tx pipeline (db->server)
    '''

    def __init__(self, db):
        '''

        '''
        self.db = db
    
    def update_transaction(self, transaction_info):
        '''
        [input]
        - transaction_info: {
            "user_name": str,
            "img_ids": a list of int,
            "dataset_name": user defined name of bought dataset, str
        }

        [output]
        - success: bool
        '''
        success = False

        try:
            success = insert_tx_info(self.db, transaction_info["user_name"], transaction_info["img_ids"], transaction_info["dataset_name"])
        except Exception as e:
            print("transaction update error,", e)
        
        return success
