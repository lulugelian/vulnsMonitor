# -*- coding: utf-8 -*-
import numpy as np
import os
import jieba

class charactorTraining:
    def __init__(self):
        pass

    # 判断是否为数字
    def is_number(self,s):
        try:  # 如果能运⾏ float(s) 语句，返回 True（字符串 s 是浮点数）
            float(s)
            return True
        except ValueError:  # ValueError 为 Python 的⼀种标准异常，表⽰"传⼊⽆效的参数"
            pass  # 如果引发了 ValueError 这种异常，不做任何事情（pass：不做任何事情，⼀般⽤做占位语句）
        try:
            import unicodedata  # 处理 ASCII 码的包
            unicodedata.numeric(s)  # 把⼀个表⽰数字的字符串转换为浮点数返回的函数
            return True
        except (TypeError, ValueError):
            pass
            return False

    def MakeWordsSet(self,words_file):
        words_set = set()  # 创建set集合
        with open(words_file, 'r', encoding='utf-8') as f:  # 打开文件
            for line in f.readlines():  # 一行一行读取
                word = line.strip()  # 去回车
                if len(word) > 0:  # 有文本，则添加到words_set中
                    words_set.add(word)
        return words_set  # 返回处理结果

    def createVocabList(self,dataSet):
        resultList=[]
        vocabSet = set([])  # 创建一个空的不重复列表
        stopwords_file = './Sample/stopwords_cn.txt'
        backList = self.MakeWordsSet(stopwords_file)
        for document in dataSet:
            vocabSet = vocabSet | set(document)  # 取并集
        vocabList = list(vocabSet)
        for doc in vocabList:
            if (doc not in backList) and  not self.is_number(doc):
                resultList.append(doc)
        return resultList

    def setOfWords2Vec(self,vocabList, inputSet):
        returnVec = [0] * len(vocabList)  # 创建一个其中所含元素都为0的向量
        for word in inputSet:  # 遍历每个词条
            if word in vocabList:  # 如果词条存在于词汇表中，则置1
                returnVec[vocabList.index(word)] = 1
            else:
                pass
                #print("the word: %s is not in my Vocabulary!" % word)
        return returnVec  # 返回文档向量

    def bagOfWords2VecMN(self,vocabList, inputSet):
        returnVec = [0] * len(vocabList)  # 创建一个其中所含元素都为0的向量
        for word in inputSet:  # 遍历每个词条
            if word in vocabList:  # 如果词条存在于词汇表中，则计数加一
                returnVec[vocabList.index(word)] += 1
        return returnVec  # 返回词袋模型

    def trainNB0(self,trainMatrix, trainCategory):
        numTrainDocs = len(trainMatrix)  # 计算训练的文档数目
        numWords = len(trainMatrix[0])  # 计算每篇文档的词条数
        pAbusive = sum(trainCategory) / float(numTrainDocs)  # 文档属于侮辱类的概率
        p0Num = np.ones(numWords);
        p1Num = np.ones(numWords)  # 创建numpy.ones数组,词条出现数初始化为1，拉普拉斯平滑
        p0Denom = 2.0;
        p1Denom = 2.0  # 分母初始化为2,拉普拉斯平滑
        for i in range(numTrainDocs):
            if trainCategory[i] == 1:  # 统计属于侮辱类的条件概率所需的数据，即P(w0|1),P(w1|1),P(w2|1)···
                p1Num += trainMatrix[i]
                p1Denom += sum(trainMatrix[i])
            else:  # 统计属于非侮辱类的条件概率所需的数据，即P(w0|0),P(w1|0),P(w2|0)···
                p0Num += trainMatrix[i]
                p0Denom += sum(trainMatrix[i])
        p1Vect = np.log(p1Num / p1Denom)  # 取对数，防止下溢出
        p0Vect = np.log(p0Num / p0Denom)
        return p0Vect, p1Vect, pAbusive  # 返回属于侮辱类的条件概率数组，属于非侮辱类的条件概率数组，文档属于侮辱类的概率

    def classifyNB(self,vec2Classify, p0Vec, p1Vec, pClass1):
        p1 = sum(vec2Classify * p1Vec) + np.log(pClass1)  # 对应元素相乘。logA * B = logA + logB，所以这里加上log(pClass1)
        p0 = sum(vec2Classify * p0Vec) + np.log(1.0 - pClass1)
        if p1 > p0:
            return 1
        else:
            return 0


    def textParse(self,bigString):  # 将字符串转换为字符列表
        listOfTokens = list(jieba.cut(bigString, cut_all=False))  # 精简模式，返回一个可迭代的generator
        return listOfTokens  # 除了单个字母，例如大写的I，其它单词变成小写

    def  sampleTest(self):
        docList = []
        classList = []
        folder_list = os.listdir('./Sample/vulnsWarn')
        for folder in folder_list:
            new_folder_path = os.path.join('./Sample/vulnsWarn', folder)
            with open(new_folder_path, 'rb') as f:
                raws = f.readlines()
            for raw in raws:
                wordList = self.textParse(raw)
                docList.append(wordList)
                classList.append(1)  # 标记漏洞样本，1表示是漏洞预警信息
        folder_list = os.listdir('./Sample/normal')
        for folder in folder_list:
            new_folder_path = os.path.join('./Sample/normal', folder)
            with open(new_folder_path, 'rb') as f:
                raws = f.readlines()
            for raw in raws:
                wordList = self.textParse(raw)
                docList.append(wordList)
                classList.append(0)  # 标记非漏洞样本，0表示不是漏洞预警信息
        vocabList = self.createVocabList(docList)  # 创建词汇表，不重复
        trainMat = []
        trainClasses = []  # 创建训练集矩阵和训练集类别标签系向量
        for docIndex in range(len(docList)):  # 遍历训练集
            trainMat.append(self.setOfWords2Vec(vocabList, docList[docIndex]))  # 将生成的词集模型添加到训练矩阵中
            trainClasses.append(classList[docIndex])  # 将类别添加到训练集类别标签系向量中
        p0V, p1V, pSpam = self.trainNB0(np.array(trainMat), np.array(trainClasses))  # 训练朴素贝叶斯模型
        return vocabList,p0V, p1V, pSpam

    def run(self,vocabList,p0V, p1V, pSpam,testStr):
        wordList = self.textParse(testStr)

        wordVector = self.setOfWords2Vec(vocabList, wordList)  # 测试集的词集模型
        return self.classifyNB(np.array(wordVector), p0V, p1V, pSpam)

    def test(self,vocabList,p0V, p1V, pSpam):
        sum=0
        errorNum=0
        with open('./Sample/test/test-vulns.txt', 'r',encoding='utf-8') as f:
            raws = f.readlines()
        for testStr in raws:
            sum+=1
            wordList = self.textParse(testStr)
            wordVector = self.setOfWords2Vec(vocabList, wordList)  # 测试集的词集模型
            if(self.classifyNB(np.array(wordVector), p0V, p1V, pSpam)!=1):
                errorNum += 1
                print("分类错误的测试集：",testStr)
        with open('./Sample/test/test-normal.txt', 'r',encoding='utf-8') as f:
            raws = f.readlines()
        for testStr in raws:
            sum += 1
            wordList = self.textParse(testStr)
            wordVector = self.setOfWords2Vec(vocabList, wordList)  # 测试集的词集模型
            if(self.classifyNB(np.array(wordVector), p0V, p1V, pSpam)!=0):
                errorNum += 1
                print("分类错误的测试集：",testStr)
        print('错误率：%.2f%%' % (float(errorNum) / sum * 100))


if __name__ == '__main__':
    pwd = os.getcwd()
    os.chdir('%s/../'%pwd)
    charactorTraining=charactorTraining()
    vocabList,p0V, p1V, pSpam =  charactorTraining.sampleTest()
    #charactorTraining.test(vocabList,p0V, p1V, pSpam)
    print(charactorTraining.run(vocabList,p0V, p1V, pSpam,"11111"))