#!/usr/bin/env python
# coding: utf-8

# # EMA-Strategy Interactive Brokers execution

# In[1]:


import ibapi


# In[2]:


import sys
print(sys.executable)
print(sys.version)
print(sys.version_info)


# In[28]:


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

import threading
import time


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 2 and reqId == 1:
            print('The current ask price is: ', price)

def run_loop():
    app.run()

app = IBapi()
app.connect('127.0.0.1', 7497, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
apple_contract = Contract()
apple_contract.symbol = 'AAPL'
apple_contract.secType = 'STK'
apple_contract.exchange = 'SMART'
apple_contract.currency = 'USD'

#Request Market Data
app.reqMktData(1, apple_contract, '', False, False, [])

time.sleep(10) #Sleep interval to allow time for incoming price data
app.disconnect()


# In[4]:


# from ibapi.client import EClient
# from ibapi.wrapper import EWrapper
# from ibapi.contract import Contract

# import threading
# import time

# class IBapi(EWrapper, EClient):
#     def __init__(self):
#         EClient.__init__(self, self)
#     def historicalData(self, reqId, bar):
#         print(f'Time: {bar.date} Close: {bar.close}')

# def run_loop():
#     app.run()

# app = IBapi()
# app.connect('127.0.0.1', 7497, 123)

# #Start the socket in a thread
# api_thread = threading.Thread(target=run_loop, daemon=True)
# api_thread.start()

# time.sleep(1) #Sleep interval to allow time for connection to server

# #Create contract object
# eurusd_contract = Contract()
# eurusd_contract.symbol = 'EUR'
# eurusd_contract.secType = 'CASH'
# eurusd_contract.exchange = 'IDEALPRO'
# eurusd_contract.currency = 'USD'

# #Request historical candles
# app.reqHistoricalData(1, eurusd_contract, '', '2 D', '30 mins', 'BID', 0, 2, False, [])

# time.sleep(5) #sleep to allow enough time for data to be returned
# app.disconnect()


# In[ ]:


help(EWrapper)


# In[4]:


from ibapi.ticktype import TickTypeEnum

for i in range(91):
    print(TickTypeEnum.to_str(i), i)


# In[4]:


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *

import threading
import time

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)
        
    def error(self, reqId, errorCode, errorString):
        if errorCode == 202:
            print('order canceled') 

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)


def run_loop():
    app.run()

#Function to create FX Order contract
def FX_order(symbol):
    contract = Contract()
    contract.symbol = symbol[:3]
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'
    contract.currency = symbol[3:]
    return contract

def STK_order_buy(symbol, quantity):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    
    #Create stop loss order object
    stop_order = Order()
    stop_order.action = 'SELL'
    stop_order.totalQuantity = quantity
    stop_order.orderType = 'STP'
    stop_order.auxPrice = '1.09'
    stop_order.orderId = app.nextorderId
    app.nextorderId += 1
    stop_order.parentId = order.orderId
    order.transmit = True
    
    #Create stop loss order object
    takeprofit_order = Order()
    takeprofit_order.action = 'SELL'
    takeprofit_order.totalQuantity = quantity
    takeprofit_order.orderType = 'STP'
    stop_order.auxPrice = '1.09'
    stop_order.orderId = app.nextorderId
    app.nextorderId += 1
    stop_order.parentId = order.orderId
    order.transmit = True
    
def STK_order_sell(symbol, quantity):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    
    #Create stop loss order object
    stop_order = Order()
    stop_order.action = 'BUY'
    stop_order.totalQuantity = quantity
    stop_order.orderType = 'STP'
    stop_order.auxPrice = '1.09'
    stop_order.orderId = app.nextorderId
    app.nextorderId += 1
    stop_order.parentId = order.orderId
    order.transmit = True
    
    #Create stop loss order object
    takeprofit_order = Order()
    takeprofit_order.action = 'BUY'
    takeprofit_order.totalQuantity = quantity
    takeprofit_order.orderType = 'STP'
    stop_order.auxPrice = '1.09'
    stop_order.orderId = app.nextorderId
    app.nextorderId += 1
    stop_order.parentId = order.orderId
    order.transmit = True
    

app = IBapi()
app.connect('127.0.0.1', 7497, 123)

app.nextorderId = None

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

#Check if the API is connected via orderid
while True:
    if isinstance(app.nextorderId, int):
        print('connected')
        break
    else:
        print('waiting for connection')
        time.sleep(1)

#Create order object
enter_signal = 'BUY'

order = Order()
order.action = enter_signal
order.totalQuantity = 10
order.orderType = 'LMT'
order.lmtPrice = '160'

#Place order

if order.action = 'BUY'
    app.placeOrder(app.nextorderId, STK_order_buy('AAPL', quantity=order.totalQuantity), order)
    
if order.action = 'SELL':
    app.placeOrder(app.nextorderId, STK_order('AAPL', quantity=order.totalQuantity), order)
    
#app.nextorderId += 1

time.sleep(3)

#Cancel order 
print('cancelling order')
app.cancelOrder(app.nextorderId)

time.sleep(3)
app.disconnect()


# In[ ]:




