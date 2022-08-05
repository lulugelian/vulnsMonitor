from  crawlspider.monitor import monitor
from SampleTraining.charactorTraining import charactorTraining
import urllib.parse
import time
import schedule
import os
from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def sendEmail(body_content):
    mail_host = "smtp.163.com"
    # 发件人邮箱
    mail_sender = "******@163.com"
    # 邮箱授权码,注意这里不是邮箱密码,如何获取邮箱授权码,请看本文最后教程
    mail_license = "******"
    # 收件人邮箱，可以为多个收件人
    mail_receivers = ["******@qq.com"]
    mm = MIMEMultipart('related')
    # 邮件主题
    subject_content = """漏洞预警"""
    # 设置发送者,注意严格遵守格式,里面邮箱为发件人邮箱
    mm["From"] = "vulnsMonitor<******@163.com>"
    # 设置接受者,注意严格遵守格式,里面邮箱为接受者邮箱
    mm["To"] = "name<******@qq.com>"
    # 设置邮件主题
    mm["Subject"] = Header(subject_content, 'utf-8')
    # 构造文本,参数1：正文内容，参数2：文本格式，参数3：编码方式
    message_text = MIMEText(body_content, "plain", "utf-8")
    # 向MIMEMultipart对象中添加文本对象
    mm.attach(message_text)
    # 创建SMTP对象
    stp = smtplib.SMTP()
    # 设置发件人邮箱的域名和端口，端口地址为25
    stp.connect(mail_host, 25)
    # 登录邮箱，传递参数1：邮箱地址，参数2：邮箱授权码
    stp.login(mail_sender, mail_license)
    # 发送邮件，传递参数1：发件人邮箱地址，参数2：收件人邮箱地址，参数3：把邮件内容格式改为str
    stp.sendmail(mail_sender, mail_receivers, mm.as_string())
    # 关闭SMTP对象
    stp.quit()

def requestJob(url,driver,vocabList, p0V, p1V, pSpam,sendEmailWarn):
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
                resultTag = 1
                if sendEmailWarn:
                    sendEmail("%s %s %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),url,diffContent))
                    resultLog.write('%s 站点更新漏洞信息：%s,已发送邮件\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), diffContent))
                resultLog.write('%s 站点更新漏洞信息：%s,未发送邮件\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), diffContent))
            else:
                resultLog.write('%s 站点更新，但不是漏洞信息：%s\n'%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),diffContent))
        else:
            resultLog.write('%s 未发现更新\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    elif webMonitorResult == 3:
        resultLog.write('%s %s请求异常！！！' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    resultLog.close()
    return resultTag


def main(urls,vocabList, p0V, p1V, pSpam,sendEmailWarn):
    try:
        # phantomjs下载地址：https://phantomjs.org/download.html
        driver = webdriver.PhantomJS(executable_path=r'./crawlspider/phantomjs.exe')
        for url in urls:
            print('%s 正在请求%s'%( time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),url), flush=True)
            resultTag = requestJob(url,driver,vocabList, p0V, p1V, pSpam,sendEmailWarn)
            if resultTag :
                print('%s %s请求结束,发生漏洞更新!!!' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), url), flush=True)
            else:
                print('%s %s请求结束,未发生更新' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), url), flush=True)
            time.sleep(10)
        driver.quit()
    except:
        print("%s请求异常!"%time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

if __name__ == '__main__':
    vocabList, p0V, p1V, pSpam = charactorTraining().sampleTest()#获取机器学习结果
    sendEmailWarn = 0 #是否设置邮件提醒，1启动，0不启动
    print('%s 已完成机器学习训练' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    with open('urls.txt', 'r') as f:
        urls = f.read().splitlines()
    main(urls,vocabList, p0V, p1V, pSpam,sendEmailWarn)
    schedule.every(10).minutes.do(main,urls,vocabList, p0V, p1V, pSpam)
    while True:
        schedule.run_pending()
        time.sleep(1)

