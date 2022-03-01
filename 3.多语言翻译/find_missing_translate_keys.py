# !/usr/local/bin/python3
# -*- coding: utf-8 -*-
#

__doc__ = """
以 zh-Hant.lproj/Localizable.strings 为参照，过滤出 ar.lproj/Localizable.strings 中不存在的 key + 过滤出 Hant 中没有使用%@而 ar 中使用了%@的 key

即找出阿语翻译中缺失和不完整的部分
"""

import sys
import re
from tokenize import group

def read_lines(file_path):
    with open (file_path, 'r') as rf:
        while True:
            line = rf.readline()
            if line:
                yield line
            else:
                break

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

class TranslateInfo:
    def __init__(self, key, val) -> None:
        self.key = key
        self.val = val
    def __str__(self) -> str:
        return "key: {} ,val: {}".format(self.key, self.val)
    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, TranslateInfo) and self.key == __o.key
    def __repr__(self) -> str:
        return self.__str__()

def pre_handle_strs(file_path):
    """
    将每一条合法的翻译，转换成 TranslateInfo 数组返回(迭代器)
    """
    pattern = '"(.*?)"[\s]*=[\s]*"(.*?)";'
    def map2Obj(line):
        ret = re.search(pattern, line)
        if ret:
            return TranslateInfo(key=ret.group(1), val=ret.group(2))
    
    return filter(lambda x : x , map(map2Obj, read_contents(file_path=file_path)))

def find_missing_translates(main_strs_path, broken_strs_path):
    b_translates = list(pre_handle_strs(broken_strs_path))
    for m_translate in pre_handle_strs(main_strs_path):
        if m_translate in b_translates:
            sel_b_translates = list(filter(lambda x: x.key == m_translate.key, b_translates))
            if len(sel_b_translates) != 1:
                print("重复记录: {}".format(sel_b_translates))
            b_translate = sel_b_translates[-1]
            if "%@" in b_translate.val and "%@" not in m_translate.val:
                print("格式不对： {}".format(b_translate))
        else:
            print("缺失： {}".format(m_translate))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("参数错误")
    else:
        hant_strs = sys.argv[1]
        ar_strs =  sys.argv[2]
        find_missing_translates(main_strs_path=hant_strs, broken_strs_path=ar_strs)
