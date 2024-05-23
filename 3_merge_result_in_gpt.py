import pandas as pd
from pandas import DataFrame
import os


def create_pandas(class_name: str):
    if os.path.exists("./result/"+class_name+".xlsx"):
        df = pd.read_excel("./result/"+class_name+".xlsx")
        df.set_index('api_name', inplace=True)
        return True, df
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
    return False, df

def create_gpt_class_pandas(class_name: str):
    if os.path.exists(dir_gpt+class_name+"/"+class_name+".csv"):
        df = pd.read_csv(dir_gpt+class_name+"/"+class_name+".csv")
        df.set_index('api', inplace=True)
        return df
    else:
        df = pd.DataFrame({
            'api': [],
            'desc': [],
            'replace': []

        },
        )
        df.set_index('api', inplace=True)
    return df

def write_excel(df: DataFrame, class_name: str):
    df.to_excel("./result/"+class_name+".xlsx")

def result_excel_exit(class_name: str):
    return os.path.exists("./result/"+class_name+".xlsx")

def get_api_name(api_name: str):
    api_index = api_name.rfind('.')
    if api_index == -1:
        return False, "", ""
    class_name = api_name[0:api_index]
    api_name = api_name[api_index+1:]
    return True,class_name, api_name

def get_class_and_api2(full_name: str):
    this_full_name_list = full_name.split('.')
    this_api_name = ".".join(this_full_name_list[-2:])
    this_class_name = ".".join(this_full_name_list[:-2])
    return this_class_name, this_api_name

def read_json(class_name: str):
    df = create_gpt_class_pandas(class_name)
    for api_name in df.index:
        if not pd.isna(df.loc[api_name, "replace"]):
            replace_string: str = df.loc[api_name, "replace"]
            replace_list = replace_string.split("&")
            for next_api in replace_list:
                merge_api(class_name, next_api, api_name)

def merge_api(class_name1: str, class_and_api_name2: str, api_name1:str):
    flag, class_name2, api_name2 = get_api_name(class_and_api_name2)
    if not flag:
        return
    flag, df1 = create_pandas(class_name1)
    if not flag:
        return
    # check
    flag, df2 = create_pandas(class_name2)
    if not flag:
        class_name2, api_name2 = get_class_and_api2(class_and_api_name2)
        flag, df2 = create_pandas(class_name2)
        if not flag:
            return
    # check done
    api_full_name1 = class_name1 + '.' + api_name1
    api_full_name2 = class_name2 + '.' + api_name2
    df1_next: str = df1.loc[api_name1, 'next_full_api_name']
    try:
        df1_list = df1_next.split('&')
    except:
        df1_list = []
        df1_next = "&"
    if api_full_name2 not in df1_list:
        df1_next += api_full_name2 + "&"
        df1.loc[api_name1, 'next_full_api_name'] = df1_next
        write_excel(df1, class_name1)
    flag, df2 = create_pandas(class_name2)
    if not flag:
        return
    df2_last: str = df2.loc[api_name2, 'last_full_api_name']
    try:
        df2_list = df2_last.split('&')
    except:
        df2_list = []
        df2_last = "&"
    if api_full_name1 not in df2_list:
        df2_last += api_full_name1 + "&"
        df2.loc[api_name2, 'last_full_api_name'] = df2_last
        write_excel(df2, class_name2)

dir_gpt = './gpt_class_with_group_with_res'

if __name__ == '__main__':
    json_files = os.listdir(dir_gpt)
    json_files_length = len(json_files)
    for json_file_path_index in range(0, json_files_length):
        print('===='+'('+str(json_file_path_index)+'/'+str(json_files_length)+')==='+json_files[json_file_path_index]+'=========')
        read_json(json_files[json_file_path_index])

