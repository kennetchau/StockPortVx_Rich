import requests 
import pandas as pd 
import cred
from rich import print 
from rich.layout import Layout 
from rich.live import Live
from rich.console import Console
from rich.table import Table

class Portfolio:
    def __init__(self, path):
        df = pd.read_json(path)
        df['Book Cost'] = df['Quantity'] * df['Cost']
        dfStockPortOver = df.drop(columns = ['Date']).groupby(by = "Symbol").sum().reset_index(drop=False)
        dfStockPortOver = dfStockPortOver[["Symbol", "Quantity", "Book Cost"]]
        self.dfStockPortRecords = df.sort_values(by='Date', ascending = False).head(10)
        self.dfStockPortOver = dfStockPortOver.sort_values(by = "Book Cost", ascending = False)

    def returnTable(self, choice:str)->pd.DataFrame:
        match choice:
            case 'Overview':
                return self.dfStockPortOver
            case 'records':
                return self.dfStockPortRecords
            case _:
                return None


def drawTable(df:pd.DataFrame, title:str)->Table:
    table = Table(title = title, title_justify = 'left')
    df = df.round(2)
    
    # Adding columns
    for item in df:
        table.add_column(item)

    # Add rows
    for item in df.to_numpy():
        item = [str(element) for element in item]
        table.add_row(*item)

    return table

def drawPortDashboard(table1,table2)->Layout:
    layout = Layout()
    layout.split(
            Layout(name = 'header', size = 3),
            Layout(name = 'body', ratio = 1),
            Layout(name = 'footer', size = 7)
            )

    layout['body'].split_column(
            Layout(name = 'upper', ratio = 1),
            Layout(name = 'stockPortTrading', ratio = 2),
            )
    #layout['upper'].split_row(
    #        Layout(name = 'stockOverView'),
    #        Layout(name = 'right'),
    #        )

    #layout['stockOverView'].update(table1)
    # Comment out the split line until something is added to the second column
    layout['header'].update('Stock Portfolio Tracker')
    layout['upper'].update(table1)
    layout['stockPortTrading'].update(table2)
    return layout


def main():
    dataPath = 'data/data.json'

    # read the json for the stock Portfolio
    dfStockPortOver = Portfolio(dataPath)
    table1 = drawTable(dfStockPortOver.returnTable('Overview'), "Stock Portfolio")
    table2 = drawTable(dfStockPortOver.returnTable('records'), "Stock Transactions")
    layout = drawPortDashboard(table1,table2)
    print(layout)
    

if __name__ == '__main__':
    main()
