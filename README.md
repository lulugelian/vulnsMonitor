## 漏洞预警监控
![](https://camo.githubusercontent.com/d350cc76b2880b7621f80b2aa037d3cb3a8ffda8e5f3374f38548c5c4315d1df/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f7265706f6f672f476974507265792e737667)
### 背景介绍
    
漏洞预警是供应链安全建设中的重要一环，漏洞预警平台众多，传统定制化爬虫耗时且不够灵活。基于机器学习自动识别漏洞预警信息特征，让程序自动判断监控站点更新信息是否是漏洞预警信息，这样只需告知程序要监控的web页面地址即可自动实现站点信息检测。
### 技术实现
    
从华云安、360 POC++等漏洞预警平台收集漏洞预警样本，基于朴素贝叶斯算法训练程序识别漏洞预警信息特征。
每十分钟爬取一次监控页面，对比上一次页面信息，提取差异内容，基于机器学习训练结果让程序判断差异内容是否是漏洞预警信息，如果是则通报。
### 目录介绍
>vulnsMonitor/  
├── crawlspider 爬虫脚本，使用phantomjs渲染js  
│    ├── monitor.py  
│    ├── phantomjs  
│    ├── phantomjs.exe  
│    └── result  
├── result  保存网站爬虫结果以及漏洞预警判断结果  
├── Sample  样本文件  
│    ├── normal  
│    ├── test  
│    └── vulnsWarn  
├── SampleTraining  机器学习训练  
│    ├── charactorTraining.py  训练脚本  
│    ├── p0v.npy  训练结果  
│    ├── p1v.npy  训练结果  
│    ├── pSpam.npy  训练结果  
│    └── vocabList.ini  训练结果  
├── requirements.txt  
├── main.py 启动脚本  
└── urls.txt    监控url列表  

### 快速开始
#### windows环境安装  

```bash
#安装python 3.8.3环境
git clone https://github.com/lulugelian/vulnsMonitor.git
cd vulnsMonitor
python3 -m pip install -r requirements.txt
python3 main.py
```
#### centos7环境安装
```bash 
#安装python 3.8.3环境
sudo yum install yum-utils
sudo yum-builddep python
curl -O https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz
tar xf Python-3.8.3.tgz
cd Python-3.8.3
./configure
make
sudo make install
python3 
#安装程序
git clone https://github.com/lulugelian/vulnsMonitor.git
cd vulnsMonitor
python3 -m pip install -r requirements.txt
vi main.py 修改phantomjs.exe为phantomjs
chmod +x crawlspider/phantomjs
python3 main.py
```
设置邮件提醒（默认不启动）
```bash
修改 main.py 文件
  将sendEmailWarn = 1
  sendEmail函数中配置邮件服务器
```
