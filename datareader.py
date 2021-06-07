import datetime
import pandas as pd
import fix_yahoo_finance as yf
import pandas_datareader.data as web
import numpy as np
import neal
import dimod
from dwave.system import DWaveSampler
import random
import hybrid

## GLOBAL VARIABLES ##

# Money that can be invested
Ai = 50
Aj = 50
# Total budget
B = 200

#Dictorionary J and h terms
J = {}
h = {}

def covariance(a,b):
    return a.cov(b)

def hi(name, price, returns, cov):

    # mean expected return
    E = np.mean(returns)

    # hi = -(1/2)((1/3)*cov(Ri,Ri) + (1/3)Ai^2 - (1/3)E(Ri) - 2B(1/3)*Ai)
    h_term = -0.5*((1/3)*cov + (1/3)* (Ai ** 2) - (1/3)* E - 2*B*(1/3)*Ai)
    h[name] = h_term

def Ji(name_i, name_j, cov):
    # Ji,j = -(1/4)((1/3)*cov(Ri,Rj) + (1/3)AiAj)
    coupler = -(0.25)*((1/3)*cov + ((1/3)*Ai*Aj))
    J[(name_i, name_j)] = coupler

start = datetime.datetime(2018,1,3)       
end = datetime.datetime(2021,1,1)
all_data = {ticker: web.get_data_yahoo(ticker,start,end)
          for ticker in ['AAPL','IBM','MSFT','GOOGL']}	  
price = pd.DataFrame({ticker:data['Adj Close']
                    for ticker,data in all_data.items()})
volume = pd.DataFrame({ticker:data['Volume']
                     for ticker,data in all_data.items()})
returns = price.pct_change()      #calculate the percentage of the price

returns = returns.dropna()

print('-' * 55)
print(returns.tail())
    
cov_apple = covariance(returns['AAPL'], returns['AAPL'])
print('-' * 55)
print(f' Sampleset sorted on energy')
cov_ibm = covariance(returns['IBM'], returns['IBM'])
cov_msft = covariance(returns['MSFT'], returns['MSFT'])
cov_google = covariance(returns['GOOGL'], returns['GOOGL'])

cov_apple_ibm = covariance(returns['AAPL'], returns['IBM'])
cov_ibm_microsoft = covariance(returns['IBM'], returns['MSFT'])
cov_microsoft_google = covariance(returns['MSFT'], returns['GOOGL'])
cov_google_apple = covariance(returns['GOOGL'], returns['AAPL'])
cov_apple_microsoft = covariance(returns['AAPL'], returns['MSFT'])
cov_ibm_google = covariance(returns['IBM'], returns['GOOGL'])

hi('apple', price['AAPL'],returns['AAPL'], cov_apple)
hi('ibm', price['IBM'],returns['IBM'], cov_ibm)
hi('microsoft', price['MSFT'],returns['MSFT'], cov_msft)
hi('google', price['GOOGL'],returns['GOOGL'], cov_google)

Ji('apple','ibm',cov_apple_ibm)
Ji('apple','microsoft',cov_apple_microsoft)
Ji('ibm','microsoft',cov_ibm_microsoft)
Ji('ibm','google',cov_ibm_google)
Ji('microsoft','google',cov_microsoft_google)
Ji('google','apple',cov_google_apple)

print('-' * 55)

sampler = neal.SimulatedAnnealingSampler()

anneal_schedule = (
(0.0, 0.0), # Start the anneal (time 0.0) at 0.0 (min)
(1.0, 0.25), # Quickly ramp up to 0.25 anneal at 1us
(19.0, 0.75), # Hold the anneal at 0.25 until 19us, then go up to 0.75
(20.0, 1.0) # End the full anneal at 20us
)

# Construct a problem
bqm = dimod.BinaryQuadraticModel.from_ising(h,J)

sampleset = dimod.ExactSolver().sample_ising(h,J)
print(sampleset)
