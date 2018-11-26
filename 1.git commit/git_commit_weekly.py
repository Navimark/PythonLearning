# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
# Created by xx on 2018/11/26 10:31 AM

__doc__ = """
    功能：递归遍历 work_dir 中所有子类目，找到所有的 git 仓库（包括 submodule），在这些仓库中，获取其中指定用户在过去一段时间的 commit log
"""

import os,datetime,subprocess

work_dir = '/Users/xx/Documents/ALLGit'
duration = 7 # 默认获取过去7天的 commit log

def find_all_file_path(validate_fun=None, path=''):
    target_file_paths = []
    for root, _, file_list in os.walk(path):
        for i in file_list:
            target_file_path = os.path.join(root, i)
            if validate_fun and callable(validate_fun) and validate_fun(target_file_path):
                target_file_paths.append(target_file_path)
    return target_file_paths

def output_log_path():
    output_log = '/Users/xx/Desktop'
    end_str = datetime.date.today().strftime('%m-%d')
    begin_str = (datetime.date.today() - datetime.timedelta(days=duration)).strftime('%Y-%m-%d')
    return os.path.join(output_log,'{}至{}周报.log'.format(begin_str,end_str))

if __name__ == '__main__':

    dirs = map(lambda x:x.split('.git')[0],find_all_file_path(lambda x:x.endswith('.git') or '.git/' in x,work_dir))
    dirs = filter(lambda x:os.path.isdir(x) or os.path.isfile(x),dirs)
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    begin_date = (datetime.date.today() - datetime.timedelta(days=duration)).strftime('%Y-%m-%d')
    author_email = ['name1@gmail.com','name2@gmail.com'] # 公司电脑 + 家里电脑 + gitlab 操作记录
    comand_line_dicts = []
    for full_path in set(dirs):
        for author in author_email:
            commnd_str = 'cd {folder}&&git log --oneline --decorate --after={begin} --before={end} --author={author} --pretty=format:"%ai: %s"'.format(folder=full_path,begin=begin_date,end=end_date,author=author)
            comand_line_dicts.append({commnd_str:full_path})

    all_cmds = [''.join(item.keys()) for item in comand_line_dicts]

    with open(output_log_path(),'w') as wf:
        for index in range(len(all_cmds)):
            dict_item = comand_line_dicts[index]
            dict_key = all_cmds[index]
            dict_path = dict_item[dict_key]
            result = str(subprocess.check_output(dict_key, shell=True), encoding='utf-8')
            if len(result) :
                single_log = '路径:{0},日志:\n{1}\n'.format(dict_path,result)
                wf.write(single_log+'\n')
