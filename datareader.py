import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import datetime
import pandas_datareader.data as DataReader

start= datetime.datetime(2015,1,1)
end= datetime.datetime.today()

df = DataReader.DataReader('IBM', 'yahoo', start, end)
#df = q.to_dfs()['Historical Prices']

df = df.dropna()

print(df)
print(df.describe())

