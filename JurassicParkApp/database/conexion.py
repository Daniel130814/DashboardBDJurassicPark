import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=JurassicPark;"
        "UID=sa;"
        "PWD=tu_password;"
        "TrustServerCertificate=yes;"
    )
    return conn