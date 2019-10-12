# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 10:59:17 2018

@author: opuser1
"""

import pandas as pd 


f=open('observations2/00result_test.csv','a')
mean_list=pd.DataFrame()
for i in range(63):
    df=pd.read_csv('observations2/c_report_'+str(i)+'_.csv')
    temp=pd.DataFrame(df.mean()).transpose()
    if i==0:
        temp.to_csv(f)
    else:    
        temp.to_csv(f,header=False)

f.close()   