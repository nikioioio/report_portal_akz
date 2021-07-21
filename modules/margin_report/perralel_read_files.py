import pandas as pd

def get_files(*args):
    if args[0][2] == 'ost_nach':
        df = pd.read_excel(args[0][0],sheet_name=args[0][1], index_col=0)
        return df
    if args[0][2] == 0:
        df = pd.read_excel(args[0][0], sheet_name=args[0][1])
        return df
    else:
        df = pd.read_excel(args[0][0], sheet_name=args[0][1],header=args[0][2])
        return df
