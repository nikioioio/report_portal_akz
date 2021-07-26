import datetime
import pandas as pd

# функция для корректировки в тип datetime столбцов в 0 иерехией столбцов
def replace_to_correct_datetime(df):
    l = list(df.columns)

    for ind, col in enumerate(df.columns):
        try:
            l[ind] = datetime.datetime.fromtimestamp((int(l[ind]) - 25569) * 86400)
        except (TypeError, ValueError):
            pass

    df.columns = l

    return df

# функция для корректировки в тип datetime столбцов c иерархией столбцов
def replace_to_correct_datetime_erarh(df):
    l = list(df.columns)

    for ind, col in enumerate(df.columns):
        l[ind] = list(l[ind])
        for ind1, el in enumerate(l[ind]):
            try:
                l[ind][ind1] = datetime.datetime.fromtimestamp((int(l[ind][ind1]) - 25569) * 86400)
            except (TypeError, ValueError):
                pass

        if ind1 == len(l[ind]) - 1:
            l[ind] = tuple(l[ind])

    df.columns = pd.MultiIndex.from_tuples(l)

    return df


# функция для параллельного считывания файлов
def get_files(*args):
    if args[0][2] == 'ost_nach':
        df = pd.read_excel(args[0][0],sheet_name=args[0][1], index_col=0)
        return df
    if args[0][2] == 0:
        df = pd.read_excel(args[0][0], sheet_name=args[0][1])
        df = replace_to_correct_datetime(df)
        return df
    else:
        df = pd.read_excel(args[0][0], sheet_name=args[0][1],header=args[0][2])
        df = replace_to_correct_datetime_erarh(df)
        return df
