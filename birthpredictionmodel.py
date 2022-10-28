from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error as MSE
import numpy as np
import pandas as pd
import math

dataset=pd.read_csv('labourward2.csv')
dataset.head()

x=np.array(dataset[['BMIScaled','momWeight/10']])

y=np.array(dataset['timeValueinHrs'])

train_x,test_x,train_y,test_y=train_test_split(x,y,test_size=0.3,random_state=1)

#the model itself
gbr_model=GradientBoostingRegressor(n_estimators=200,max_depth=1,random_state=1)

#fit training data
gbr_model.fit(train_x,train_y)

#use test set to give prediction

y_hat=gbr_model.predict(test_x)

#print predictions
#len(test_x) for range
def timePred(bmi,w):
    b=bmi/10
    wgt=w/10
    inputs=[b, wgt]
    param=np.array([inputs])
    pred=gbr_model.predict(param)

    m=(round((pred[0]-int(pred[0]))*60,0))/100
    h=math.trunc(pred[0])
    time=m+h
    
    if time>0.0 and time<12.0:
         #am
         val=str(round(time,2))
         stringval=val+" "+"am"
         return stringval
    elif time>11.59 and time<23.59:
     time=round(time-12.00,2)#convert into 12hrs clock
    if time>=0.0 and time<=0.59:
        #pm
         val=str(round(time,2))
         stringval=val+" "+"pm"
         return stringval
    elif time>0.59:
        #pm
         val=str(round(time,2))
         stringval=val+" "+"pm"
         return stringval 
    
    #get the RMSE of the model
    #error=MSE(test_y,y_hat)**0.5 #missed by many hours
    
       