import pandas as pd

def save_backup(path_backup, arrs):
    try:
        backup = pd.HDFStore(path_backup)
        for arr in arrs:
            backup[str(arr.name)] = arr
        backup.close()
    except:
        backup.close()


# типизируем cтолбцы таблица,
# type_ к какому типу приводим,
# mask по каком услову в столбце типизируем
def retype_multiindex(df, type_, mask, levelForFindMask):
    for col in df.columns:
        try:
            if col[levelForFindMask].find(mask) != -1:
                df.loc[:, col] = df.loc[:, col].fillna(0).astype('int').astype(type_)
        except AttributeError:
            pass
        except ValueError:
            pass
    return df


def retype_index(df, type_, mask):
    for col in df.columns:
        try:
            if col.find(mask) != -1:
                df.loc[:, col] = df.loc[:, col].fillna(0).astype(type_)
        except AttributeError:
            pass
        except ValueError:
            pass
    return df


# Упаковка справочника для insert vpr
def rev_to_dict(ind, find):
    #     ind = ind.astype('str')
    df = pd.DataFrame(index=ind, data=find.values, columns=[find.name])
    df = df[(df.index != 0) | (pd.isnull(df.index) == True)]
    df = df.groupby(df.index).first()
    dictt = df.to_dict('index')
    return dictt


# Аналог впр
def insert_vpr(x, dictt, name):
    try:
        return dictt[x][name]
    except KeyError:
        return 0


# Собириает текущие данные
def get_current_data(data, global_index, current_month):
    index = [x for x in data.columns if x in global_index]
    index.extend([current_month])
    return data[index]


def save_pyex(path, df):
    wb = Workbook()
    wb.new_sheet('sheet1', data=[df.columns.tolist(), ] + df.values.tolist())
    wb.save(path)


# def dict_keys(mapping):
#     cons = pd.DataFrame()
#     for ind, col in enumerate(mapping.columns):
#         try:
#             frame_ = mapping.loc[:, (col[0],['Артикул','Часть'])]
#             frame_.columns = ['Артикул','Часть']
#             cons = cons.append(frame_)
#         except KeyError:
#             pass
#         except ValueError:
#             pass

#     return cons.drop_duplicates()


def dict_keys(col_1_val, mapping):
    cons = pd.DataFrame()
    try:
        frame_ = mapping.loc[:, (col_1_val, ['Артикул', 'Часть'])]
        frame_.columns = ['Артикул', 'Часть']
        cons = cons.append(frame_)
    except KeyError:
        pass
    except ValueError:
        pass

    return cons.drop_duplicates()


def dict_keys_free(col_1_val, mapping, arr_cols):
    cons = pd.DataFrame()
    try:
        frame_ = mapping.loc[:, (col_1_val, arr_cols)]
        frame_.columns = arr_cols
        cons = cons.append(frame_)
    except KeyError:
        pass
    except ValueError:
        pass

    return cons.drop_duplicates()


# Установить тип продукции для 3 передела
def get_type_product(data):
    colName = 'Тип продукции'
    data[colName] = ''
    for art in data['Артикул'].unique():
        min_index = min(list(data[data['Артикул'] == art].index))
        max_index = max(list(data[data['Артикул'] == art].index))
        #         data.loc[min_index,colName] = 'готовая продукция'
        data.loc[max_index, colName] = 'основная продукция'
    return data


# Установка новых % в накладные расходы по упаковке
def input_proc_packaging(df, arr_priznak, date, filter_, df2, arr_priznak1, filter_2):
    cols1 = ('downstream', 'Упак', arr_priznak1[0])
    cols2 = ('downstream', 'Упак', arr_priznak1[1])
    cols3 = ('downstream', 'Упак', arr_priznak1[2])
    cols_all = ('downstream', 'Упак', 'всего')

    all_cost = df2.loc[df2['Месяц']['Месяц']['Месяц'] == date, (cols_all)].sum()

    d1 = df[df[arr_priznak[0]] == "да"][date].sum() / \
         df2[df2['Наименование']['Наименование']['Наименование'] == filter_].loc[:, cols1].sum()

    d2 = df[df[arr_priznak[1]] == "да"][date].sum() / \
         df2[df2['Наименование']['Наименование']['Наименование'] == filter_].loc[:, cols2].sum()

    d3 = df[df[arr_priznak[2]] == "да"][date].sum() / \
         df2[df2['Наименование']['Наименование']['Наименование'] == filter_].loc[:, cols3].sum()

    df2.loc[df2['Наименование']['Наименование']['Наименование'] == filter_2, (cols1)] = d1 / (d1 + d2 + d3)
    df2.loc[df2['Наименование']['Наименование']['Наименование'] == filter_2, (cols2)] = d2 / (d1 + d2 + d3)
    df2.loc[df2['Наименование']['Наименование']['Наименование'] == filter_2, (cols3)] = d3 / (d1 + d2 + d3)

    #     Подставляем значения всего умноженные на эти проценты

    df2.loc[df2['Месяц']['Месяц']['Месяц'] == date, (cols1)] = d1 / (d1 + d2 + d3) * all_cost
    df2.loc[df2['Месяц']['Месяц']['Месяц'] == date, (cols2)] = d2 / (d1 + d2 + d3) * all_cost
    df2.loc[df2['Месяц']['Месяц']['Месяц'] == date, (cols3)] = d3 / (d1 + d2 + d3) * all_cost

    return df2


def save_iter_month_xlsx(directory_out, df, months, name):
    try:
        for date in months:
            df[date].to_excel(directory_out + str(date.month) + name)
    except KeyError:
        pass


# Функция Реструктурирует таблицу с мультиколонками  для того чтобы pandas воспринимал индекс
def restruct_multitindex(df):
    df.rename(columns=dict((x[1],'') for x in df.columns if x[1].find('Unnamed')!=-1) ,inplace=True)
    df = df.dropna(axis='index', how='any', subset=[('Артикул','','')])
    df  = retype_multiindex(df, 'int', 'Артикул', 0)
    df = df.set_index('Артикул')
    return df