import requests
from hdbcli import dbapi
import pandas as pd
import os


def read_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

def call_file_api(input_data):
    files = {"file": input_data}
    api_url = "http://127.0.0.1:8000/upload/"
    response = requests.post(api_url, files=files)
    return response.json()

def call_chat_api(query, file_name = None):
    if file_name == None:
        querys = {"query": query}
    else:
        querys = {"query": query, "file_name": file_name}
    api_url = "http://127.0.0.1:8000/chat/"
    response = requests.post(api_url, querys).json()
    return response


def get_hana_db_conn():
    conn = dbapi.connect(
            address=os.environ.get("Hostname"),
            port=os.environ.get("Port"),
            user=os.environ.get("Username"),
            password=os.environ.get("Password"),
    )
    return conn

def get_table_from_cursor(cursor):
        data = pd.DataFrame(cursor.fetchall())
        header = [i[0] for i in cursor.description]
        data = data.rename(columns=dict(zip(data.columns, header)))
        data = data.convert_dtypes()
        return data

def get_sap_table(table_name, schema, conn):
    cursor = conn.cursor()
    cursor.execute(f"SELECT VEC_META FROM "+ schema +"." + table_name)
    return get_table_from_cursor(cursor)


def get_source(response):
    ans = response['answer']
    source = ""
    try:
        if os.path.basename(response['source_documents'][0]['metadata']['source']) != "":
            src = os.path.basename(response['source_documents'][0]['metadata']['source'])
            source += "\n Document Name: " +src + "  Page No.: " + str(response['source_documents'][0]['metadata']['page']+1) 
        
            reply = ans + '\n\n' + 'Source: ' +  source
            return reply
    
    except:
        return "Sorry There is no relevent Source Document!" + '\n\n' + "Thanks for asking!"
    

def clear_data():
    api_url = "http://127.0.0.1:8000/clear_data/"
    response = requests.post(api_url)
    return response