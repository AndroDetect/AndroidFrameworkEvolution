import pandas as pd
from pandas import DataFrame
import os
import json
import re


def create_pandas(class_name: str):
    if os.path.exists("./result/" + class_name + ".xlsx"):
        df = pd.read_excel("./result/" + class_name + ".xlsx")
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
    df.to_excel("./result/" + class_name + ".xlsx")


def result_excel_exit(class_name: str):
    return os.path.exists("./result/" + class_name + ".xlsx")


def res_json_file_exit(dir_path: str, class_name: str):
    return os.path.exists(dir_path + '/' + class_name + ".json")


def read_json(dir_path: str, json_file_path: str):
    json_file_path = dir_path + '/' + json_file_path
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    full_name = json_file_path.split('/')[-1][:-5]
    isDeprecated = data['deprecated']
    apis_dict: dict = data['Fuctions']
    all_replace_class_list = []
    df = create_pandas(full_name)
    for api_item in apis_dict:
        write_api_only(api_item, full_name, df)
    write_excel(df, full_name)
    if isDeprecated:
        replace_class_list: list = data['LinkedList']
        for replace_class in replace_class_list:
            replace_class_name = replace_class.strip().split("\s+")[0]
            if replace_class_name not in all_replace_class_list:
                if res_json_file_exit(dir_path, replace_class_name):
                    all_replace_class_list.append(replace_class_name)
        replace_class_list = data['SeeList']
        for replace_class in replace_class_list:
            replace_class_name = replace_class.strip().split("\s+")[0]
            if replace_class_name not in all_replace_class_list:
                if res_json_file_exit(dir_path, replace_class_name):
                    all_replace_class_list.append(replace_class_name)
        replace_class_list = get_else_deprecated_class(data['Desc'])
        for replace_class in replace_class_list:
            replace_class_name = replace_class.strip().split("\s+")[0]
            if replace_class_name not in all_replace_class_list:
                if res_json_file_exit(dir_path, replace_class_name):
                    all_replace_class_list.append(replace_class_name)
        for replace_class_item in all_replace_class_list:
            replace_classfile_path = dir_path + '/' + replace_class_item + '.json'
            if full_name.split(".")[-1] == replace_class_item.split(".")[-1]:
                with open(replace_classfile_path, 'r') as replace_classfile_file:
                    replace_class_data = json.load(replace_classfile_file)
                for api_item in apis_dict:
                    flag, api_short_name = get_api_name(api_item)
                    if not flag:
                        continue
                    find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'], full_name, api_short_name,
                                                           replace_class_item)
            else:
                add_df(df_for_diff_name_class, full_name, replace_class_item)
    for api_item in apis_dict:
        read_api_without_deprecated_class(api_item, full_name, apis_dict[api_item], apis_dict, dir_path)


def write_api_only(api_full_name: str, class_name: str, df: DataFrame):
    flag, api_short_name = get_api_name(api_full_name)
    if not flag:
        return
    if api_short_name in df.index:
        # There is no need to update if there is already api_shortname
        return
    df.loc[api_short_name, 'func_class_name'] = class_name
    df.loc[api_short_name, 'func_api_name'] = api_short_name
    df.loc[api_short_name, 'next_full_api_name'] = "&"
    df.loc[api_short_name, 'last_full_api_name'] = "&"


def read_api_without_deprecated_class(api_full_name: str, class_name: str, api_dict: dict, all_api_dicts: dict,
                                      dir_path: str):
    flag, api_short_name = get_api_name(api_full_name)
    if not flag:
        return
    isDeprecated = api_dict['deprecated']
    all_replace_api_list = []
    if isDeprecated:
        replace_api_list: list = api_dict['LinkedList']
        for replace_api_item in replace_api_list:
            replace_api_name_item: str = replace_api_item
            replace_api_name_split_list = replace_api_name_item.split("@see")
            for replace_api_name_split_item in replace_api_name_split_list:
                replace_api_name = replace_api_name_split_item.replace("*", "").replace("@see", "").replace("/",
                                                                                                            "").replace(
                    "@hide", "").strip()
                if replace_api_name not in all_replace_api_list:
                    all_replace_api_list.append(replace_api_name)
        replace_api_list: list = api_dict['SeeList']
        for replace_api_item in replace_api_list:
            replace_api_name_item: str = replace_api_item
            replace_api_name_split_list = replace_api_name_item.split("@see")
            for replace_api_name_split_item in replace_api_name_split_list:
                replace_api_name = replace_api_name_split_item.replace("*", "").replace("@see", "").replace("/",
                                                                                                            "").replace(
                    "@hide", "").strip()
                if replace_api_name not in all_replace_api_list:
                    all_replace_api_list.append(replace_api_name)
        replace_api_list: list = get_else_deprecated_api(api_dict['Desc'])
        for replace_api in replace_api_list:
            replace_api_name = replace_api
            if replace_api_name not in all_replace_api_list:
                all_replace_api_list.append(replace_api_name.strip())
        for replace_api_item in all_replace_api_list:
            if '(' in replace_api_item:
                # Is it an API, determine if it is an intra class API
                if '.' not in replace_api_item and '#' not in replace_api_item:
                    # In class APIs, searching for in class APIs
                    flag, replace_api_item_short_name = get_api_name(replace_api_item)
                    if not flag:
                        continue
                    if replace_api_item_short_name != api_short_name:
                        all_keys_list = all_api_dicts.keys()
                        for keys_item in all_keys_list:
                            if replace_api_item_short_name in keys_item:
                                merge_api(class_name, api_short_name, class_name, replace_api_item_short_name)
                                break
                else:
                    # Non intra class API
                    if '#' in replace_api_item:
                        split_list: list = replace_api_item.split('#')
                        split_list_len = len(split_list)
                        if split_list_len == 2:
                            if split_list[0].strip() == '':
                                # In class API
                                flag, replace_api_item_short_name = get_api_name(split_list[1].strip())
                                if not flag:
                                    continue
                                if replace_api_item_short_name != api_short_name:
                                    all_keys_list = all_api_dicts.keys()
                                    for keys_item in all_keys_list:
                                        if replace_api_item_short_name in keys_item:
                                            merge_api(class_name, api_short_name, class_name,
                                                      replace_api_item_short_name)
                                            break
                            else:
                                class_name2 = split_list[0].strip()
                                if '.' in class_name2:
                                    # It is the complete package name
                                    if res_json_file_exit(dir_path, class_name2):
                                        replace_class_file_path = dir_path + '/' + class_name2 + '.json'
                                        with open(replace_class_file_path, 'r', encoding='utf-8') as replace_class_file:
                                            replace_class_data = json.load(replace_class_file)
                                        api_name2: str = split_list[1].strip()
                                        if '(' in api_name2:
                                            # It is the API name
                                            flag, api_short_name2 = get_api_name(api_name2)
                                            if not flag:
                                                continue
                                            find_and_merge_api_with_api_name(replace_class_data['Fuctions'], class_name,
                                                                             api_short_name, class_name2,
                                                                             api_short_name2)
                                        else:
                                            # Ignoring API names and searching directly
                                            find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'],
                                                                                   class_name, api_short_name,
                                                                                   class_name2)
                                else:
                                    # Not the full package name
                                    class_name_split_list = class_name.split('.')
                                    class_name_split_list[-1] = class_name2
                                    separator = "."
                                    class_name2 = separator.join(class_name_split_list)
                                    if res_json_file_exit(dir_path, class_name2):
                                        replace_class_file_path = dir_path + '/' + class_name2 + '.json'
                                        with open(replace_class_file_path, 'r', encoding='utf-8') as replace_class_file:
                                            replace_class_data = json.load(replace_class_file)
                                        api_name2: str = split_list[1].strip()
                                        if '(' in api_name2:
                                            # Is the API name
                                            flag, api_short_name2 = get_api_name(api_name2)
                                            if not flag:
                                                continue
                                            find_and_merge_api_with_api_name(replace_class_data['Fuctions'],
                                                                             class_name, api_short_name,
                                                                             class_name2, api_short_name2)
                                        else:
                                            # Ignoring API names and searching directly
                                            find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'],
                                                                                   class_name, api_short_name,
                                                                                   class_name2)
                        else:
                            continue
                    else:
                        # Just the package name
                        class_name2 = replace_api_item
                        if '.' in class_name2:
                            # Is the full package name
                            if res_json_file_exit(dir_path, class_name2):
                                replace_class_file_path = dir_path + '/' + class_name2 + '.json'
                                with open(replace_class_file_path, 'r') as replace_class_file:
                                    replace_class_data = json.load(replace_class_file)
                                # Ignoring API names and searching directly
                                find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'],
                                                                       class_name, api_short_name,
                                                                       class_name2)
                        else:
                            # Not the full package name
                            class_name_split_list = class_name.split('.')
                            class_name_split_list[-1] = class_name2
                            separator = "."
                            class_name2 = separator.join(class_name_split_list)
                            # Ignoring API names and searching directly
                            find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'],
                                                                   class_name, api_short_name,
                                                                   class_name2)
            else:
                # Without parentheses
                if '#' in replace_api_item:
                    split_list: list = replace_api_item.split('#')
                    split_list_len = len(split_list)
                    if split_list_len == 2:
                        if split_list[0].strip() == '':
                            # API in class
                            replace_api_item_short_name = split_list[1].strip()
                            if not flag:
                                continue
                            if replace_api_item_short_name != api_short_name:
                                all_keys_list = all_api_dicts.keys()
                                for keys_item in all_keys_list:
                                    if replace_api_item_short_name in keys_item:
                                        merge_api(class_name, api_short_name, class_name,
                                                  replace_api_item_short_name)
                                        break
                        else:
                            class_name2 = split_list[0].strip()
                            if '.' in class_name2:
                                # It is the complete package name
                                if res_json_file_exit(dir_path, class_name2):
                                    replace_class_file_path = dir_path + '/' + class_name2 + '.json'
                                    with open(replace_class_file_path, 'r', encoding='utf-8') as replace_class_file:
                                        replace_class_data = json.load(replace_class_file)
                                    api_name2: str = split_list[1].strip()
                                    if '(' in api_name2:
                                        # It is the API name
                                        flag, api_short_name2 = get_api_name(api_name2)
                                        if not flag:
                                            continue
                                        find_and_merge_api_with_api_name(replace_class_data['Fuctions'], class_name,
                                                                         api_short_name, class_name2, api_short_name2)
                                    else:
                                        # Ignoring API names and searching directly
                                        find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'],
                                                                               class_name, api_short_name,
                                                                               class_name2)
                            else:
                                # Not the full package name
                                class_name_split_list = class_name.split('.')
                                class_name_split_list[-1] = class_name2
                                separator = "."
                                class_name2 = separator.join(class_name_split_list)
                                if res_json_file_exit(dir_path, class_name2):
                                    replace_class_file_path = dir_path + '/' + class_name2 + '.json'
                                    with open(replace_class_file_path, 'r', encoding='utf-8') as replace_class_file:
                                        replace_class_data = json.load(replace_class_file)
                                    api_name2: str = split_list[1].strip()
                                    if '(' in api_name2:
                                        # It is the API name
                                        flag, api_short_name2 = get_api_name(api_name2)
                                        if not flag:
                                            continue
                                        find_and_merge_api_with_api_name(replace_class_data['Fuctions'],
                                                                         class_name, api_short_name,
                                                                         class_name2, api_short_name2)
                                    else:
                                        # Ignoring API names and searching directly
                                        find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'],
                                                                               class_name, api_short_name,
                                                                               class_name2)
                    else:
                        continue
                else:
                    class_name2 = replace_api_item
                    if '.' in class_name2:
                        # It is the complete package name
                        if res_json_file_exit(dir_path, class_name2):
                            replace_class_file_path = dir_path + '/' + class_name2 + '.json'
                            with open(replace_class_file_path, 'r') as replace_class_file:
                                replace_class_data = json.load(replace_class_file)
                            find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'],
                                                                   class_name, api_short_name,
                                                                   class_name2)
                    else:
                        # Not the full package name
                        class_name_split_list = class_name.split('.')
                        class_name_split_list[-1] = class_name2
                        separator = "."
                        class_name2 = separator.join(class_name_split_list)
                        if res_json_file_exit(dir_path, class_name2):
                            replace_class_file_path = dir_path + '/' + class_name2 + '.json'
                            with open(replace_class_file_path, 'r', encoding='utf-8') as replace_class_file:
                                replace_class_data = json.load(replace_class_file)
                            find_and_merge_api_in_class_deprecated(replace_class_data['Fuctions'],
                                                                   class_name, api_short_name,
                                                                   class_name2)


def read_json_dir(dir_path: str):
    json_files = os.listdir(dir_path)
    json_files_length = len(json_files)
    for json_file_path_index in range(0, json_files_length):
        print(dir_path + ' (' + str(json_file_path_index) + '/' + str(json_files_length) + ')----' + json_files[
            json_file_path_index])
        read_json(dir_path, json_files[json_file_path_index])


def get_api_name(api_name: str):
    api_short_name_len = api_name.find('(')
    if api_short_name_len > 0:
        return True, api_name[:api_short_name_len]
    return False, ''


def find_and_merge_api_with_api_name(class2_api_dicts: dict, class_name1: str, api_name1: str, class_name2: str,
                                     api_short_name2: str):
    class2_api_keys = class2_api_dicts.keys()
    for class2_api_key in class2_api_keys:
        if api_short_name2 in class2_api_key:
            flag, api_name2 = get_api_name(class2_api_key)
            if not flag:
                continue
            if api_short_name2 == api_name2:
                merge_api(class_name1, api_name1, class_name2, api_name2)
            return


def find_and_merge_api_in_class_deprecated(class2_api_dict: dict, class_name1: str, api_name1: str, class_name2: str):
    class2_api_keys = class2_api_dict.keys()
    for class2_api_key in class2_api_keys:
        if api_name1 in class2_api_key:
            flag, api_name2 = get_api_name(class2_api_key)
            if not flag:
                continue
            if api_name1 == api_name2:
                merge_api(class_name1, api_name1, class_name2, api_name2)
                return


def merge_api(class_name1: str, api_name1: str, class_name2: str, api_name2: str):
    # Class1 replaced by class2
    api_full_name1 = class_name1 + '.' + api_name1
    api_full_name2 = class_name2 + '.' + api_name2
    df1 = create_pandas(class_name1)
    if api_name1 not in df1.index:
        # There is no need to update if there is already api_short_name
        df1.loc[api_name1, 'func_class_name'] = class_name1
        df1.loc[api_name1, 'func_api_name'] = api_name1
        df1.loc[api_name1, 'next_full_api_name'] = "&"
        df1.loc[api_name1, 'last_full_api_name'] = "&"
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
    df2 = create_pandas(class_name2)
    if api_name2 not in df2.index:
        # There is no need to update if there is already api_short_name
        df2.loc[api_name2, 'func_class_name'] = class_name2
        df2.loc[api_name2, 'func_api_name'] = api_name2
        df2.loc[api_name2, 'next_full_api_name'] = "&"
        df2.loc[api_name2, 'last_full_api_name'] = "&"
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


def get_else_deprecated_class(desc: str):
    deprecated_list = []
    desc_line_list = desc.replace("/*", "").split('*')
    flag = 0
    for desc_line in desc_line_list:
        # Due to some formatting reasons, search within the scope
        if 'deprecated ' in desc_line or 'Deprecated ' in desc_line or 'use ' in desc_line or 'Use ' in desc_line \
                or ' instead' in desc_line or ' Instead' in desc_line or 'Replace by ' in desc_line or 'replace by ' in desc_line:
            flag = 2
        if flag > 0:
            re_word_list = re.findall('(?:\w+\.)+\w+', desc_line)
            for re_word in re_word_list:
                deprecated_list.append(re_word)
        flag -= 1
    return deprecated_list


def get_else_deprecated_api(desc: str):
    deprecated_list = []
    desc_line_list = desc.split('*')
    for desc_line in desc_line_list:
        deprecated_list.extend(get_deprecated_api_in_string(desc_line, 'deprecated '))
        deprecated_list.extend(get_deprecated_api_in_string(desc_line, 'Deprecated '))
        deprecated_list.extend(get_deprecated_api_in_string(desc_line, 'use '))
        deprecated_list.extend(get_deprecated_api_in_string(desc_line, 'Use '))
        deprecated_list.extend(get_deprecated_api_in_string(desc_line, ' instead'))
        deprecated_list.extend(get_deprecated_api_in_string(desc_line, ' Instead'))
        deprecated_list.extend(get_deprecated_api_in_string(desc_line, 'Replace by '))
        deprecated_list.extend(get_deprecated_api_in_string(desc_line, 'replace by '))
    return deprecated_list


def get_deprecated_api_in_string(string: str, substr: str):
    result = []
    try:
        index = string.index(substr)
        re_word_list = re.findall('[\s]+([\w.]+\([\w\s,.]*\))', string)
        for re_word in re_word_list:
            if string.index(re_word) > index:
                result.append(re_word)
        return result
    except ValueError:
        return []


df_for_diff_name_class: DataFrame


def add_df(df: DataFrame, param1: str, param2):
    length = len(df.index)
    df.loc[length, "class_from"] = param1
    df.loc[length, "class_to"] = param2


if __name__ == '__main__':
    df_for_diff_name_class = pd.DataFrame({
        'class_from': [],
        'class_to': [],
    },
    )
    dir_files = os.listdir('./res_java')
    dir_files_len = len(dir_files)
    for dir_files_index in range(0, dir_files_len):
        print('====' + '(' + str(dir_files_index) + '/' + str(dir_files_len) + ')===' + dir_files[
            dir_files_index] + '=========')
        read_json_dir('./res_java/' + dir_files[dir_files_index])
    df_for_diff_name_class.to_excel("./diff_name_class.xlsx")
