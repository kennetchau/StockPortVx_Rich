import requests
import pandas as pd
from rich.live import Live
from rich.console import Console
from rich.table import Table

def read_json(path:str)->pd.DataFrame:
    df1 = pd.read_json(path)
    return df1

def returnTables(df:pd.DataFrame)->list:
    df['Book Cost'] = df['Quantity'] * df['Cost']
    dfStockPortOver = df.drop(columns = ['Date']).groupby(by = "Symbol").sum().reset_index(drop=False)
    dfStockPortOver = dfStockPortOver[["Symbol", "Quantity", "Book Cost"]]
    return dfStockPortOver.sort_values(by = "Book Cost", ascending = False)

def drawTable(df:pd.DataFrame, title:str)->Table:
    table = Table(title = title, title_justify = 'left')
    
    # Adding columns
    for item in df:
        table.add_column(item)

    # Add rows
    for item in df.to_numpy():
        table.add_row(item[0],f'{item[1]:,}',f'$ {item[2]:,.2f}')

    return table


def main():
    dataPath = 'data/data.json'

    # read the json for the stock Portfolio
    df = read_json(dataPath)
    dfStockPortOver = returnTables(df)
    table = drawTable(dfStockPortOver, "Stock Portfolio")

    console = Console()
    console.print(table)



if __name__ == '__main__':
    main()
