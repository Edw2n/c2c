# for postgresql connection
POSTGRES_CONFIG = { # 보안상 문제로 이렇게 하면 안되긴 하는데 그건 담에
    "C2C_USER": "edw2n",
    "C2C_PASSWORD": "p4dsc2c",
    "C2C_HOST": "localhost",
    "C2C_PORT": "5432",
    "C2C_DB": "c2c",

}

SCHEMA_NAME = "public"
TABLE_NAME = "user"
USER_COLUMNS_INFO = {
    "Name": "VARCHAR(128)",
    "Age": "INTEGER",
}
