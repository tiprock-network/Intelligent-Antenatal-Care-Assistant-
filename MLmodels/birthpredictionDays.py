from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error as MSE
import numpy as np
import pandas as pd


dataset=pd.read_csv('labourward2.csv')
dataset.head()

x=np.array(dataset[['BMIScaled','momWeight/10']])

y=np.array(dataset['daysScaled'])

train_x,test_x,train_y,test_y=train_test_split(x,y,test_size=0.3,random_state=1)

#the model itself
gbr_model=GradientBoostingRegressor(n_estimators=200,max_depth=1,random_state=1)

#fit training data
gbr_model.fit(train_x,train_y)

#use test set to give prediction

y_hat=gbr_model.predict(test_x)

def predDays(bmi,weight):
  b=bmi/10
  w=weight/10
  inputs=[b, w]
  param=np.array([inputs])
  pred=gbr_model.predict(param)

  #error=MSE(test_y,y_hat)**0.5 #numebr of days that can be before or after
  
  return pred[0]*100
