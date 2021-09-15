import pandas as pd
import datetime
import calendar
from modules.margin_report.builtin_functions import retype_index,retype_multiindex,get_current_data,dict_keys,rev_to_dict,insert_vpr,input_proc_packaging,restruct_multitindex,replaceUnnameToPass,replaceNToPass,dict_keys_free
import warnings
warnings.filterwarnings('ignore')


def get_ss_amp(month,budj_AMD,global_index,year_report,bolv1,ost_AMD,sebes_amp,df_list_amp,ost_AMP,sebes_amp_new):
    #     эта структура хранит верхнюю таблицу пг_сс_амп формат: дата - 'выход_AMD' и дата - Списано в производство АМП
    upper_table = {}
    sebes_real_pr_AMD = {}

    ost_start_new_amp = df_list_amp[0]

    mapping = df_list_amp[1]
    mapping = retype_multiindex(mapping, 'int', 'Артикул', 1)
    index_for_amp_tables = dict_keys_free('Мэппинг АМП', mapping, ['Артикул', 'Наименование АМД', 'Тип'])

    iter_months = [datetime.datetime(year_report, x, calendar.monthrange(year_report, x)[1], 0, 0) for x in
                   range(1, 13)]
    ost_AMD = ost_AMD.set_index('Артикул')

    amort = df_list_amp[2]

    for ind___, current_month in enumerate(iter_months):
        print(current_month)

        curr_amort = get_current_data(amort, global_index, current_month)

        curr_sebes_amp = get_current_data(sebes_amp, global_index, current_month)[current_month].reset_index()
        curr_budj = \
        get_current_data(budj_AMD.reset_index().set_index(['Артикул', 'канал']), global_index, current_month)[
            current_month].reset_index()
        curr_ost_AMP = get_current_data(ost_AMP, global_index, current_month)
        output_amd = bolv1.copy().reset_index()
        curr_sebes_amp_new = \
        get_current_data(sebes_amp_new.reset_index().set_index(['Артикул']), global_index, current_month)[
            current_month].reset_index()

        #         собираю блок закуп у амд

        def func(x, df, filter_, filter__):
            return df[(df[filter_] == x[filter_]) & (df[filter__] == 'АМП пром')]['Кол-во'].sum()

        output_amd['Объем кг'] = output_amd.apply(lambda x: func(x,
                                                                 curr_budj,
                                                                 'Артикул',
                                                                 'канал'
                                                                 ), axis=1)

        # --------------------------------

        current_rash = ost_AMD['Расход'][current_month].copy().reset_index()

        items = ['C/c мясосырья, Птицеводство тг/кг', 'Специи, добавки тг/кг', 'Упаковочный материал тг/кг',
                 'Затраты на убой и потрошение тг/кг',
                 'Затраты на разделку тг/кг', 'Затраты на охлаждение тг/кг', 'Затраты на заморозку тг/кг',
                 'Затраты на Индив. пакет тг/кг',
                 'Затраты на Подложку тг/кг', 'Затраты на Групп. Пакет тг/кг', 'Затраты на Маринацию тг/кг',
                 'Затраты на Прессование тг/кг']

        for item in items:
            def func(x, df, filter_, filter__):
                return df[df[filter_] == x[filter_]][item].sum()

            output_amd[item] = output_amd.apply(lambda x: func(x,
                                                               current_rash,
                                                               'Артикул',
                                                               item
                                                               ), axis=1)

            output_amd[item] = (output_amd['Объем кг'] * output_amd[item]) / output_amd['Объем кг']

        output_amd['Итого с/c с прямыми расходами тг/кг'] = output_amd['C/c мясосырья, Птицеводство тг/кг'] + \
                                                            output_amd['Специи, добавки тг/кг'] + \
                                                            output_amd['Упаковочный материал тг/кг']

        # -----------------------------------

        output_amd['Итого накладная с/с тг/кг'] = output_amd['Затраты на убой и потрошение тг/кг'] + \
                                                  output_amd['Затраты на разделку тг/кг'] + \
                                                  output_amd['Затраты на охлаждение тг/кг'] + \
                                                  output_amd['Затраты на заморозку тг/кг'] + \
                                                  output_amd['Затраты на Индив. пакет тг/кг'] + \
                                                  output_amd['Затраты на Подложку тг/кг'] + \
                                                  output_amd['Затраты на Групп. Пакет тг/кг'] + \
                                                  output_amd['Затраты на Маринацию тг/кг'] + \
                                                  output_amd['Затраты на Прессование тг/кг']

        # ------------------------------------

        output_amd['Итого с/c тг/кг'] = output_amd['Итого накладная с/с тг/кг'] + \
                                        output_amd['Итого с/c с прямыми расходами тг/кг']

        #         Запись в словарь блока закуп у АМД
        upper_table[current_month] = output_amd

        #         Зполняю себестоимость реализованной продукции АМП

        sebes_prod_amp = pd.DataFrame(index=index_for_amp_tables['Артикул'],
                                      columns=output_amd.set_index('Артикул').columns)
        sebes_prod_amp = sebes_prod_amp.reset_index()
        sebes_prod_amp = sebes_prod_amp.drop_duplicates(subset=['Артикул'])
        sebes_prod_amp = sebes_prod_amp[sebes_prod_amp['Артикул'] != 0]

        def func(x, df, filter_, col):
            return df[df[filter_] == x[filter_]][col].sum()

        sebes_prod_amp['Объем кг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                         curr_sebes_amp,
                                                                         'Артикул',
                                                                         'Объем'
                                                                         ), axis=1)

        sebes_prod_amp['Произв-я с/с по 1С, с амортизацией тыс. тг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                                                           curr_sebes_amp,
                                                                                                           'Артикул',
                                                                                                           'Произв с/с с аморт'
                                                                                                           ),
                                                                                            axis=1) / 1000

        sebes_prod_amp['Сырьевая с/с по 1С тыс. тг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                                           curr_sebes_amp,
                                                                                           'Артикул',
                                                                                           'Сырьевая с/с'
                                                                                           ), axis=1) / 1000

        sebes_prod_amp['С/с мясосырья с наценкой по 1С тыс. тг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                                                       curr_sebes_amp,
                                                                                                       'Артикул',
                                                                                                       'С\с мясо'
                                                                                                       ), axis=1) / 1000

        def func(x, sebes_prod_amp, curr_amort):
            return x['Произв-я с/с по 1С, с амортизацией тыс. тг'] / sebes_prod_amp[
                'Произв-я с/с по 1С, с амортизацией тыс. тг'].sum() * \
                   (sebes_prod_amp['Произв-я с/с по 1С, с амортизацией тыс. тг'].sum() - curr_amort[
                       current_month] / 1000)

        sebes_prod_amp['Произв-я с/с по 1С, без амортизации тыс. тг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                                                            sebes_prod_amp,
                                                                                                            curr_amort
                                                                                                            ), axis=1)

        def func(x, sebes_prod_amp, output_amd):
            return x['С/с мясосырья с наценкой по 1С тыс. тг'] / sebes_prod_amp[
                'С/с мясосырья с наценкой по 1С тыс. тг'].sum() * \
                   output_amd['C/c мясосырья, Птицеводство тг/кг'].sum()

        sebes_prod_amp['C/c мясосырья, Птицеводство тыс. тг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                                                    sebes_prod_amp,
                                                                                                    output_amd
                                                                                                    ), axis=1)

        def func(x, sebes_prod_amp, output_amd, df, filter_, col):
            return x['Объем кг'] / sebes_prod_amp['Объем кг'].sum() * sebes_prod_amp['Специи, добавки тг/кг'].sum() + \
                   df[df[filter_] == x[filter_]][col].sum() / 1000

        sebes_prod_amp['Специи, добавки тыс. тг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                                        sebes_prod_amp,
                                                                                        output_amd,
                                                                                        curr_sebes_amp,
                                                                                        'Артикул',
                                                                                        'С\с специи'
                                                                                        ), axis=1)

        def func(x, sebes_prod_amp, output_amd, df, filter_, col):
            return x['Объем кг'] / sebes_prod_amp['Объем кг'].sum() * sebes_prod_amp[
                'Упаковочный материал тг/кг'].sum() + \
                   df[df[filter_] == x[filter_]][col].sum() / 1000

        sebes_prod_amp['Упаковочный материал тыс. тг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                                             sebes_prod_amp,
                                                                                             output_amd,
                                                                                             curr_sebes_amp,
                                                                                             'Артикул',
                                                                                             'С\с упаковка'
                                                                                             ), axis=1)

        dict_type_prod_amp = rev_to_dict(index_for_amp_tables['Артикул'], index_for_amp_tables['Тип'])
        sebes_prod_amp['Тип продукции'] = sebes_prod_amp.apply(
            lambda x: insert_vpr(x['Артикул'], dict_type_prod_amp, 'Тип'), axis=1).astype('str')

        def func(x, output_amd, filter_, col, col___):
            outp_ = (output_amd[col] * output_amd[col___ + ' тг/кг']).sum() / 1000
            if x['Тип продукции'] == 'ГП':
                return x[col] / sebes_prod_amp[sebes_prod_amp[filter_] == 'ГП'][col].sum() * outp_
            else:
                return 0

        cols = ['Затраты на убой и потрошение', 'Затраты на разделку', 'Затраты на охлаждение', 'Затраты на заморозку',
                'Затраты на Индив. пакет', 'Затраты на Подложку', 'Затраты на Групп. Пакет', 'Затраты на Маринацию',
                'Затраты на Прессование']

        for col___ in cols:
            sebes_prod_amp[col___ + ' тыс. тг'] = sebes_prod_amp.apply(lambda x: func(x,
                                                                                      output_amd,
                                                                                      'Тип продукции',
                                                                                      'Объем кг',
                                                                                      col___
                                                                                      ), axis=1)

        sebes_prod_amp['Прозв-е затраты АМП тыс. тг'] = sebes_prod_amp['Произв-я с/с по 1С, без амортизации тыс. тг'] - \
                                                        sebes_prod_amp['Сырьевая с/с по 1С тыс. тг']

        items = ['Специи, добавки', 'Упаковочный материал', 'Затраты на убой и потрошение',
                 'Затраты на разделку', 'Затраты на охлаждение', 'Затраты на заморозку', 'Затраты на Индив. пакет',
                 'Затраты на Подложку', 'Затраты на Групп. Пакет', 'Затраты на Маринацию', 'Затраты на Прессование',
                 'Прозв-е затраты АМП']
        #         'C/c мясосырья, Птицеводство'

        for item in items:
            sebes_prod_amp[item + ' тг/кг'] = sebes_prod_amp[item + ' тыс. тг'] / sebes_prod_amp['Объем кг'] * 1000

        def func(x, df, filter_):
            sum_ = df[df[filter_] == x[filter_]]['Сырьевая себестоимость(KZT)']['Себестоимость(KZT) Мясо'].sum()

            if x['Объем кг'] != 0:
                return sum_ / x['Объем кг'] - x['Затраты на убой и потрошение тг/кг'] - x['Затраты на разделку тг/кг'] - \
                       x['Затраты на охлаждение тг/кг'] - x['Затраты на заморозку тг/кг']
            else:
                return 0

        sebes_prod_amp['C/c мясосырья, Птицеводство тг/кг'] = \
            sebes_prod_amp.apply(lambda x: func(x,
                                                curr_sebes_amp_new,
                                                'Артикул'
                                                ), axis=1)

        #         if ind___+1==1:
        #             return sebes_prod_amp

        #         Записываю  Себестоимость реализованной продукции АМП в словарь
        sebes_real_pr_AMD[current_month] = sebes_prod_amp

        #         закончил формрование Себестоимость реализованной продукции АМП

        #        начинаю формирование Себестоимость реализованной продукции АМП с учетом остатков

        if ind___ > 0:
            prev_month = iter_months[ind___ - 1]

        if current_month.month == 1:
            cols_join = []

            cols_join = [x for x in sebes_prod_amp.columns if x.find('тг/кг') != -1]
            cols_join.extend(['Объем кг'])

            start_date = datetime.datetime(year_report - 1, 12, 31, 0, 0)

            cons_ost_start = pd.DataFrame(index=ost_start_new_amp.index, data=ost_start_new_amp)
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


        else:

            path_ost_nach = ('Остаток', prev_month)
            path_pr = ('Приход', current_month)
            path_r = ('Расход', current_month)
            path_ost_kon = ('Остаток', current_month)

        #         Обрботка приходной части

        #         prih = bolv.copy()

        #         prih = prih.reset_index()

        prih = sebes_prod_amp.set_index('Артикул')[cols_join]

        ml = pd.MultiIndex.from_tuples([('Приход', current_month, x) for x in prih.columns])

        prih.columns = ml

        if current_month.month == 1:
            it = pd.concat([cons_ost_start, prih], axis=1)


        else:
            it = it.set_index('Артикул')
            it = pd.concat([it, prih], axis=1)

        #         ------------------------------------------------------------------------------------------------------------

        it = it.reset_index()

        cols_sum = ['C/c мясосырья, Птицеводство тг/кг', 'Специи, добавки тг/кг', 'Упаковочный материал тг/кг',
                    'Затраты на убой и потрошение тг/кг',
                    'Затраты на разделку тг/кг', 'Затраты на охлаждение тг/кг', 'Затраты на заморозку тг/кг',
                    'Затраты на Индив. пакет тг/кг',
                    'Затраты на Подложку тг/кг', 'Затраты на Групп. Пакет тг/кг', 'Затраты на Маринацию тг/кг',
                    'Затраты на Прессование тг/кг',
                    'Прозв-е затраты АМП тг/кг']

        it.loc[:, (path_pr[0], path_pr[1], 'Итого с/c тг/кг')] = it.loc[:, (path_pr[0], path_pr[1], cols_sum)].sum(
            axis=1)

        #         Заполняем расходную часть

        rash = bolv.copy()
        #         rash = rash.set_index('Артикул')
        ml = pd.MultiIndex.from_tuples([('Расход', current_month, x) for x in rash.columns])
        rash.columns = ml

        #         rash = rash.reset_index()

        it = it.set_index('Артикул')
        it = pd.concat([it, rash], axis=1)

        it = it.reset_index()

        curr_budj = curr_budj.reset_index()

        # -----------------------

        def func(x, df, filter_, current_month):
            return df[(df[filter_] == x[filter_][0]) & (df['канал'] == 'ОПТ АМП')]['Кол-во'].sum()

        it.loc[:, (path_r[0], path_r[1], 'Объем кг')] = it.apply(lambda x: func(x,
                                                                                curr_budj,
                                                                                'Артикул',
                                                                                current_month
                                                                                ), axis=1)

        items = ['C/c мясосырья, Птицеводство тг/кг', 'Специи, добавки тг/кг', 'Упаковочный материал тг/кг',
                 'Затраты на убой и потрошение тг/кг',
                 'Затраты на разделку тг/кг', 'Затраты на охлаждение тг/кг', 'Затраты на заморозку тг/кг',
                 'Затраты на Индив. пакет тг/кг',
                 'Затраты на Подложку тг/кг', 'Затраты на Групп. Пакет тг/кг', 'Затраты на Маринацию тг/кг',
                 'Затраты на Прессование тг/кг', 'Прозв-е затраты АМП тг/кг']

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

        # -----------------------------------

        it.loc[:, (path_r[0], path_r[1], 'Итого с/c тг/кг')] = it.loc[:, (path_r[0], path_r[1], cols_sum)].sum(axis=1)

        #         Заполняю блок остатки на конец периода

        ost_con = bolv.copy()
        #         rash = rash.set_index('Артикул')
        ml = pd.MultiIndex.from_tuples([('Остаток', current_month, x) for x in ost_con.columns])
        ost_con.columns = ml
        it = it.set_index('Артикул')
        it = pd.concat([it, ost_con], axis=1)

        it = it.reset_index()

        curr_ost_AMP = curr_ost_AMP.reset_index()

        #         ------------------------------------

        def func(x, df, filter_, current_month):
            return df[df[filter_] == x[filter_][0]][current_month].sum()

        it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Объем кг')] = it.apply(lambda x: func(x,
                                                                                            curr_ost_AMP,
                                                                                            'Артикул',
                                                                                            current_month
                                                                                            ), axis=1)

        for item in items:

            it.loc[:, (path_ost_kon[0], path_ost_kon[1], item)] = it.loc[:,
                                                                  (path_ost_nach[0], path_ost_nach[1], 'Объем кг')] - \
                                                                  it.loc[:, (path_pr[0], path_pr[1], 'Объем кг')]

            def func(x):
                if (x[path_pr[0]][path_pr[1]]['Объем кг'] - x[path_r[0]][path_r[1]]['Объем кг']) == 0:
                    return x[path_r[0]][path_r[1]][item]
                else:

                    return (x[path_ost_nach[0]][path_ost_nach[1]]['Объем кг'] * x[path_ost_nach[0]][path_ost_nach[1]][
                        item] + \
                            x[path_pr[0]][path_pr[1]]['Объем кг'] * x[path_pr[0]][path_pr[1]][item] + \
                            x[path_r[0]][path_r[1]]['Объем кг'] * x[path_r[0]][path_r[1]][item]) / \
                           (x[path_ost_nach[0]][path_ost_nach[1]]['Объем кг'] + x[path_pr[0]][path_pr[1]]['Объем кг'] + \
                            x[path_r[0]][path_r[1]]['Объем кг'])

            it.loc[:, (path_ost_kon[0], path_ost_kon[1], item)] = it.apply(lambda x: func(x), axis=1)

        #             it.loc[:,(path_ost_kon[0],path_ost_kon[1],item)] = ( it.loc[:,(path_ost_nach[0],path_ost_nach[1],'Объем кг')] * \
        #                                                     it.loc[:,(path_ost_nach[0],path_ost_nach[1],item)] + \
        #                                                     it.loc[:,(path_pr[0],path_pr[1],'Объем кг')] * \
        #                                                     it.loc[:,(path_pr[0],path_pr[1],item)] - \
        #                                                     it.loc[:,(path_r[0],path_r[1],'Объем кг')] * \
        #                                                     it.loc[:,(path_r[0],path_r[1],item)] ) / \
        #                                                     (  it.loc[:,(path_ost_nach[0],path_ost_nach[1],'Объем кг')] + it.loc[:,(path_pr[0],path_pr[1],'Объем кг')] - it.loc[:,(path_r[0],path_r[1],'Объем кг')])

        # ----------------------------------

        # ------------------------------------

        it.loc[:, (path_ost_kon[0], path_ost_kon[1], 'Итого с/c тг/кг')] = it.loc[:, (path_ost_kon[0], path_ost_kon[1],
                                                                                      cols_sum)].sum(axis=1)

        if ind___ + 1 == month:
            template_ = \
            get_current_data(budj_AMD.reset_index().set_index(['Артикул', 'канал', 'Наименование', 'продукт']),
                             global_index, current_month)[current_month].reset_index()[
                ['Артикул', 'канал', 'Наименование', 'продукт']]

            return it, template_, mapping, upper_table, sebes_real_pr_AMD

#         return it