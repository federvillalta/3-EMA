#!/usr/bin/env python
# coding: utf-8

# In[489]:


# Expand output to show more rows, columns, and width.
import pandas as pd
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 50000)


# In[490]:


# !pip install yfinance --user
# !pip install mplfinance --user
import yfinance as yf
import mplfinance as mpf
from datetime import datetime
import matplotlib.pyplot as plt
sd = datetime(2022, 8, 29)
ed = datetime(2022, 9, 2)
df = yf.download(tickers='^IXIC', start=sd, end=ed, interval="1m")
mpf.plot(df,type='candle',volume=False)


# In[491]:


df.head()


# In[492]:


#df[['Close', 'ema-short', 'ema-mid', 'ema-long']].plot()
df1 = df.copy()
trend_lag  = 10

df1['ema-short'] = df1['Close'].shift(1).ewm(alpha=(2/(9+1))).mean()
df1['ema-short-trend'] = df1['ema-short'] - df1['ema-short'].shift(trend_lag)

df1['ema-mid'] = df1['Close'].shift(1).ewm(alpha=(2/(50+1))).mean()
df1['ema-mid-trend'] = df1['ema-mid'] - df1['ema-mid'].shift(trend_lag)
df1['lower_threshold'] = df1['ema-mid'] * 0.99995
df1['higher_threshold'] = df1['ema-mid'] * 1.00015

df1['ema-long'] = df1['Close'].shift(1).ewm(alpha=(2/(100+1))).mean()

df1['ema-long-trend'] = df1['ema-long'] - df1['ema-long'].shift(trend_lag)



display(df1.shape)

apdict = mpf.make_addplot(df1[650:700][['ema-short', 'ema-mid', 'ema-long', 'lower_threshold', 'higher_threshold']])
mpf.plot(df1[650:700],type='candle',volume=False, figsize=(20,10), addplot=apdict)
display(df1.shape)


df1.dropna(inplace=True)
df1.reset_index(inplace=True)
display(df1.head())


# ### enter rules
# - All exponential moving average in same trend and space between them 
# - candle breaking the 20-ema with an opposite trend
# - next candle breaking the 20-ema favor to trend
# - enter posision with stop-loss as the min of the previous candle if bullish, or max is the previous candle if bearish
# - take profit as 1:1 in favor of the trend
# 
# 

# In[493]:


display(df1.head(), df1.shape)


# In[494]:


state = []
hist = []
stop_loss = []
take_profit = []
for i in df1.index:
    if len(hist) < 1:
        hist.append(0)
    
    elif len(state) < 1:
        print(i)
        
    
        #################### Entry rules #############
        
        
        # Bullish rules
        if (df1['ema-short-trend'][i] > 0) and (df1['ema-mid-trend'][i] > 0) and (df1['ema-long-trend'][i] > 0):
            print('what')

            if (df1['ema-short'][i] > df1['higher_threshold'][i]) and (df1['ema-long'][i] < df1['lower_threshold'][i]):
                print(df1['Datetime'][i])
                print(df1['Close'][i-1])
                print(df1['ema-short'][i-1])
                
                print(df1['Close'][i])
                print(df1['ema-short'][i])
                print(' ')
                print(' ')

                if (df1['Close'][i-1] < df1['ema-short'][i-1]) and (df1['Close'][i] > df1['ema-short'][i]):
                    print('hello')
                    hist.append(1)
                    state.append(1)
                    stop_loss.append(df1['Open'][i])
                    take_p = df1['Close'][i] - df1['Open'][i]
                    take_profit.append(df1['Close'][i] + take_p)
                    
                else:
                    hist.append(0)
                    
            else:
                hist.append(0)
                    
        # Bearish rules
        elif (df1['ema-short-trend'][i] < 0) and (df1['ema-mid-trend'][i] < 0) and (df1['ema-long-trend'][i] < 0):

            if (df1['ema-short'][i] < df1['lower_threshold'][i]) and (df1['ema-long'][i] > df1['higher_threshold'][i]):
                
                print('now')

                if (df1['Close'][i-1] > df1['ema-short'][i-1]) and (df1['Close'][i] < df1['ema-short'][i]):
                    print(df1['Datetime'][i])
                    print(df1['Close'][i-1])
                    print(df1['ema-short'][i-1])

                    print(df1['Close'][i])
                    print(df1['ema-short'][i])
                    print(' ')
                    print(' ')
                    hist.append(-1)
                    state.append(-1)
                    stop_loss.append(df1['Open'][i])
                    take_p = df1['Open'][i] - df1['Close'][i]
                    take_profit.append(df1['Close'][i] - take_p)
                    
                else:
                    hist.append(0)
                
            else:
                hist.append(0)
                    
                    
        else:
            print('wtf')
            hist.append(0)
            
    elif state[-1] == 1:
        print('bullish')
        if (df1['Open'][i] <= stop_loss[-1]) or (df1['Open'][i] >= take_profit[-1]):
            hist[-1] = 0
            hist.append(0)
            state.clear()
            stop_loss.clear()
            take_profit.clear()
        elif (df1['Close'][i] <= stop_loss[-1]) or (df1['Close'][i] >= take_profit[-1]):
            hist.append(0)
            state.clear()
            stop_loss.clear()
            take_profit.clear()
            
        else:
            hist.append(1)
            state.append(1)
            
    elif state[-1] == -1:
        print(df1['Datetime'][i])
        print('stop_loss')
        print(stop_loss[-1])
        print(df1['Open'][i])
        
        if (df1['Open'][i] >= stop_loss[-1]) or (df1['Open'][i] <= take_profit[-1]):
            hist[-1] = 0
            hist.append(0)
            state.clear()
            stop_loss.clear()
            take_profit.clear()
            
        elif (df1['Close'][i] >= stop_loss[-1]) or (df1['Close'][i] <= take_profit[-1]):
            hist.append(0)
            state.clear()
            stop_loss.clear()
            take_profit.clear()
            
        else:
            hist.append(-1)
            state.append(-1)
        
        
            
            
    


# In[495]:


df1.shape


# In[498]:


df_plot = df1.copy()
df_plot.set_index('Datetime', inplace=True)
df_plot = df_plot['2022-08-29 10:30':'2022-08-31 11:30']

apdict = mpf.make_addplot(df_plot[['ema-short', 'ema-mid', 'ema-long', 'lower_threshold', 'higher_threshold']])
mpf.plot(df_plot,type='candle',volume=True, figsize=(20,10), addplot=apdict)
display(df_plot.shape)


# In[497]:


df2 = df1.copy()
df2['hist'] = hist
df2.set_index('Datetime', inplace=True)

#df2 = df2[['Open', 'High', 'Low', 'Close', 'hist']]
df2['returns'] = (df2['Close'] - df2['Close'].shift())/ df['Close'].shift()
df2['hist'] = df2['hist'].shift(1)
df2['strat-ret'] = df2['returns'] * df2['hist'] * 10
df2[['returns', 'strat-ret']].cumsum().plot()



# In[ ]:




