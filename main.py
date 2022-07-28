from  crawlspider.monitor import monitor
from SampleTraining.charactorTraining import charactorTraining
import urllib.parse
import time
import schedule
import os
from selenium import webdriver


def requestJob(url,driver,vocabList, p0V, p1V, pSpam):
    resultTag = 0
    domain = urllib.parse.urlparse(url).netloc
    monitorObj = monitor(url,domain)
    if not os.path.exists('./result/%s'%domain):
        os.mkdir('./result/%s'%domain)
    resultLog =  open('./result/%s/result.log'%domain, 'a',encoding='utf-8')
    webMonitorResult = monitorObj.webMonitor(driver)
    if webMonitorResult == 1:
        time.sleep(2)
        file1= './result/%s/1.html'%domain
        file2 = './result/%s/2.html'%domain
        diffContent = monitorObj.compareHtml(file1,file2).replace(" ","")
        if diffContent:
            if charactorTraining().run(vocabList, p0V, p1V, pSpam,diffContent):
                resultLog.write('%s 站点更新漏洞信息：%s\n'%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),diffContent))
                resultTag = 1
            else:
                resultLog.write('%s 站点更新，但不是漏洞信息：%s\n'%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),diffContent))
    elif webMonitorResult == 2:
        resultLog.write('%s 未发现更新\n' % (time.strftime("%Y-%m-%d %H:%M:%S\n", time.localtime())))
    elif webMonitorResult == 3:
        resultLog.write('%s %s请求异常！！！' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    resultLog.close()
    return resultTag


def main(urls,vocabList, p0V, p1V, pSpam):
    # phantomjs下载地址：https://phantomjs.org/download.html
    driver = webdriver.PhantomJS(executable_path=r'./crawlspider/phantomjs.exe')
    for url in urls:
        print('%s 正在请求%s'%( time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),url), flush=True)
        resultTag = requestJob(url,driver,vocabList, p0V, p1V, pSpam)
        if resultTag :
            print('%s %s请求结束,发生漏洞更新!!!' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), url), flush=True)
        else:
            print('%s %s请求结束,未发生更新' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), url), flush=True)
        time.sleep(10)
    driver.quit()

if __name__ == '__main__':
    vocabList, p0V, p1V, pSpam = charactorTraining().sampleTest()#获取机器学习结果
    print('%s 已完成机器学习训练' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    with open('urls.txt', 'r') as f:
        urls = f.read().splitlines()
    main(urls,vocabList, p0V, p1V, pSpam)
    schedule.every(10).minutes.do(main,urls,vocabList, p0V, p1V, pSpam)
    while True:
        schedule.run_pending()
        time.sleep(1)

