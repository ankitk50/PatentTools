# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 16:52:08 2018

@author: opuser1
"""

#import numpy as np
import pandas as pd
import itertools
#import matplotlib.pyplot as plt
#import seaborn as sb
from sklearn.model_selection import train_test_split
#import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
iterations=5
df=pd.read_excel('Complete_Das.xlsx','Combined')#High:1, Medium+Low:0,NA:-1
df_new=pd.DataFrame()
report_data=[]
combinations=[]
comb_list=[]
array=['LoC','NoFC']
#array=['LoC','NoFC','NoBC','FR','RL']
#
def getClassificationReport(report):
    #this fucntion is not used due to diifrent layout used in excel recording!!
    lines=report.split('\n')
    for line in lines[2:-3]:
        row={}
        rowdata=line.split('     ')
        row['class']=rowdata[2]
        row['precision']=float(rowdata[3])
        row['recall']=float(rowdata[4])
        row['f1_score']=float(rowdata[5])
        row['support']=float(rowdata[6])
        report_data.append(row)

def getClassificationReportSorted(report):
    lines=report.split('\n')
    row={}
    rowdata=lines[2].split('     ')
    
    row['precision0']=float(rowdata[3])
    row['recall0']=float(rowdata[4])
    row['f1_score0']=float(rowdata[5])
    row['support0']=float(rowdata[6])
    rowdata=lines[3].split('     ')
    
    row['precision1']=float(rowdata[3])
    row['recall1']=float(rowdata[4])
    row['f1_score1']=float(rowdata[5])
    row['support1']=float(rowdata[6])
    report_data.append(row)
    rowdata=lines[5].split('     ')
    
    row['Total_precision']=float(rowdata[1])
    row['Total_recall']=float(rowdata[2])
    row['Total_f1_score']=float(rowdata[3])
    row['Total_support']=float(rowdata[4])
    report_data.append(row)    

def getCombinations(array):
    for i in range(len(array)):
        combinations.append(list(itertools.combinations(array,i+1)))
    for i in range (len(combinations)):
        for j in range(len(combinations[i])):
            comb_list.append(list(combinations[i][j]))
    print comb_list            
index=0    
#main
getCombinations(array)        

for i in range(len(comb_list)):
    temp=comb_list[i]
    #col=['LoC','NoFC','NoBC','FR','RL'] I need a function to generate combinations of this 
    col=temp#['LoC','NoFC'] #paramters used for training
    for k in range(iterations):
        train, test = train_test_split(df,test_size=0.2)
        X=train[col]
        Y=train['EoO'] #target parameter
        #model fitting, training
        logreg = LogisticRegression()
        clf=logreg.fit(X, Y)
        train_accuracy=clf.score(X, Y)
        #testing
        X3_test = test[col]
        Y3_test = test['EoO']
        Y3test_pred = logreg.predict(X3_test)
        test_accuracy=logreg.score(X3_test, Y3_test)
        print('Accuracy of logistic regression classifier on test set: {:.2f}'.format(test_accuracy))
        report=metrics.classification_report(Y3_test,Y3test_pred)
        print report
        getClassificationReportSorted(report)
    dict_frame=pd.DataFrame(report_data)
    dict_frame.to_csv('c_report_'+str(index)+'_.csv',index=False)
    report_data=[]
    index=index+1
    print index
 

#todo(done): create permutations function, nomeculature for the csv, do something with the data
#Dumping Models 
