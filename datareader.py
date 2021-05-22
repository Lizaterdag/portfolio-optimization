import datetime
import pandas as pd
import fix_yahoo_finance as yf
import pandas_datareader.data as web
import numpy as np
import neal
import dimod

def cov(a,b):
    return a.cov(b)

def hi(price, returns, cov):
    #mean price
    Ai = np.mean(price)

    #mean expected return
    E = np.mean(returns)

    # hi = -(1/2)((1/3)*cov(Ri,Rj) + (1/3)Ai^2 - (1/3)E(Ri) - 2B(1/3)*Ai)
    h = (-(1/2)*((1/3)*cov + (1/3)* (Ai ** 2) - (1/3)* E - 2*100*(1/3)*Ai))
    return h

yf.pdr_override()

start = datetime.datetime(2018,1,3)       
end = datetime.datetime(2021,1,1)
all_data = {ticker: web.get_data_yahoo(ticker,start,end)
          for ticker in ['AAPL','IBM','MSFT','GOOGL']}	  #Note: GOOG has become GOOGL
price = pd.DataFrame({ticker:data['Adj Close']
                    for ticker,data in all_data.items()})
volume = pd.DataFrame({ticker:data['Volume']
                     for ticker,data in all_data.items()})
returns = price.pct_change()      #calculate the percentage of the price

returns = returns.dropna()

print(returns.tail())
    
a = cov(returns['AAPL'], returns['IBM'])
b = cov(returns['IBM'], returns['MSFT'])
c = cov(returns['MSFT'], returns['GOOGL'])
d = cov(returns['GOOGL'], returns['AAPL'])

apple = hi(price['AAPL'],returns['AAPL'], a)
ibm = hi(price['IBM'],returns['IBM'], b)
microsoft = hi(price['MSFT'],returns['MSFT'], c)
google = hi(price['GOOGL'],returns['GOOGL'], d)


sampler = neal.SimulatedAnnealingSampler()
bqm = dimod.BinaryQuadraticModel({'a': .5, 'b': -.5}, {('a', 'b'): -1}, 0.0, dimod.SPIN)
# Run with default parameters
sampleset = sampler.sample(bqm)
# Run with specified parameters
sampleset = sampler.sample(bqm, seed=1234, beta_range=[0.1, 4.2],
                                num_reads=1, num_sweeps=20,
                                beta_schedule_type='linear')

h = {apple: 0.0, ibm: 0.0, microsoft: 0.0, google: 0.0}
#energy changes when bias value changes
J = {(apple, ibm): 0.0, (ibm, microsoft): 0.5, (google, apple): 0.3, (apple, microsoft): 0.5, (ibm, google): 0.2}
sampleset = sampler.sample_ising(h, J, num_reads=10)
print(sampleset)

# class maken van code
# functies maken
# data opslaan
# plots maken

