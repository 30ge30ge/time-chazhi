# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 10:05:31 2019

@author: Administrator
"""
import numpy as np
import pandas as pd
from datetime import datetime, date, time

import talib
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus']=False


df=pd.read_csv("F:/shuju/单位跳价点的参数/0228/记录期权行情-0-HSI1903-00700.HK-58094.HK-2019-02-28 15_14_26.814-2019-02-28.csv",engine='python',sep=",")


data=[]
lastDateTime = None
for index, item in enumerate(df["time"]):
    currDateTime = datetime.combine(date.min, time(*[int(n) for n in item.split(':')]))
    if lastDateTime is None:
        lastDateTime = currDateTime
    elif abs((currDateTime - lastDateTime).total_seconds()) > 0:
        #print(df.loc[index])
        data.append(df.loc[index])
        lastDateTime = currDateTime

a=pd.DataFrame(data)
print(a)
a["TIME"]=a["Time"]+" "+a["time"]
df_new=a[["TIME","期货B","股票B","BQTY","SQTY","庄家B"]]

df_new["期货排序"] = df_new["期货B"].shift(-9)
df_new["期货差"]=df_new["期货排序"]-df_new["期货B"]
df_new["股票排序"] = df_new["股票B"].shift(-9)
df_new["股票差"]=df_new["股票排序"]- df_new["股票B"]
df_new["买卖量"]=df_new["BQTY"]+df_new["SQTY"]
df_new["委B"]=round(df_new["BQTY"]/df_new["买卖量"]*100)
df_new["涨速"]=df_new["期货差"]/df_new["期货B"]
df_new["股票延时10s"]=df_new["股票差"].shift(-9)
qihuo_up=df_new.loc[lambda df_new: df_new.期货差 > 0, :]
qihuo_stop=df_new.loc[lambda df_new: df_new.期货差 == 0, :]
qihuo_down=df_new.loc[lambda df_new: df_new.期货差 < 0, :]
gupiao_up=df_new.loc[lambda df_new: df_new.股票差 > 0, :]
gupiao_stop=df_new.loc[lambda df_new: df_new.股票差 == 0, :]
gupiao_down=df_new.loc[lambda df_new: df_new.股票差 < 0, :]
tiaojian_up=qihuo_up.loc[lambda qihuo_up: qihuo_up.股票差 > 0, :]
tiaojian_down=qihuo_down.loc[lambda qihuo_down: qihuo_down.股票差 < 0, :]
yanshi_up=qihuo_up.loc[lambda qihuo_up: qihuo_up.股票延时10s > 0, :]
yanshi_down=qihuo_down.loc[lambda qihuo_down: qihuo_down.股票延时10s < 0, :]
qihuocha_up=tiaojian_up["期货差"].tolist()
qihuocha_down=tiaojian_down["期货差"].tolist()
mav_up=tiaojian_up["涨速"].tolist()
mav_down=tiaojian_down["涨速"].tolist()
qty_up=tiaojian_up["BQTY"].tolist()
qty_down=tiaojian_down["BQTY"].tolist()
wb_up=tiaojian_up["委B"].tolist()
wb_down=tiaojian_down["委B"].tolist()
print("在10秒间隔中,恒生指数期货上涨的次数为",len(qihuo_up),",下跌次数为",len(qihuo_down))
print("在10秒间隔中,股票指数期货上涨的次数为",len(gupiao_up),",下跌次数为",len(gupiao_down))
print("在10秒间隔中,当恒指上涨时股票延时10s上涨的次数为",len(yanshi_up),"占整个正股上涨的概率比值为%.2f %%"%(len(yanshi_up)/len(gupiao_up)*100))
print("在10秒间隔中,当恒指下跌时股票延时10s下跌的次数为",len(yanshi_down),"占整个正股上涨的概率比值为%.2f %%"%(len(tiaojian_down)/len(gupiao_down)*100))
print("在10秒间隔中,恒指上涨时，成交量均值在",round(np.mean(qty_up)),"委比均值在",round(np.mean(wb_up)),"涨速均值为: %.2f %%"%(np.mean(mav_up)*100),"恒指期货差均值为:",round(np.mean(qihuocha_up)),"正股上涨")
print("在10秒间隔中,恒指下跌时，成交量均值在",round(np.mean(qty_down)),"委比均值在",round(np.mean(wb_down)),"涨速均值为: %.2f %%"%(np.mean(mav_down)*100),"恒指期货差均值为:",round(np.mean(qihuocha_down)),"正股下跌")

df_new["TIME"]=pd.to_datetime(df_new["TIME"])
df_new.set_index("TIME", inplace=True)
print(df_new)
df_new.to_csv("F:/shuju/单位跳价点的参数/0228/延时10秒数据.csv",encoding="utf_8_sig")
