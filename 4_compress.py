import os

from pandas import DataFrame
import pandas as pd


def create_pandas(class_name: str):
    if os.path.exists("./result/" + class_name + ".xlsx"):
        df = pd.read_excel("./result/" + class_name + ".xlsx")
        df.set_index('api_name', inplace=True)
        return df
    else:
        return False


def write_excel(df: DataFrame, class_name: str):
    df.to_excel("./result/" + class_name + ".xlsx")


def compress_all_api():
    excel_files = os.listdir('./result')
    excel_files_length = len(excel_files)
    for excel_file_path_index in range(0, excel_files_length):
        print('----------' + ' (' + str(excel_file_path_index) + '/' + str(excel_files_length) + ')----' + excel_files[
            excel_file_path_index])
        if ")" in excel_files[excel_file_path_index]:
            return
        class_name = excel_files[excel_file_path_index][:-5]
        df: DataFrame = create_pandas(class_name)
        if "ways" not in df.columns:
            df["ways"] = "#"
            df["list"] = "#"
        write_excel(df, class_name)
        df: DataFrame = create_pandas(class_name)
        flag = False
        for api_name in df.index:
            if ")." in df.loc[api_name, "func_api_name"]:
                flag = True
                df.loc[api_name, "func_api_name"] = df.loc[api_name, "func_api_name"].replace(").", "")
        if flag:
            df = df.reset_index(drop=True)
            for index in df.index:
                df.loc[index, "api_name"] = df.loc[index, "func_api_name"]
            df.set_index('api_name', inplace=True)
            write_excel(df, class_name)
        df = create_pandas(class_name)
        df = df.reset_index(drop=False)
        df = df.drop_duplicates(subset=["api_name"], keep='first', inplace=False)
        df.set_index('api_name', inplace=True)
        write_excel(df, class_name)
        df = create_pandas(class_name)
        item_list = df.index
        for api_name in item_list:
            df_flag = df.loc[api_name, "ways"]
            try:
                if len(df_flag) == 0:
                    df_flag = "#"
            except:
                df_flag = "#"
            if df_flag == "#":
                compress_api(class_name, api_name)


def result_excel_exit(class_name: str):
    return os.path.exists("./result/" + class_name + ".xlsx")


def compress_api(class_name: str, api_name: str):
    full_name_root = class_name + '.' + api_name
    full_api_wait_to_search_list: list = []
    full_api_and_way_dic: dict = {full_name_root: "根目录" + full_name_root}
    full_api_wait_to_search_list.append(full_name_root)
    all_api_list = []
    all_api_list.append(full_name_root)
    while len(full_api_wait_to_search_list) > 0:
        this_full_name: str = full_api_wait_to_search_list[0]
        full_api_wait_to_search_list.remove(this_full_name)
        this_class_name, this_api_name = get_class_and_api(this_full_name)
        if not result_excel_exit(this_class_name):
            this_class_name, this_api_name = get_class_and_api2(this_full_name)
            if not result_excel_exit(this_class_name):
                this_class_name, this_api_name = get_class_and_api3(this_full_name)
                if not result_excel_exit(this_class_name):
                    this_class_name, this_api_name = get_class_and_api4(this_full_name)
        df_this: DataFrame = create_pandas(this_class_name)
        this_next_str: str = df_this.loc[this_api_name, "next_full_api_name"]
        try:
            this_next_list = this_next_str.split('&')
        except:
            this_next_str = "&"
            this_next_list = []
        for this_next_list_item in this_next_list:
            if len(this_next_list_item) == 0:
                continue
            if this_next_list_item not in full_api_and_way_dic.keys():
                full_api_and_way_dic[this_next_list_item] = this_full_name + " to " + this_next_list_item
                full_api_wait_to_search_list.append(this_next_list_item)
                all_api_list.append(this_next_list_item)
        this_last_str: str = df_this.loc[this_api_name, "last_full_api_name"]
        try:
            this_last_list = this_last_str.split('&')
        except:
            this_last_list = []
            this_last_str = "&"
        for this_last_list_item in this_last_list:
            if len(this_last_list_item) == 0:
                continue
            if this_last_list_item not in full_api_and_way_dic.keys():
                full_api_and_way_dic[this_last_list_item] = this_last_list_item + " to " + this_full_name
                full_api_wait_to_search_list.append(this_last_list_item)
                all_api_list.append(this_last_list_item)
    for full_api_and_way_dic_key in full_api_and_way_dic.keys():
        key_class_name, key_api_name = get_class_and_api(full_api_and_way_dic_key)
        if not result_excel_exit(key_class_name):
            key_class_name, key_api_name = get_class_and_api2(full_api_and_way_dic_key)
            if not result_excel_exit(key_class_name):
                key_class_name, key_api_name = get_class_and_api3(full_api_and_way_dic_key)
                if not result_excel_exit(key_class_name):
                    key_class_name, key_api_name = get_class_and_api4(full_api_and_way_dic_key)
        if not result_excel_exit(key_class_name):
            continue
        df_key: DataFrame = create_pandas(key_class_name)
        if key_api_name not in df_key.index:
            continue
        if "ways" not in df_key.columns:
            df_key["ways"] = "#"
            df_key["list"] = "#"
        df_key.loc[key_api_name, "func_class_name"] = class_name
        df_key.loc[key_api_name, "func_api_name"] = api_name
        df_key.loc[key_api_name, "ways"] = str(full_api_and_way_dic)
        df_key.loc[key_api_name, "list"] = all_api_list
        write_excel(df_key, key_class_name)


def get_class_and_api(full_name: str):
    this_full_name_list = full_name.split('.')
    this_api_name = this_full_name_list[-1]
    this_class_name = ".".join(this_full_name_list[:-1])
    return this_class_name, this_api_name


def get_class_and_api2(full_name: str):
    this_full_name_list = full_name.split('.')
    this_api_name = ".".join(this_full_name_list[-2:])
    this_class_name = ".".join(this_full_name_list[:-2])
    return this_class_name, this_api_name


def get_class_and_api3(full_name: str):
    this_full_name_list = full_name.split('.')
    this_api_name = ".".join(this_full_name_list[-3:])
    this_class_name = ".".join(this_full_name_list[:-3])
    return this_class_name, this_api_name


def get_class_and_api4(full_name: str):
    this_full_name_list = full_name.split('.')
    this_api_name = ".".join(this_full_name_list[-4:])
    this_class_name = ".".join(this_full_name_list[:-4])
    return this_class_name, this_api_name


if __name__ == '__main__':
    compress_all_api()
