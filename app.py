#!/usr/bin/env python3

"""
    This is a simple terminal dashboard build using rich, pandas, termplotlib
    Its purposes is to allow the user to track his stock portfolio from the terminal
    Leveraging twelve data api to pull real time data

    Author: Kenneth Chau
    Build: Python 3.12

"""

import cred
import pandas as pd 
import requests 
import termplotlib as tpl
from datetime import datetime, time
from rich import print 
from rich.align import Align
from rich.console import Console
from rich.layout import Layout 
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

class Portfolio:
    def __init__(self, path):
        df = pd.read_json(path)

        # Set the original df as the trading record table
        self.dfStockPortRecords = df.sort_values(by='Date', ascending = False)
        self.dfStockPortRecords = self.dfStockPortRecords.rename(columns = {'Cost':'Individual Cost'})
        
        # Build the stock portfolio overview table, this table will show the live data of each stock price
        df['Total Cost'] = df['Quantity'] * df['Cost']
        dfStockPortOver = df.drop(columns = ['Date']).groupby(by = "Symbol").sum().reset_index(drop=False)
        dfStockPortOver['Average Cost'] = dfStockPortOver['Total Cost']/dfStockPortOver['Quantity']
        dfStockPortOver = dfStockPortOver[["Symbol", "Quantity", "Average Cost", "Total Cost"]]
        self.dfStockPortOver = dfStockPortOver.rename(columns = {"Total Cost": "Book Cost"})
        currentPrices = self.latestPrice(self.returnUniqueHold())
        self.dfStockPortOver = self.updatePrices(self.dfStockPortOver, currentPrices)
        self.dfStockPortOver = self.dfStockPortOver.sort_values(by = "Market Value", ascending = False)

    def returnTable(self, choice:str)->pd.DataFrame:
        match choice:
            case 'Overview':
                return self.dfStockPortOver.head(5)
            case 'records':
                return self.dfStockPortRecords.head(10)
            case _:
                return None

    # This is the function that will update the price of the table
    def updatePrices(self, currentDf:pd.DataFrame, currentPrice:dict)->pd.DataFrame:
        def applyUpdatesPrices(item):
            try: 
                return float(currentPrice[item]['price'])
            except KeyError:
                return currentDf[currentDf['Symbol'] == item]['Average Cost'].values[0]
        currentDf['Current Price'] = currentDf['Symbol'].apply(applyUpdatesPrices)
        currentDf['Market Value'] = currentDf['Current Price'] * currentDf['Quantity']
        currentDf['% Change'] = (currentDf['Market Value']/currentDf['Book Cost'] - 1)*100
        currentDf['Unrealized Gain or Loss'] = currentDf['Market Value'] - currentDf['Book Cost']
        currentDf = currentDf[["Symbol", "Quantity", "Average Cost","Current Price", "Book Cost", "Market Value", "% Change", "Unrealized Gain or Loss"]]
        return currentDf


    # This is the function that will return the latest price
    def latestPrice(self, stockList:list)->dict:
        listOfTicker = stockList
        # since the api take comma separated values, we will need to format them like so
        listOfTicker_str = ','.join(listOfTicker)
        api_key = cred.api_key
        base_url = cred.base_url
        tickerPrices = requests.get(base_url.format('price',listOfTicker_str, api_key))
        if tickerPrices.status_code == 200:
            return tickerPrices.json()
        else:
            return tickerPrices.status_code

    def returnBookCost(self)->str:
        return str(round(self.dfStockPortOver['Book Cost'].sum(),2))

    def returnMarketValue(self)->str:
        return str(round(self.dfStockPortOver['Market Value'].sum(),2))
    
    def returnUnrealizeGainOrLoss(self)->str:
        return str(round(self.dfStockPortOver['Market Value'].sum()- self.dfStockPortOver['Book Cost'].sum(),2))
    
    def returnUniqueHold(self)->list:
        return self.dfStockPortOver.Symbol.unique().tolist()


def drawTable(df:pd.DataFrame, title:str)->Table:
    table = Table(title = title, title_justify = 'left', expand = True)
    df = df.round(2)
    
    # Adding columns
    for item in df:
        table.add_column(item)

    # Add rows
    for item in df.to_numpy():
        item = [str(element) for element in item]
        table.add_row(*item)

    return table

def drawPortDashboard(current_time, market_open, table1, table2, TotalBookCost, MarketValue, UnrealizeGainOrLoss, Graph)->Layout:
    current_date = datetime.now().strftime("%d %b %Y at %H:%M:%S %Z")
    if market_open:
        marketStatus = Text(f"It is currently {current_time}, Market is open")
        marketStatus.stylize("green")
    else:
        marketStatus = Text(f"It is currently {current_time}, Market is close")
        marketStatus.stylize("red")
    layout = Layout()
    layout.split(
            Layout(name = 'header', size = 3),
            Layout(name = 'MarketStatus', size = 3),
            Layout(name = 'body', ratio = 1),
            Layout(name = 'footer', size = 6)
            )

    layout['body'].split_column(
            Layout(name = 'upper'),
            Layout(name = 'stockPortTrading', ratio = 1),
            )
    layout['upper'].split_row(
            Layout(name = 'stockOverView'),
            Layout(name = 'stockOverViewBar'),
            )
    layout['stockOverView'].split_column(
            Layout(name = 'Cost', size = 4),
            Layout(name = 'stockOverViewTable')
            )
    layout['Cost'].split_row(
            Layout(name = 'TotalBookCost'),
            Layout(name = 'MarketValue'),
            Layout(name = 'UnrealizedGainOrLoss'),
            )
    # Comment out the split line until something is added to the second column
    layout['header'].update(Panel(Align('Stock Portfolio Tracker', align = 'center')))
    layout['MarketStatus'].update(Panel(Align(marketStatus, align = 'left')))
    layout['stockOverViewBar'].update(Panel(Graph, title = 'Portfolio Distribution', title_align = 'center'))
    layout['TotalBookCost'].update(Panel(f"$ {TotalBookCost}", title="Total Book Cost", title_align = 'center'))
    layout['MarketValue'].update(Panel(f"$ {MarketValue}", title="Market Value", title_align = 'center'))
    layout['UnrealizedGainOrLoss'].update(Panel(f"$ {UnrealizeGainOrLoss}", title = "Unrealized Gain or Loss", title_align = 'center'))
    layout['stockOverViewTable'].update(table1)
    layout['stockPortTrading'].update(table2)
    layout['footer'].update(Panel(f'Data updated at {current_date}\nLive Data source from twelve data\nSome data might not be avaliable depends on your api subscription'))
    return layout

def drawGraph(data:pd.DataFrame, xValue:str, yValue:str)->str:
    fig = tpl.figure()
    fig.barh(data[xValue].values, data[yValue].values,force_ascii = True)
    return fig.get_string()

def main():
    # Get current date and time
    dataPath = 'data/data.json'
    
    # read the json for the stock Portfolio
    dfStockPortOver = Portfolio(dataPath)
    
    # Get the current date and time
    current_time = datetime.now().time()
    current_weekdate = datetime.today().weekday()
    
    # Check if market is open
    market_open = current_time >= time(9,30) and current_time <= time(16,00) and (current_weekdate != 5 and current_weekdate != 6)
    
    # Draw the tables and graphs
    table1 = drawTable(dfStockPortOver.returnTable('Overview'), "Top 5 Holdings")
    table2 = drawTable(dfStockPortOver.returnTable('records'), "Stock Transactions")
    Graph = drawGraph(dfStockPortOver.returnTable('Overview'), 'Market Value', 'Symbol')
    
    # Getting some key stats
    totalBookCost = dfStockPortOver.returnBookCost()
    MarketValue = dfStockPortOver.returnMarketValue()
    UGainOrLoss = dfStockPortOver.returnUnrealizeGainOrLoss()
    
    # Draw the layout
    layout = drawPortDashboard(current_time, market_open, table1, table2, totalBookCost, MarketValue, UGainOrLoss, Graph)
    print(layout)
    

if __name__ == '__main__':
    main()
