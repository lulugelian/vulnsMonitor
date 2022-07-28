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

class monitor:
    def __init__(self,url,domain):
        self.url = url
        self.domain = domain

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

    def compareHtml(self,file1,file2):
        with open(file1,'r',encoding='utf-8') as f:
            text1 = f.read().splitlines(keepends=True)
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
            diffContent += HTMLParser(dif.text).text()
        return diffContent


if __name__=='__main__':
    monitorObj=monitor('http://127.0.0.1/vulnswarn/','127.0.0.1')
    #monitorObj.webMonitor()
    file1 = 'C:\\Data\\PyProject\\vulnsMonitor\\result\\vti.huaun.com\\1.html'
    file2 = 'C:\\Data\\PyProject\\vulnsMonitor\\result\\vti.huaun.com\\2.html'
    diffContent = monitorObj.compareHtml(file1,file2)
    print(diffContent)

