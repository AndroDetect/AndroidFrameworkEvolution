import pandas as pd
from pandas import DataFrame
import os


def create_pandas(class_name: str):
    if os.path.exists("./result/"+class_name+".xlsx"):
        df = pd.read_excel("./result/"+class_name+".xlsx")
        df.set_index('api_name', inplace=True)
        return df
    else:
        df = pd.DataFrame({
            'api_name': [],
            'func_api_name': [],
            'func_class_name': [],
            'next_full_api_name': [],
            'last_full_api_name': []

        },
        )
        df.set_index('api_name', inplace=True)
    return df

def write_excel(df: DataFrame, class_name: str):
    df.to_excel("./result/"+class_name+".xlsx")

def result_excel_exit(class_name: str):
    return os.path.exists("./result/"+class_name+".xlsx")

def read_xlsx(file_path1: str, file_path2: str):
    df = create_pandas(file_path1)
    for api_name in df.index:
        df2 = create_pandas(file_path2)
        if api_name in df2.index:
            merge_api(file_path1, file_path2, api_name)

def merge_api(class_name1: str, class_name2: str, api_name:str):
    api_full_name1 = class_name1+'.'+api_name
    api_full_name2 = class_name2+'.'+api_name
    df1 = create_pandas(class_name1)
    df1_next: str = df1.loc[api_name, 'next_full_api_name']
    try:
        df1_list = df1_next.split('&')
    except:
        df1_list = []
        df1_next = "&"
    if api_full_name2 not in df1_list:
        df1_next += api_full_name2 + "&"
        df1.loc[api_name, 'next_full_api_name'] = df1_next
        write_excel(df1, class_name1)
    df2 = create_pandas(class_name2)
    df2_last: str = df2.loc[api_name, 'last_full_api_name']
    try:
        df2_list = df2_last.split('&')
    except:
        df2_list = []
        df2_last = "&"
    if api_full_name1 not in df2_list:
        df2_last += api_full_name1 + "&"
        df2.loc[api_name, 'last_full_api_name'] = df2_last
        write_excel(df2, class_name2)



if __name__ == '__main__':
    json_files = os.listdir('./result')
    json_files_length = len(json_files)
    df = pd.read_csv('android_classes_dict.csv')
    for item_index in df.index:
        print('===='+str(item_index)+'====')
        read_xlsx(df.loc[item_index, "class_name"], df.loc[item_index, "next_class_name"])

