# for postgresql connection
POSTGRES_CONFIG = { # 보안상 문제로 이렇게 하면 안되긴 하는데 그건 담에
    "C2C_USER": "edw2n",
    "C2C_PASSWORD": "p4dsc2c",
    "C2C_HOST": "localhost",
    "C2C_PORT": "5432",
    "C2C_DB": "c2c"
}

SCHEMA_NAME = "public"
TABLE_NAME = ["GroundTruth", "ProductInfo", "QC", "User", "DatasetInfo", "Features", "Transaction"]
ALL_COLUMNS = [[   'gt_id', 'gt_object_id', 'gt_object',
                        'gt_Xordinate', 'gt_Yordinate', 'gt_Zordinate',
                        'gt_Xrotate', 'gt_Yrotate', 'gt_Zrotate', 'gt_state', 
                        'gt_occlusion', 'gt_occlusion_kf',
                        'gt_amt_occlusion', 'gt_amt_occlusion_kf', 'gt_amt_border_l', 'gt_amt_border_r', 'gt_amt_border_kf'
                     ],
                     [
                        'product_id', 'price', 'sold_count' 
                     ],
                     [
                        'qc_id', 'qc_status', 'qc_start_date', 'qc_end_date', 'qc_score', 'object_type', 'object_count', 'tag'
                     ],
                     [
                        'user_id', 'user_idName', 'user_password' 
                     ],
                     [
                        'dataset_id', 'dataset_name'
                     ],
                     [
                        'img_id', 'image_path', 'image_width', 'image_height',
                        'upload_date', 'contrast', 'brightness', 'sharpness', 'saturation',
                        'lat', 'lon', 'region', 'alt', 'roll', 'pitch', 'yaw',
                        'velo_north', 'velo_east', 'velo_forward', 'velo_leftward',
                        'accel_front', 'accel_left', 'accel_top', 'accel_forward', 'accel_leftward', 'accel_upward',
                        'ang_x', 'ang_y', 'ang_z', 'ang_forward', 'ang_leftward', 'ang_upward',
                        'gt_id', 'qc_id', 'user_id', 'product_id', 'dataset_id', 'like_cnt'
                     ],
                     [
                        'tx_id', 'tx_date', 'img_id', 'buyer_id', 'seller_id'
                     ]
                    ]
PK_LIST = ['gt_id', 'product_id', 'qc_id', 'user_id', 'dataset_id','img_id','tx_id']
## PK table, PK column, FK table, FK column
FK_LIST = [('GroundTruth','gt_id', 'Features', 'gt_id'),
           ('ProductInfo', 'product_id', 'Features', 'product_id'),
           ('QC', 'qc_id', 'Features', 'qc_id',),
           ('User', 'user_id', 'Features', 'user_id'),
           ('DatasetInfo', 'dataset_id','Features', 'dataset_id'),
           ('Features', 'img_id', 'Transaction', 'img_id'),
           ('User', 'user_id', 'Transaction', 'buyer_id'),
           ('User', 'user_id', 'Transaction', 'seller_id')
           ]

# GroundTruth 
GROUNDTRUTH_COLUMNS_INFO = {
    "gt_id":               "bigint NOT NULL",
    "gt_object_id":        "bigint NULL",
    "gt_object":           "varchar(50) NULL",
    "gt_Xordinate":        "numeric NULL",
    "gt_Yordinate":        "numeric NULL",
    "gt_Zordinate":        "numeric NULL",
    "gt_Xrotate":          "numeric NULL",
    "gt_Yrotate":          "numeric NULL",
    "gt_Zrotate":          "numeric NULL",
    "gt_state":            "numeric NULL",
    "gt_occlusion":        "numeric NULL",
    "gt_occlusion_kf":     "numeric NULL",
    "gt_amt_occlusion":    "numeric NULL",
    "gt_amt_occlusion_kf": "numeric NULL",
    "gt_amt_border_l":     "numeric NULL",
    "gt_amt_border_r":     "numeric NULL",
    "gt_amt_border_kf":    "numeric NULL"
}

# ProductInfo
PRODUCTINFO_COLUMNS_INFO = {
    "product_id": "bigint NOT NULL",
    "price":      "bigint NULL",
    "sold_count": "bigint NULL"
}

# QC
QC_COLUMNS_INFO = {
    "qc_id":         "bigint NOT NULL",
    "qc_status":     "varchar(50) NOT NULL",
    "qc_start_date": "timestamp with time zone NULL",
    "qc_end_date":   "timestamp with time zone NULL",
    "qc_score":      "numeric NULL",
    "object_type":   "bigint NULL",
    "object_count":  "bigint NULL",
    "tag":           "varchar(50) NULL"
}

# User 
USER_COLUMNS_INFO = {
    "user_id":       "bigint NOT NULL",
    "user_idName":   "varchar(50) NOT NULL",
    "user_password": "varchar(50) NOT NULL",
}

# DatasetInfo
DATASETINFO_COLUMNS_INFO = {
    "dataset_id":   "bigint NOT NULL",
    "dataset_name": "varchar(50) NOT NULL",
}

# Features
FEATURES_COLUMNS_INFO = {
    "img_id":         "bigint NOT NULL",
    "image_path":     "varchar(100) NOT NULL",
    "image_width":    "bigint NOT NULL",
    "image_height":   "bigint NOT NULL",
    "upload_date":    "timestamp with time zone NOT NULL",
    "contrast":       "numeric NOT NULL",
    "brightness":     "numeric NOT NULL",
    "sharpness":      "numeric NOT NULL",
    "saturation":     "numeric NOT NULL",
    "lat":            "numeric NULL",
    "lon":            "numeric NULL",
    "region":         "varchar(50) NULL",
    "alt":            "numeric NULL",
    "roll":           "numeric NULL",
    "pitch":          "numeric NULL",
    "yaw":            "numeric NULL",
    "velo_north":     "numeric NULL",
    "velo_east":      "numeric NULL",
    "velo_forward":   "numeric NULL",
    "velo_leftward":  "numeric NULL",
    "accel_front":    "numeric NULL",
    "accel_left":     "numeric NULL",
    "accel_top":      "numeric NULL",
    "accel_forward":  "numeric NULL",
    "accel_leftward": "numeric NULL",
    "accel_upward":   "numeric NULL",
    "ang_x":          "numeric NULL",
    "ang_y":          "numeric NULL",
    "ang_z":          "numeric NULL",
    "ang_forward":    "numeric NULL",
    "ang_leftward":   "numeric NULL",
    "ang_upward":     "numeric NULL",
    "gt_id":          "bigint NOT NULL",
    "qc_id":          "bigint NOT NULL",
    "user_id":        "bigint NOT NULL",
    "product_id":     "bigint NOT NULL",
    "dataset_id":     "bigint NOT NULL",
    "like_cnt":       "bigint NOT NULL"
}

# transaction
TRANSACTION_COLUMNS_INFO = {
"tx_id":     "bigint NOT NULL",
"tx_date":   "timestamp with time zone NOT NULL",
"img_id":    "bigint NOT NULL",
"buyer_id":  "bigint NOT NULL",
"seller_id": "bigint NOT NULL",
}

ALL_COLUMNS_INFO = [GROUNDTRUTH_COLUMNS_INFO, PRODUCTINFO_COLUMNS_INFO,QC_COLUMNS_INFO,USER_COLUMNS_INFO, DATASETINFO_COLUMNS_INFO, FEATURES_COLUMNS_INFO, TRANSACTION_COLUMNS_INFO]
