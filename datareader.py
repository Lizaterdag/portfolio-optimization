import datetime
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import neal
import dimod
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

# Date of assets
start = datetime.datetime(2018,1,3)       
end = datetime.datetime(2021,1,1)

# Assets to work with
assets_dict = {'apple':'AAPL','ibm':'IBM','microsoft':'MSFT','google':'GOOGL'}

assets = []
asset_names = []
cov_assets = {}
cov_assets_coupled = {}

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
    
def price_assets(a):
    all_data = {asset : web.get_data_yahoo(asset,start,end)
          for asset in a} 
    price = pd.DataFrame({asset : data['Adj Close']
                    for asset , data in all_data.items()})
    return price

def returns_assets(a):
    price_all_assets = price_assets(a)
    returns_unclean = price_all_assets.pct_change()
    returns_clean = returns_unclean.dropna()
    return returns_clean

for key, value in assets_dict.items():
    asset_names.append(key)
    assets.append(value)

price = price_assets(assets)
returns = returns_assets(assets) 

# Covariance of the assets with themselves, 4 items
for i in assets:
    cov = covariance(returns[i], returns[i])
    cov_assets[i] = cov
    
# Covariance of the assets with each other, 6 items
for i in range(len(assets)):
    for j in range(i + 1, len(assets)):
        if j < len(assets):
            cov = covariance(returns[assets[i]], returns[assets[j]])
        else:
            j = 0
            cov = covariance(returns[assets[i]], returns[assets[j]])
        cov_assets_coupled[assets[i],assets[j]] = cov
        
for i in range(len(assets)):
    hi(asset_names[i], price[assets[i]], returns[assets[i]], cov_assets[assets[i]])

for key1, key2 in cov_assets_coupled:
    Ji(key1, key2, cov_assets_coupled[key1,key2])

sampler = neal.SimulatedAnnealingSampler()

# Construct a problem
bqm = dimod.BinaryQuadraticModel.from_ising(h,J)

sampleset = dimod.ExactSolver().sample_ising(h,J)
print(sampleset)
