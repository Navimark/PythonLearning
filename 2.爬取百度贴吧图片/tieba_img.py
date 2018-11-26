# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
# Created by cz on 2018/11/10 12:27 PM

import urllib
from urllib import request
import random
import time
import os,re
from requests_html import HTMLSession
session = HTMLSession()
request_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
}


def fetch_html_text(temp_url=''):
    re_txt = ''
    try:
        response_data = session.get(temp_url, headers=request_headers)
        re_txt = response_data.html._html.decode('utf-8')
    except Exception as e:
        print("解析遇到错误:",e)
    return re_txt

def fetch_main_tie_urls(keyword=''):
    """
    获取名为"keyword"的贴吧所有分页的内容（即该贴吧中所有的帖子链接）
    """
    if len(keyword) <= 0 :
        return ''
    def batch_url_template(b_pn = 0):
        name = urllib.request.quote(keyword)
        return 'https://tieba.baidu.com/f?kw=' + name + '&ie=utf-8&pn=%d'%b_pn

    def has_next_page(t_html_text=''):
        reg = 'pn=(.*)?" >下一页'
        reg_comp = re.compile(reg)
        return not len(reg_comp.findall(t_html_text)) == 0

    def parse_one_page(t_html_text=''):
        """
        获取当面页面的所有帖子地址
        """
        linkre = re.compile('href=\"(/p/.+?)\"')
        all_short_linkers = linkre.findall(t_html_text)
        t_urls = []
        for link in all_short_linkers:
            detail_link = 'https://tieba.baidu.com' + link
            t_urls.append(detail_link)
        return t_urls,len(t_urls) # 返回 当前页面所有的帖子地址，当前页面帖子数量

    pn = 0
    page_index = 0
    tie_urls = []  # 这个贴吧所有的帖子 url
    while True:
        # 构建第一页 url
        t_url = batch_url_template(b_pn=pn)
        print("解析%s页面的所有帖子链接" % t_url)
        # 拿到这一页的内容
        html_text = fetch_html_text(temp_url=t_url)
        # 解析这一页的所有帖子链接和其数量
        t_tie_urls,page_size = parse_one_page(t_html_text=html_text)
        if page_size > 0:
            # 将这一页的所有帖子链接存起来
            tie_urls = tie_urls + t_tie_urls
            print("\n这一页帖子数量为:%d，分别是"%page_size,t_tie_urls)
            # 判断这一页是否有"下一页"
            if has_next_page(t_html_text=html_text):
                page_index += 1
                # 构造下一页的链接地址，其实是 pn 的值
                pn = page_index * 50
                print("构造下一页的帖子 pn = %d"%pn)
            else:
                print('没有下一页了')
                break
        else:
            print("返回页面数据为0")
            break
    print("keyword= %s 的贴吧，所有帖子总数:%d"%(keyword,len(tie_urls)))
    return tie_urls

def fetch_single_tie_urls(single_tie_url=''):
    """
    获取贴吧中链接为 single_tie_url(https://tieba.baidu.com/p/38734238335) 的单贴的所有分页链接（即该帖子中所有的分页面链接）
    """
    def has_next_page(t_html_text=''):
        reg = 'pn=(.*)?">下一页'
        reg_comp = re.compile(reg)
        return not len(reg_comp.findall(t_html_text)) == 0

    def batch_url_template(b_pn = 0):
        return single_tie_url + '?pn=%d'%b_pn

    pn=1
    img_links = []
    while True:
        # 构造页面 url
        t_url = batch_url_template(b_pn=pn)
        print("当前处理的 url：",t_url)
        # 拿到当前页的 html
        html_text = fetch_html_text(temp_url=t_url)
        # 在 html 中解析出图片的链接
        image_re = re.compile('src=\"(.*?//imgsa.*?/sign=.*?.\\w{3})\"')
        img_links = img_links + image_re.findall(html_text)
        # 判断当前页是否有下一页
        if has_next_page(html_text) and 'come_from' not in t_url:
            print("当前页图片个数:%d，构造下一页的地址pn=%d"%(len(img_links),pn))
            pn = pn + 1
        else:
            print("没有下一页了")
            break
    return img_links

def save_imgs(tieba_name=''):
    if len(tieba_name) <= 0:
        return
    all_tie_urls = fetch_main_tie_urls(keyword=tieba_name)
    print("帖子总个数:%d" % len(all_tie_urls))
    total_imgs = []
    for t_url in all_tie_urls:
        sleep_time = random.randint(1, 10) * 0.1
        time.sleep(sleep_time)
        print("休息%f..." % sleep_time)
        total_imgs += fetch_single_tie_urls(single_tie_url=t_url)
    print(total_imgs)

    pic_total = 0
    for image_link in total_imgs:
        if re.match(r'^https?:/{2}\w.+$', image_link) and '<' not in image_link:
            pass
        else:
            print("不合法的 url:", image_link)
            save_error_url(image_link);
            continue
        try:
            folder = '/Users/cz/Desktop/ImgTieBa/%s'%tieba_name
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(folder + ('/%d.jpg' % pic_total), 'wb') as f:
                f.write(urllib.request.urlopen(image_link).read())
            print('%d.jpg 保存成功' % pic_total)
            pic_total += 1
        except Exception as e:
            print('保存错误', e, 'url:', image_link)

    print("全部完成，总计图片%d张" % pic_total)

def save_error_url(err_url):
    with open("/Users/cz/Desktop/ImgTieBa/err.log",'a') as af:
        af.write(err_url + '\n\n')

if __name__ == '__main__':

    tl = list(set(['杀破狼','荒野大镖客']))
    save_error_url(str(tl))
    for t in tl:
        save_imgs(tieba_name=t)