# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 16:52:08 2018

@author: opuser1
"""
import pandas as pd
import itertools
import pickle
from sklearn.linear_model import LogisticRegression
logreg = LogisticRegression()
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(random_state=1)
#defining random state allows generation of same results at all times.
from sklearn import metrics
iterations=1
#importing train set and test set
df=pd.read_excel('Complete_Das.xlsx','Combined')#train set ;High:1, Medium+Low:0,NA:-1
df_test=df=pd.read_excel('corning.xlsx','test_set')#High:1, Medium+Low:0,NA:-1
#some data accumulators 
report_data=[]
comb_list=[]

array=['LoC','NoFC','NoBC','FR','RL','TtG']
loc='test2'
    
def save_model(model_param):
    dump_file=open(loc+'/dump_model.obj','wb')
    X=df[model_param]
    Y=df['EoO'] #target parameter
    #model fitting, training
    
    clf=rf.fit(X, Y)
    train_accuracy=clf.score(X, Y)
    print "Train Accuracy:",train_accuracy
    pickle.dump(clf,dump_file)

def predictions(pred):
    submission=pd.DataFrame({
            "Patent Number":df['PatNo'],
            "Extent of Overlap":pred
            })
    submission.to_csv(loc+'/Classified_patents'+str(index)+'.csv',index=False)

    
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
    
    rowdata=lines[5].split('     ')
    row['Total_precision']=float(rowdata[1])
    row['Total_recall']=float(rowdata[2])
    row['Total_f1_score']=float(rowdata[3])
    row['Total_support']=float(rowdata[4])
    report_data.append(row) 
    #print report_data

def getCombinations(array):
    combinations=[]
    for i in range(len(array)):
        combinations.append(list(itertools.combinations(array,i+1)))
    for i in range (len(combinations)):
        for j in range(len(combinations[i])):
            comb_list.append(list(combinations[i][j]))
    #code below can be used to generate a csv of combination of variables        
    #comb_frame=pd.DataFrame(comb_list)
    #comb_frame.to_csv('observations/00combinationsOfvariables.csv',index=False)        
    #print comb_list
            

#main
getCombinations(array)
        
index=0
for i in range(len(comb_list)):
    temp=comb_list[i]
    #col=['LoC','NoFC','NoBC','FR','RL'] I need a function to generate combinations of this 
    col=temp#['LoC','NoFC'] #paramters used for training
    X=df[col]
    Y=df['EoO'] #target parameter
    
    #model fitting, training
    
    clf=rf.fit(X, Y)
    train_accuracy=clf.score(X, Y)
    print "Train Accuracy:",train_accuracy
    #testing
        
    X3_test = df_test[col]
    Y3_test = df_test['EoO']
    Y3test_pred = rf.predict(X3_test)
    predictions(Y3test_pred)
    test_accuracy=rf.score(X3_test, Y3_test)
    print('Accuracy of logistic regression classifier on test set: {:.2f}'.format(test_accuracy))
    report=metrics.classification_report(Y3_test,Y3test_pred)
    #print report
    getClassificationReportSorted(report)
    index+=1
    print index
        
dict_frame=pd.DataFrame(report_data)# can use orient=''precision0''
dict_frame.to_csv(loc+'/classification_report_'+loc+'.csv',index=False)
del report_data[:]



#save_model(['LoC','NoFC'])

    

#Free some RAM
#todo(done): create permutations function, nomeculature for the csv, do something with the data
#Dumping Models 
