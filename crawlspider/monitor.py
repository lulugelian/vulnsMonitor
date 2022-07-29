import requests
import os
import time
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
import difflib
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import re

class monitor:
    def __init__(self,url,domain):
        self.url = url
        self.domain = domain

    def filter_tags(self,htmlstr):
        # 先过滤CDATA
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')  # 处理换行
        re_h = re.compile('</?\w+[^>]*>')  # HTML标签
        re_comment = re.compile('<!--[^>]*-->')  # HTML注释
        s = re_cdata.sub('', htmlstr)  # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)  # 去掉style
        s = re_br.sub('\n', s)  # 将br转换为换行
        s = re_h.sub('', s)  # 去掉HTML 标签
        s = re_comment.sub('', s)  # 去掉HTML注释
        # 去掉多余的空行
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = self.replaceCharEntity(s)  # 替换实体
        return s

    def replaceCharEntity(self,htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如>
            key = sz.group('name')  # 去除&;后entity,如>为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    def webMonitor(self,driver):
        try:
            driver.get(self.url)
        except:
            return 3
        driver.refresh()  # 刷新页面
        time.sleep(5)
        result = driver.page_source
        path = './result/%s'%self.domain
        if not os.path.exists("%s/1.html"%path):
            with open("%s/1.html"%path,'w',encoding='utf-8') as f:
                f.write(result)
            return 0
        elif os.path.exists("%s/2.html"%path):
            os.remove("%s/1.html"%path)
            os.rename("%s/2.html"%path, "%s/1.html"%path)
            with open("%s/2.html"%path,'w',encoding='utf-8') as f:
                f.write(result)
            return 1
        else:
            with open("%s/2.html"%path,'w',encoding='utf-8') as f:
                f.write(result)
            return 1

    def compareHtmltest(self,file1,file2):
        with open(file1,'r',encoding='utf-8') as f:
            text1str = f.read()
            text1 = text1str.splitlines(keepends=True)
        with open(file2,'r',encoding='utf-8') as f:
            text2 = f.read().splitlines(keepends=True)
        d = difflib.HtmlDiff()
        htmlContent = d.make_file(text1, text2)
        with open('diff.html', 'w',encoding='utf-8') as f:
            f.write(htmlContent)
        soup = BeautifulSoup(htmlContent, 'html.parser')
        diffContentHtml = soup.find_all("span", class_="diff_add")
        diffContent = ''
        for dif in diffContentHtml:
            diffContent += HTMLParser(dif.text).text()
        diffContentHtml = soup.find_all("span", class_="diff_chg")
        for dif in diffContentHtml:
            diftext = dif.text
            if diftext not in text1str:
                diffContent += HTMLParser(diftext).text()
        return diffContent

    #先提取html文本，在比较
    def compareHtml(self,file1,file2):
        """with open(file1,'r',encoding='utf-8') as f:
            text1str = f.read()
            text1 = text1str.splitlines(keepends=True)
        soup = BeautifulSoup(text1str, 'html.parser')
        with open('html.txt', 'w', encoding='utf-8') as fw:
            for tag in soup.find_all(True):
                fw.write(tag.text)"""
        text1 = ''
        text2 = ''
        with open(file1,'r',encoding='utf-8') as f:
            text1str = f.read()
            text1=self.filter_tags(text1str)
        with open(file2,'r',encoding='utf-8') as f:
            text2str = f.read()
            text2=self.filter_tags(text2str)
        d = difflib.HtmlDiff()
        htmlContent = d.make_file(text1, text2)
        with open('diff.html', 'w',encoding='utf-8') as f:
            f.write(htmlContent)
        soup = BeautifulSoup(htmlContent, 'html.parser')
        diffContentHtml = soup.find_all("span", class_="diff_add")
        diffContent = ''
        for dif in diffContentHtml:
            diffContent += HTMLParser(dif.text).text()
        diffContentHtml = soup.find_all("span", class_="diff_chg")
        for dif in diffContentHtml:
            diftext = dif.text
            if diftext not in text1str:
                diffContent += HTMLParser(diftext).text()
        return diffContent


if __name__=='__main__':
    monitorObj=monitor('http://127.0.0.1/vulnswarn/','127.0.0.1')
    #monitorObj.webMonitor()
    file1 = 'C:\\Data\\PyProject\\vulnsMonitor\\result\\127.0.0.1\\1.html'
    file2 = 'C:\\Data\\PyProject\\vulnsMonitor\\result\\127.0.0.1\\2.html'
    diffContent = monitorObj.compareHtml(file1,file2)
    print(diffContent)

