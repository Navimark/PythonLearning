from pickletools import pyint


# !/usr/local/bin/python3
# -*- coding: utf-8 -*-
#

__doc__ = """
过滤出指定的 .strings 文件中，没有被代码引用的翻译字符串
"""

import os
import sys
import re

def read_lines(file_path):
    with open (file_path, 'r') as rf:
        while True:
            try:
                line = rf.readline()
            except UnicodeDecodeError as e:
                print("打不开:{},异常:{}".format(file_path, e))
            else:
                if line:
                    yield line
                else:
                    break

class TranslateInfo:
    def __init__(self, key, val="-") -> None:
        self.key = key
        self.val = val
    def __str__(self) -> str:
        return "key: {} ,val: {}\n\n".format(self.key, self.val)
    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, TranslateInfo) and self.key == __o.key
    def __repr__(self) -> str:
        return self.__str__()
    def __hash__(self) -> int:
        return hash(self.key)

def travel_dir(root_dir, check):
    for root_path, dir_list, file_list in os.walk(root_dir):  
        for file_name in file_list: # 所有文件名
            ext_name = os.path.splitext(file_name)[-1][1:]
            if check(ext_name, file_name):
                yield os.path.join(root_path, file_name)

def read_contents(file_path=''):
    """
    读取文件，返回移除单行注释和多行注释后的按行迭代器)
    """
    def read_m_file(path=''):
        return '\n'.join(read_lines(file_path=path))

    def _remove_comments(string):
        pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
        regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

        def _replacer(match):
            if match.group(2) is not None:
                return ""
            else:
                return match.group(1)

        return regex.sub(_replacer, string)

    file_str = _remove_comments(read_m_file(path=file_path))
    return filter(lambda x:len(x) != 0, file_str.split('\n'))

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print("参数错误")
        exit(0)

    project_folder = sys.argv[1]

    all_localze_strs_in_code = set()
    source_file_pattern = 'WPLocalizedString\(@"(.*?)"[\s]*,'
    for source_file in travel_dir(root_dir=project_folder, check=lambda x, _: x in ["h","mm","m"]):
        for single_line in read_lines(file_path=source_file):
            ret = re.search(source_file_pattern, single_line)
            if ret:
                all_localze_strs_in_code.add(TranslateInfo(key=ret.group(1)))
    
    all_localza_in_localizable_file = set()
    translate_pattern = '"(.*?)"[\s]*=[\s]*"(.*?)";'
    except_char = ["-", "_","."]
    for source_file in travel_dir(root_dir=project_folder, check=lambda x, f: x in ["strings"] and 'Localizable.strings' in f and '.bundle' not in f):
        for single_line in read_lines(file_path=source_file):
            ret = re.search(translate_pattern, single_line)
            if ret:
                tkey = ret.group(1)
                if len([True for x in except_char if x in tkey]) == 0 and \
                    len([True for x in tkey if u'\u4e00' <= x <= u'\u9fff']) == 0: # 不包含中文
                    all_localza_in_localizable_file.add(TranslateInfo(key=tkey, val=ret.group(2)))


    print("源码翻译长度:{}, .strings长度:{}".format(len(all_localze_strs_in_code), len(all_localza_in_localizable_file)))


    unused = all_localza_in_localizable_file - all_localze_strs_in_code
    print("未使用:{}".format(unused))
    
