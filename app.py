import requests 
import pandas as pd 
import cred
from rich import print 
from rich.align import Align
from rich.layout import Layout 
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
from rich.table import Table

class Portfolio:
    def __init__(self, path):
        df = pd.read_json(path)
        df['Total Cost'] = df['Quantity'] * df['Cost']
        dfStockPortOver = df.drop(columns = ['Date']).groupby(by = "Symbol").sum().reset_index(drop=False)
        dfStockPortOver['Average Cost'] = dfStockPortOver['Total Cost']/dfStockPortOver['Quantity']
        dfStockPortOver = dfStockPortOver[["Symbol", "Quantity", "Average Cost", "Total Cost"]]
        dfStockPortOver = dfStockPortOver.rename(columns = {"Total Cost": "Book Cost"})
        self.dfStockPortRecords = df.sort_values(by='Date', ascending = False)
        self.dfStockPortOver = dfStockPortOver.sort_values(by = "Book Cost", ascending = False)

    def returnTable(self, choice:str)->pd.DataFrame:
        match choice:
            case 'Overview':
                return self.dfStockPortOver.head(5)
            case 'records':
                return self.dfStockPortRecords.head(10)
            case _:
                return None

    def returnBookCost(self)->str:
        return str(round(self.dfStockPortOver['Book Cost'].sum(),2))
    
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

def drawPortDashboard(table1,table2,TotalBookCost)->Layout:
    layout = Layout()
    layout.split(
            Layout(name = 'header', size = 3),
            Layout(name = 'body', ratio = 1),
            Layout(name = 'footer', size = 5)
            )

    layout['body'].split_column(
            Layout(name = 'upper'),
            Layout(name = 'stockPortTrading', ratio = 1),
            )
    layout['upper'].split_row(
            Layout(name = 'stockOverView'),
            Layout(name = 'right'),
            )
    layout['stockOverView'].split_column(
            Layout(name = 'Cost', size = 4),
            Layout(name = 'stockOverViewTable')
            )
    layout['Cost'].split_row(
            Layout(name = 'TotalBookCost'),
            Layout(name = 'UnrealizedGainOrLost'),
            )
    # Comment out the split line until something is added to the second column
    layout['header'].update(Panel(Align('Stock Portfolio Tracker', align = 'center')))
    #layout['upper'].update(table1)
    layout['TotalBookCost'].update(Panel(f"Total Book Cost: \n$ {TotalBookCost}"))
    layout['UnrealizedGainOrLost'].update(Panel(f"Unrealized Gain or Lost: \n $"))
    layout['stockOverViewTable'].update(table1)
    layout['stockPortTrading'].update(table2)
    layout['footer'].update(Panel('Data updated at \nLive Data source from'))
    return layout


def main():
    dataPath = 'data/data.json'
    console = Console()
    # read the json for the stock Portfolio
    dfStockPortOver = Portfolio(dataPath)
    table1 = drawTable(dfStockPortOver.returnTable('Overview'), "Top 5 Holdings")
    table2 = drawTable(dfStockPortOver.returnTable('records'), "Stock Transactions")
    totalBookCost = dfStockPortOver.returnBookCost()
    layout = drawPortDashboard(table1, table2, totalBookCost)
    print(layout)
    

if __name__ == '__main__':
    main()
