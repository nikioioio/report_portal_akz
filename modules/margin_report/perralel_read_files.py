import datetime
import pandas as pd
import calendar


class MyException(Exception):
	pass

# функция для корректировки в тип datetime столбцов в 0 иерехией столбцов
def replace_to_correct_datetime(df,year_report,month_report,sheet_name,filename):

    iter_months = [datetime.datetime(year_report, x, calendar.monthrange(year_report, x)[1], 0, 0) for x in
                   range(1, month_report + 1)]

    l = list(df.columns)

    for ind, col in enumerate(df.columns):
        try:
            # реформат на тип :дата
            l[ind] = datetime.datetime.fromtimestamp((int(l[ind]) - 25569) * 86400)
        except (TypeError, ValueError):
            pass

        # if isinstance(l[ind],datetime.datetime) and iter_months.count(l[ind])!=1:
        #     raise Exception('Отсутствует столбец ' + str(l[ind]) + ' в необходимых столбцах на листе ' + str(sheet_name) + ' в файле ' + str(filename))

    df.columns = l

    return df

# функция для корректировки в тип datetime столбцов c иерархией столбцов
def replace_to_correct_datetime_erarh(df,year_report,month_report,sheet_name):

    iter_months = [datetime.datetime(year_report, x, calendar.monthrange(year_report, x)[1], 0, 0) for x in
                   range(1, month_report + 1)]

    l = list(df.columns)

    for ind, col in enumerate(df.columns):
        l[ind] = list(l[ind])
        for ind1, el in enumerate(l[ind]):
            try:
                # реформат на тип :дата
                l[ind][ind1] = datetime.datetime.fromtimestamp((int(l[ind][ind1]) - 25569) * 86400)
            except (TypeError, ValueError):
                pass

            # raise Exception('Отсутствует столбец ' + str(l[ind]) + ' в необходимых столбцах на листе ' + str(sheet_name))

        if ind1 == len(l[ind]) - 1:
            l[ind] = tuple(l[ind])

    df.columns = pd.MultiIndex.from_tuples(l)

    return df


# функция для параллельного считывания файлов
# args: file, list, sheetname,year,month
def get_files(*args):
    if args[0][2] == 'ost_nach':
        df = pd.read_excel(args[0][0],sheet_name=args[0][1], index_col=0)
        return df
    if args[0][2] == 0:
        df = pd.read_excel(args[0][0], sheet_name=args[0][1])
        df = replace_to_correct_datetime(df,args[0][3],args[0][4],args[0][1],args[0][0])
        return df
    else:
        df = pd.read_excel(args[0][0], sheet_name=args[0][1],header=args[0][2])
        df = replace_to_correct_datetime_erarh(df,args[0][3],args[0][4],args[0][1])
        return df
