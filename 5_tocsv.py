import os

from pandas import DataFrame
import pandas as pd

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
            'last_full_api_name': [],
            "ways": [],
            "list": []
        },
        )
        df.set_index('api_name', inplace=True)
    return df

def read_all_excel():
    excel_files = os.listdir('./result')
    excel_files_length = len(excel_files)
    for excel_file_path_index in range(0, excel_files_length):
        print('----------' + ' (' + str(excel_file_path_index) + '/' + str(excel_files_length) + ')----' + excel_files[excel_file_path_index])
        class_name = excel_files[excel_file_path_index][:-5]
        df: DataFrame = create_pandas(class_name)
        for df_index in df.index:
            df.loc[df_index, "full_fuc_name"] = df.loc[df_index, "func_class_name"]+'.'+df.loc[df_index, "func_api_name"]
        df = df.drop('func_class_name', axis=1)
        df = df.drop('func_api_name', axis=1)
        df = df.drop('ways', axis=1)
        df = df.drop('next_full_api_name', axis=1)
        df = df.drop('last_full_api_name', axis=1)
        df = df.drop('ways', axis=1)
        df = df.drop('list', axis=1)
        df.to_csv("./res_csv/"+class_name+'.csv')

if __name__ == '__main__':
    read_all_excel()