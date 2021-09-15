import pandas as pd
import datetime
import calendar
from modules.margin_report.builtin_functions import retype_index,retype_multiindex,get_current_data,dict_keys,rev_to_dict,insert_vpr,input_proc_packaging,restruct_multitindex,replaceUnnameToPass,replaceNToPass
import warnings
warnings.filterwarnings('ignore')

def get_amd_sebes(prod_UKPF, ost_UKPF, prod_MPF, ost_MPF, year_report, df_list_amd, month,
                  global_index):


    ost_start_new_dip = df_list_amd[0]

    budj = df_list_amd[1]
    budj.rename(columns=dict((x[1], '') for x in budj.columns if x[1].find('Unnamed') != -1), inplace=True)
    budj = budj.dropna(axis='index', how='any', subset=[('Артикул', '')])
    budj = retype_multiindex(budj, 'int', 'Артикул', 0)
    budj = budj.set_index('Артикул')

    ost_AMD = df_list_amd[2]
    ost_AMD.rename(columns=dict((x[1], '') for x in ost_AMD.columns if x[1].find('Unnamed') != -1), inplace=True)
    ost_AMD = ost_AMD.dropna(axis='index', how='any', subset=[('Артикул', '')])
    ost_AMD = retype_multiindex(ost_AMD, 'int', 'Артикул', 0)
    ost_AMD = ost_AMD.set_index('Артикул')

    sebes_amp_new = df_list_amd[3]
    sebes_amp_new.rename(columns=replaceUnnameToPass(sebes_amp_new), inplace=True)
    sebes_amp_new.rename(columns=replaceNToPass(sebes_amp_new), inplace=True)
    sebes_amp_new = sebes_amp_new.dropna(axis='index', how='any', subset=[('Артикул', '', '')])
    sebes_amp_new = retype_multiindex(sebes_amp_new, 'int', 'Артикул', 0)
    sebes_amp_new = sebes_amp_new.set_index('Артикул')

    ost_AMP = df_list_amd[4]
    #     ost_AMP.rename(columns=dict((x[1],'') for x in ost_AMD.columns if x[1].find('Unnamed')!=-1) ,inplace=True)
    ost_AMP = ost_AMP.dropna(axis='index', how='any', subset=['Артикул'])
    ost_AMP = retype_index(ost_AMP, 'int', 'Артикул')
    ost_AMP = ost_AMP.set_index('Артикул')

    sebes_amp = df_list_amd[5]
    sebes_amp.rename(columns=dict((x[1], '') for x in sebes_amp.columns if x[1].find('Unnamed') != -1), inplace=True)
    sebes_amp = sebes_amp.dropna(axis='index', how='any', subset=[('Артикул', '')])
    sebes_amp = retype_multiindex(sebes_amp, 'int', 'Артикул', 0)
    sebes_amp = sebes_amp.set_index('Артикул')
    iter_months = [datetime.datetime(year_report, x, calendar.monthrange(year_report, x)[1], 0, 0) for x in
                   range(1, 13)]

    ost_start = ost_UKPF.copy()

    #     ost_UKPF = ost_UKPF.set_index('Артикул')
    #     ost_MPF = ost_MPF.set_index('Артикул')

    for ind___, current_month in enumerate(iter_months):
        print(current_month)
        #         Текущие данные по бюджету продаж

        curr_budj = get_current_data(budj, global_index, current_month)
        curr_ost_AMD = get_current_data(ost_AMD, global_index, current_month)

        #         нужна для формирования таблицы с остатками
        if ind___ > 0:
            prev_month = iter_months[ind___ - 1]

        #         bolv = pd.DataFrame()
        cols_join = []

        if current_month.month == 1:

            start_date = datetime.datetime(year_report - 1, 12, 31, 0, 0)

            cols_join = [x for x in ost_UKPF['Остаток'][start_date].rename(columns={current_month: 'Объем кг'}).columns
                         if x.find('тг/кг') != -1]

            cons_ost_start = pd.DataFrame(index=ost_start_new_dip.index, data=ost_start_new_dip)
            bolv = cons_ost_start.copy()
            for col in bolv.columns: bolv[col] = 0
            #             f_ost_nach = pd.DataFrame(data = ost_UKPF['Остаток'][start_date],index = ost_UKPF.loc[:,'Артикул'])

            #             f_ost_nach.index.name = 'Артикул'

            ml = pd.MultiIndex.from_tuples([('Остаток', start_date, x) for x in cons_ost_start.columns])

            cons_ost_start.columns = ml

            path_ost_nach = ('Остаток', start_date)
            path_pr = ('Приход', current_month)
            path_r = ('Расход', current_month)
            path_ost_kon = ('Остаток', current_month)

            ost_UKPF = ost_UKPF.set_index('Артикул')
            ost_MPF = ost_MPF.set_index('Артикул')

        else:

            path_ost_nach = ('Остаток', prev_month)
            path_pr = ('Приход', current_month)
            path_r = ('Расход', current_month)
            path_ost_kon = ('Остаток', current_month)

        #         Обрботка приходной части

        prih = bolv.copy()
        #         prih = prih.reset_index()

        ost_UKPF_ = ost_UKPF['Расход'][current_month].copy()
        ost_MPF_ = ost_MPF['Расход'][current_month].copy()
        ost_UKPF_ = ost_UKPF_.reset_index()
        ost_MPF_ = ost_MPF_.reset_index()

        ml = pd.MultiIndex.from_tuples([('Приход', current_month, x) for x in prih.columns])

        prih.columns = ml

        if current_month.month == 1:
            it = pd.concat([cons_ost_start, prih], axis=1)

        else:

            it = it.set_index('Артикул')
            it = pd.concat([it, prih], axis=1)

        #         ------------------------------------------------------------------------------------------------------------

        it = it.reset_index()
        it.fillna(0, inplace=True)

        def func(x, df, df1, filter_):
            ukpf = df[df[filter_] == x[filter_][0]]['Объем кг'].sum()
            mpf = df1[df1[filter_] == x[filter_][0]]['Объем кг'].sum()
            return ukpf + mpf

        it.loc[:, (path_pr[0], path_pr[1], 'Объем кг')] = it.apply(lambda x: func(x,
                                                                                  ost_UKPF_,
                                                                                  ost_MPF_,
                                                                                  'Артикул'
                                                                                  ), axis=1)

        # --------------------------------

        def func(x, df, df1, filter_, col3):
            return (df[df[filter_] == x[filter_][0]]['Объем кг'].sum() * \
                    df[df[filter_] == x[filter_][0]][col3].sum() + \
                    df1[df1[filter_] == x[filter_][0]]['Объем кг'].sum() * \
                    df1[df1[filter_] == x[filter_][0]][col3].sum()) / x['Приход'][current_month]['Объем кг']

        items = ['C/c мясосырья, Птицеводство тг/кг', 'C/c мясосырья, Агро тг/кг', 'Специи, добавки тг/кг',
                 'Упаковочный материал тг/кг', 'Затраты на убой и потрошение тг/кг',
                 'Затраты на разделку тг/кг', 'Затраты на охлаждение тг/кг', 'Затраты на заморозку тг/кг',
                 'Затраты на Индив. пакет тг/кг',
                 'Затраты на Подложку тг/кг', 'Затраты на Групп. Пакет тг/кг', 'Затраты на Маринацию тг/кг',
                 'Затраты на Прессование тг/кг']

        for item in items:
            it.loc[:, (path_pr[0], path_pr[1], item)] = it.apply(lambda x: func(x,
                                                                                ost_UKPF_,
                                                                                ost_MPF_,
                                                                                'Артикул',
                                                                                item
                                                                                ), axis=1)

        #          if ind___+1==1:
        #             return it
        # -----------------------------------

        it.loc[:, (path_pr[0], path_pr[1], 'Итого с/c с прямыми расходами тг/кг')] = (
                it.loc[:, (path_pr[0], path_pr[1], 'C/c мясосырья, Птицеводство тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Специи, добавки тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Упаковочный материал тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'C/c мясосырья, Агро тг/кг')]).round(5)

        # -----------------------------------

        it.loc[:, (path_pr[0], path_pr[1], 'Итого накладная с/с тг/кг')] = (
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на убой и потрошение тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на разделку тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на охлаждение тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на заморозку тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на Индив. пакет тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на Подложку тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на Групп. Пакет тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на Маринацию тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Затраты на Прессование тг/кг')]).round(5)

        # -----------------------------------

        it.loc[:, (path_pr[0], path_pr[1], 'Итого с/c тг/кг')] = (
                it.loc[:, (path_pr[0], path_pr[1], 'Итого накладная с/с тг/кг')] + \
                it.loc[:, (path_pr[0], path_pr[1], 'Итого с/c с прямыми расходами тг/кг')]).round(5)

        #         Заполняем расходную часть

        rash = bolv.copy()
        #         rash = rash.set_index('Артикул')
        ml = pd.MultiIndex.from_tuples([('Расход', current_month, x) for x in rash.columns])
        rash.columns = ml

        #         rash = rash.reset_index()

        it = it.set_index('Артикул')
        it = pd.concat([it, rash], axis=1)

        it = it.reset_index()
        it.fillna(0, inplace=True)

        curr_budj = curr_budj.reset_index()

        # -----------------------

        def func(x, df, filter_, current_month):
            return df[df[filter_] == x[filter_][0]][current_month]['Кол-во'].sum()

        it.loc[:, (path_r[0], path_r[1], 'Объем кг')] = it.apply(lambda x: func(x,
                                                                                curr_budj,
                                                                                'Артикул',
                                                                                current_month
                                                                                ), axis=1)

        for item in items:
            it.loc[:, (path_r[0], path_r[1], item)] = (it.loc[:, (path_ost_nach[0], path_ost_nach[1], 'Объем кг')] * \
                                                       it.loc[:, (path_ost_nach[0], path_ost_nach[1], item)] + \
                                                       it.loc[:, (path_pr[0], path_pr[1], 'Объем кг')] * \
                                                       it.loc[:, (path_pr[0], path_pr[1], item)]).round(5) / \
                                                      (it.loc[:,
                                                       (path_ost_nach[0], path_ost_nach[1], 'Объем кг')] + it.loc[:, (
                                                                                                                         path_pr[
                                                                                                                             0],
                                                                                                                         path_pr[
                                                                                                                             1],
                                                                                                                         'Объем кг')]).round(
                                                          5)
        #         for item in items:
        #             it.loc[:,(path_r[0],path_r[1],item)] =  it.loc[:,(path_ost_nach[0],path_ost_nach[1],'Объем кг')] * \
        #                                                     it.loc[:,(path_ost_nach[0],path_ost_nach[1],item)]

        #         if ind___+1==1:
        #             return it
        # -----------------------------------

        it.loc[:, (path_r[0], path_r[1], 'Итого с/c с прямыми расходами тг/кг')] = (
                it.loc[:, (path_r[0], path_r[1], 'C/c мясосырья, Птицеводство тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Специи, добавки тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Упаковочный материал тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'C/c мясосырья, Агро тг/кг')]).round(5)
        # -----------------------------------

        it.loc[:, (path_r[0], path_r[1], 'Итого накладная с/с тг/кг')] = (
                it.loc[:, (path_r[0], path_r[1], 'Затраты на убой и потрошение тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Затраты на разделку тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Затраты на охлаждение тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Затраты на заморозку тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Затраты на Индив. пакет тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Затраты на Подложку тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Затраты на Групп. Пакет тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Затраты на Маринацию тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Затраты на Прессование тг/кг')]).round(5)

        # -----------------------------------

        it.loc[:, (path_r[0], path_r[1], 'Итого с/c тг/кг')] = (
                it.loc[:, (path_r[0], path_r[1], 'Итого накладная с/с тг/кг')] + \
                it.loc[:, (path_r[0], path_r[1], 'Итого с/c с прямыми расходами тг/кг')]).round(5)

        #         Заполняю блок остатки на конец периода

        ost_con = bolv.copy()
        #         rash = rash.set_index('Артикул')
        ml = pd.MultiIndex.from_tuples([('Остаток', current_month, x) for x in ost_con.columns])
        ost_con.columns = ml
        it = it.set_index('Артикул')
        it = pd.concat([it, ost_con], axis=1)

        it = it.reset_index()
        it.fillna(0, inplace=True)

        curr_ost_AMD = curr_ost_AMD.reset_index()

        #         ------------------------------------

        def func(x, df, filter_, current_month):
            return df[df[filter_] == x[filter_][0]][current_month]['остаток'].sum()

        it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Объем кг')] = it.apply(lambda x: func(x,
                                                                                            curr_ost_AMD,
                                                                                            'Артикул',
                                                                                            current_month
                                                                                            ), axis=1)

        for item in items:
            it.loc[:, (path_ost_kon[0], path_ost_kon[1], item)] = (it.loc[:,
                                                                   (path_ost_nach[0], path_ost_nach[1], 'Объем кг')] * \
                                                                   it.loc[:,
                                                                   (path_ost_nach[0], path_ost_nach[1], item)] + \
                                                                   it.loc[:, (path_pr[0], path_pr[1], 'Объем кг')] * \
                                                                   it.loc[:, (path_pr[0], path_pr[1], item)] - \
                                                                   it.loc[:, (path_r[0], path_r[1], 'Объем кг')] * \
                                                                   it.loc[:, (path_r[0], path_r[1], item)]).round(5) / \
                                                                  (it.loc[:, (path_ost_nach[0], path_ost_nach[1],
                                                                              'Объем кг')] + it.loc[:, (path_pr[0],
                                                                                                        path_pr[1],
                                                                                                        'Объем кг')] - it.loc[
                                                                                                                       :,
                                                                                                                       (
                                                                                                                           path_r[
                                                                                                                               0],
                                                                                                                           path_r[
                                                                                                                               1],
                                                                                                                           'Объем кг')]).round(
                                                                      5)

        # -----------------------------------

        it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Итого с/c с прямыми расходами тг/кг')] = (
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'C/c мясосырья, Птицеводство тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Специи, добавки тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Упаковочный материал тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'C/c мясосырья, Агро тг/кг')]).round(5)

        # -----------------------------------

        it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Итого накладная с/с тг/кг')] = (
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на убой и потрошение тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на разделку тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на охлаждение тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на заморозку тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на Индив. пакет тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на Подложку тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на Групп. Пакет тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на Маринацию тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Затраты на Прессование тг/кг')]).round(5)

        # ------------------------------------

        it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Итого с/c тг/кг')] = (
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Итого накладная с/с тг/кг')] + \
                it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Итого с/c с прямыми расходами тг/кг')]).round(5)

        if ind___ + 1 == month:
            return it, budj, bolv, sebes_amp, ost_AMP, sebes_amp_new
#         return it
