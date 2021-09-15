import pandas as pd
import datetime
import calendar
from modules.margin_report.builtin_functions import retype_index,retype_multiindex,get_current_data,dict_keys,rev_to_dict,insert_vpr,input_proc_packaging,restruct_multitindex
import warnings
import numpy as np
warnings.filterwarnings('ignore')

def get_ss_sku(template_for_ss_sku, budj_AMD, ost_AMP_d, ost_AMD, mapping, month, year_report,df_list_ss_sku_itog, global_index):
    cons_table_dict = {}
    #     подготовка затрат АМД

    cost_amd = df_list_ss_sku_itog[0]
    cost_amp = df_list_ss_sku_itog[1]
    cost_ukpf = df_list_ss_sku_itog[2]
    cost_mpf = df_list_ss_sku_itog[3]
    adm_cost_AMP = df_list_ss_sku_itog[4]
    adm_cost_AMD = df_list_ss_sku_itog[5]

    def get_mapping_into_cost(aa):
        for ind__ in aa.index:
            if (aa.at[ind__, 'Группа'] != aa.at[ind__, 'Группа']) == False:
                ind_inp = ind__
            else:
                aa.at[ind__, 'map1'] = aa.at[ind_inp, 'Группа']
        return aa

    cost_amd = get_mapping_into_cost(cost_amd)

    dict_cost_AMD = rev_to_dict(mapping['Расходы по реализации АМД']['Расходы по реализации АМД'],
                                mapping['Расходы по реализации АМД']['Канал'])
    dict_cost_AMD1 = rev_to_dict(mapping['Статьи затрат']['Статьи затрат'],
                                 mapping['Статьи затрат']['Группа затрат, для службы продаж'])
    dict_cost_AMD2 = rev_to_dict(mapping['Статьи затрат']['Статьи затрат'],
                                 mapping['Статьи затрат']['Группа затрат, для службы логистики'])
    dict_cost_AMD3 = rev_to_dict(mapping['Статьи затрат']['Статьи затрат'],
                                 mapping['Статьи затрат']['Группа затрат, для оставшихся'])

    cost_amd['map2'] = cost_amd.apply(lambda x: insert_vpr(x['map1'], dict_cost_AMD, 'Канал'), axis=1).astype('str')

    def func(x, col, col1, col2):
        try:

            str_ = str(x['map1']).lower()
            if str_.find('продаж') != -1 or str_.find('проф') != -1 or str_.find('кейтеринг') != -1 \
                    or str_.find('отп') != -1 or str_.find('экспорт') != -1:

                return dict_cost_AMD1[x['Служба продаж']][col]

            elif str_.find('логистики') != -1:

                return dict_cost_AMD2[x['Служба продаж']][col1]

            else:

                return dict_cost_AMD3[x['Служба продаж']][col2]

        except KeyError:
            pass

    cost_amd['map3'] = cost_amd.apply(lambda x: func(x,
                                                     'Группа затрат, для службы продаж',
                                                     'Группа затрат, для службы логистики',
                                                     'Группа затрат, для оставшихся'
                                                     ), axis=1)

    iter_months = [datetime.datetime(year_report, x, calendar.monthrange(year_report, x)[1], 0, 0) for x in
                   range(1, 13)]

    for ind___, current_month in enumerate(iter_months):

        print(current_month)

        curr_budj = \
        get_current_data(budj_AMD.reset_index().set_index(['Артикул', 'канал']), global_index, current_month)[
            current_month].reset_index()
        curr_cost_amp = get_current_data(cost_amp, global_index, current_month)[current_month].sum()
        curr_cost_amd = get_current_data(cost_amd.set_index(['map2', 'map3']), global_index, current_month)[
            current_month].reset_index()
        curr_cost_ukpf = get_current_data(cost_ukpf.set_index('Наименование показателя'), global_index, current_month)[
            current_month].reset_index()
        curr_cost_mpf = get_current_data(cost_mpf.set_index('Наименование показателя'), global_index, current_month)[
            current_month].reset_index()
        curr_adm_cost_AMP = get_current_data(adm_cost_AMP.set_index('ОАР АМП'), global_index, current_month)[
            current_month].reset_index()
        curr_adm_cost_AMD = get_current_data(adm_cost_AMD.set_index('ОАР АМД'), global_index, current_month)[
            current_month].reset_index()

        #         блок продажи
        stock = template_for_ss_sku[['Артикул', 'канал']].copy()

        def func(x, df, col):
            return df[(df['канал'] == x['канал']) & (df['Артикул'] == x['Артикул'])][col].sum()

        stock['Объем кг'] = stock.apply(lambda x: func(x, curr_budj, 'Кол-во'), axis=1)

        stock['Цена тг/кг'] = stock.apply(lambda x: func(x, curr_budj, 'Сумма'), axis=1) / stock['Объем кг']
        stock = stock.set_index(['Артикул', 'канал'])

        ml = pd.MultiIndex.from_tuples([('Продажи', x) for x in stock.columns])
        stock.columns = ml

        #         блок себестоимость

        sebes = template_for_ss_sku[['Артикул', 'канал']].copy()
        current_rash_AMD = ost_AMD.set_index('Артикул')['Расход'][current_month].copy().reset_index()
        current_rash_AMP = ost_AMP_d.set_index('Артикул')['Расход'][current_month].copy().reset_index()

        all_ = current_rash_AMD.append(current_rash_AMP)

        cols_sum = []
        for col in all_.set_index('Артикул').columns:

            if col != 'Объем кг' and col.find('Итого') == -1:
                def func(x, df, col__):
                    return df[df['Артикул'] == x['Артикул']][col__].sum()

                sebes[col] = sebes.apply(lambda x: func(x, all_, col), axis=1)
                cols_sum.append(col)

        sebes['Итого тг/кг'] = sebes[cols_sum].sum(axis=1)
        sebes = sebes.set_index(['Артикул', 'канал'])

        ml = pd.MultiIndex.from_tuples([('Себестоимость', x) for x in sebes.columns])
        sebes.columns = ml

        stock_sebes = pd.concat([stock, sebes], axis=1)
        stock_sebes = stock_sebes.reset_index()
        #
        # #         Блок расходы по реализации
        #
        # # ---------------------------------------------------
        #
        # def func(x, df):
        #     if x['канал'][0] == 'ОПТ АМП':
        #         return curr_cost_amp * (
        #                     x['Продажи']['Объем кг'] / df[df['канал'] == 'ОПТ АМП']['Продажи']['Объем кг'].sum())
        #     else:
        #         return 0

        # stock_sebes.loc[:, ('Расходы по реализации', 'РР АМП (ГП)')] = stock_sebes.apply(lambda x: func(x, stock_sebes),
        #                                                                                  axis=1) / \
        #                                                                stock_sebes['Продажи']['Объем кг'] * 1000
        #
        # # ---------------------------------------------------
        #
        # def func(x, df, df1, channel, pr_cost):
        #     #             if x['канал'][0]=='Кейтеринг':
        #     prod = x['Продажи']['Объем кг']
        #     a = (df1[(df1['map2'] == channel) & (df1['map3'] == pr_cost)][current_month].sum() / 1000) * prod / \
        #         df[df['канал'] == channel]['Продажи']['Объем кг'].sum() / prod * 1000
        #
        #     b = prod / (df['Продажи']['Объем кг'].sum() - df[df['канал'] == 'АМП пром']['Продажи']['Объем кг'].sum()) * \
        #         (df1[(df1['map2'] == 'на все каналы') & (df1['map3'] == pr_cost)][
        #              current_month].sum() / 1000) / prod * 1000
        #
        #     return a + b
        #
        # stock_sebes.loc[:, ('Расходы по реализации', 'Логистика тг/кг')] = stock_sebes.apply(lambda x: func(x,
        #                                                                                                     stock_sebes,
        #                                                                                                     curr_cost_amd,
        #                                                                                                     x['канал'][
        #                  stock_sebes                                                                                       0],
        #                                                                                                     'Логистика'),
        #                                                                                      axis=1)
        #
        # stock_sebes.loc[:, ('Расходы по реализации', 'Дистрибуция тг/кг')] = stock_sebes.apply(lambda x: func(x,
        #                                                                                                       stock_sebes,
        #                                                                                                       curr_cost_amd,
        #                                                                                                       x[
        #                                                                                                           'канал'][
        #                                                                                                           0],
        #                                                                                                       'Дистрибуция'),
        #                                                                                        axis=1)
        # stock_sebes.loc[:, ('Расходы по реализации', 'Маркетинг тг/кг')] = stock_sebes.apply(lambda x: func(x,
        #                                                                                                     stock_sebes,
        #                                                                                                     curr_cost_amd,
        #                                                                                                     x['канал'][
        #                                                                                                         0],
        #                                                                                                     'Маркетинг'),
        #                                                                                      axis=1)
        #
        # stock_sebes.loc[:, ('Расходы по реализации', 'Прочее (ЗПП+АМД) тг/кг')] = stock_sebes.apply(lambda x: func(x,
        #                                                                                                            stock_sebes,
        #                                                                                                            curr_cost_amd,
        #                                                                                                            x[
        #                                                                                                                'канал'][
        #                                                                                                                0],
        #                                                                                                            'Прочее'),
        #                                                                                             axis=1)
        #
        # def func(x, df, df1, pr_cost, stock_sebes):
        #
        #     if x['канал'][0] != 'АМП пром':
        #         prod = x['Продажи']['Объем кг']
        #         a = prod / (stock_sebes['Продажи']['Объем кг'].sum() - df[df['канал'] == 'АМП пром']['Продажи'][
        #             'Объем кг'].sum()) * \
        #             curr_cost_mpf[curr_cost_mpf['Наименование показателя'] == pr_cost][
        #                 current_month].sum() / prod * 1000
        #
        #         b = prod / (stock_sebes['Продажи']['Объем кг'].sum() - df[df['канал'] == 'АМП пром']['Продажи'][
        #             'Объем кг'].sum()) * \
        #             curr_cost_ukpf[curr_cost_ukpf['Наименование показателя'] == pr_cost][
        #                 current_month].sum() / prod * 1000
        #
        #         return a + b
        #
        # stock_sebes.loc[:, ('Расходы по реализации', 'Прочее (ЗПП+АМД) тг/кг')] = stock_sebes.loc[:, (
        #                                                                                              'Расходы по реализации',
        #                                                                                              'Прочее (ЗПП+АМД) тг/кг')] + \
        #                                                                           stock_sebes.apply(lambda x: func(x,
        #                                                                                                            stock_sebes,
        #                                                                                                            curr_cost_amd,
        #                                                                                                            'Прочее',
        #                                                                                                            stock_sebes),
        #                                                                                             axis=1)

        # stock_sebes.loc[:, ('Расходы по реализации', 'Итого тг/кг')] = stock_sebes.loc[:,
        #                                                                ('Расходы по реализации', 'Логистика тг/кг')] + \
        #                                                                stock_sebes.loc[:,
        #                                                                ('Расходы по реализации', 'Дистрибуция тг/кг')] + \
        #                                                                stock_sebes.loc[:,
        #                                                                ('Расходы по реализации', 'Маркетинг тг/кг')] + \
        #                                                                stock_sebes.loc[:, ('Расходы по реализации',
        #                                                                                    'Прочее (ЗПП+АМД) тг/кг')]
        #
        # def func(x, df, df2):
        #
        #     if x['канал'][0] == 'АМП пром':
        #         return 0
        #     else:
        #
        #         prod = x['Продажи']['Объем кг']
        #         a = prod / (stock_sebes['Продажи']['Объем кг'].sum() - df[df['канал'] == 'АМП пром']['Продажи'][
        #             'Объем кг'].sum()) * \
        #             df2[current_month].sum() / prod * 1000
        #
        #         return a
        #
        # stock_sebes.loc[:, ('Адм. расходы', 'Адм. расходы АМД тг/кг')] = stock_sebes.apply(
        #     lambda x: func(x, stock_sebes, curr_adm_cost_AMD), axis=1)
        #
        # def func(x, df, df2):
        #
        #     if x['канал'][0] == 'ОПТ АМП':
        #         prod = x['Продажи']['Объем кг']
        #         a = df2[current_month].sum() * (prod / df[df['канал'] == 'ОПТ АМП']['Продажи']['Объем кг'].sum())
        #         return a
        #
        #     else:
        #         return 0
        #
        # stock_sebes.loc[:, ('Адм. расходы', 'Адм. расходы АМП тг/кг')] = stock_sebes.apply(
        #     lambda x: func(x, stock_sebes, curr_adm_cost_AMP), axis=1) / stock_sebes['Продажи']['Объем кг'] * 1000
        #
        # stock_sebes.loc[:, ('Адм. расходы', 'Итого тг/кг')] = stock_sebes.loc[:,
        #                                                       ('Адм. расходы', 'Адм. расходы АМД тг/кг')] + \
        #                                                       stock_sebes.loc[:,
        #                                                       ('Адм. расходы', 'Адм. расходы АМП тг/кг')]
        #
        # #         блок сс
        #
        # stock_sebes.loc[:, ('СС', 'С/с реализованной продукции тг/кг')] = stock_sebes.loc[:,
        #                                                                   ('Себестоимость', 'Итого тг/кг')]
        #
        # sum_cols = [x for x in stock_sebes['Себестоимость'].columns if
        #             x not in ['Мясосырье, Птицевосдтво, тг/кг', 'C/c мясосырья, Птицеводство тг/кг', 'Итого тг/кг']]
        #
        # stock_sebes.loc[:, ('СС', 'С/с реализованной продукции ДиП тг/кг')] = stock_sebes['Себестоимость'][
        #     sum_cols].sum(axis=1)
        #
        # stock_sebes.loc[:, ('СС', 'C/c мясосырья, Птицеводство тг/кг')] = stock_sebes.loc[:, ('Себестоимость',
        #                                                                                       'C/c мясосырья, Птицеводство тг/кг')]
        #
        # stock_sebes.loc[:, ('СС', 'Полная с/с реализованной продукции тг/кг')] = stock_sebes.loc[:, (
        #                                                                                             'Расходы по реализации',
        #                                                                                             'Итого тг/кг')] + \
        #                                                                          stock_sebes.loc[:,
        #                                                                          ('Адм. расходы', 'Итого тг/кг')] + \
        #                                                                          stock_sebes.loc[:, ('СС',
        #                                                                                              'С/с реализованной продукции тг/кг')]
        #
        # sum_cols_r = [x for x in stock_sebes['Расходы по реализации'] if x not in ['Итого тг/кг']]
        # sum_cols_adm = [x for x in stock_sebes['Адм. расходы'] if x not in ['Итого тг/кг']]
        #
        # stock_sebes.loc[:, ('СС', 'Полная с/с реализованной продукции ДиП тг/кг')] = \
        # stock_sebes['Расходы по реализации'][sum_cols_r].sum(axis=1) + \
        # stock_sebes['Адм. расходы'][sum_cols_adm].sum(axis=1) + \
        # stock_sebes.loc[:, ('СС', 'С/с реализованной продукции ДиП тг/кг')]
        #
        # stock_sebes.loc[:, ('СС', 'EBITDA по SKU (AKZ) тг/кг')] = stock_sebes.loc[:, ('Продажи', 'Цена тг/кг')] - \
        #                                                           stock_sebes.loc[:,
        #                                                           ('СС', 'Полная с/с реализованной продукции тг/кг')]
        #
        # stock_sebes.loc[:, ('СС', 'EBITDA margin по SKU (AKZ) тг/кг')] = stock_sebes.loc[:,
        #                                                                  ('СС', 'EBITDA по SKU (AKZ) тг/кг')] / \
        #                                                                  stock_sebes.loc[:, ('Продажи', 'Цена тг/кг')]
        #
        # #         Блок пг
        #
        # pr_copy = stock_sebes['Продажи'].copy()
        # pr_copy['Доходы тыс. тг'] = pr_copy['Объем кг'] * pr_copy['Цена тг/кг']
        # pr_copy.drop('Цена тг/кг', axis=1, inplace=True)
        #
        # a = stock_sebes['Себестоимость'].multiply(stock_sebes['Продажи']['Объем кг'], axis="index") / 1000
        # c = stock_sebes['Расходы по реализации'].multiply(stock_sebes['Продажи']['Объем кг'], axis="index") / 1000
        # b = stock_sebes['Адм. расходы'].multiply(stock_sebes['Продажи']['Объем кг'], axis="index") / 1000
        #
        # cons_pg = pd.concat([pr_copy, a, c, b], axis=1)
        #
        # ml = pd.MultiIndex.from_tuples([('Для ПГ', x) for x in cons_pg.columns])
        #
        # cons_pg.columns = ml
        #
        # stock_sebes = pd.concat([stock_sebes, cons_pg], axis=1)

        cons_table_dict[current_month] = stock_sebes

        if ind___ + 1 == month:
            return cons_table_dict

#         return template_for_ss_sku.set_index(['Артикул','канал','Наименование','продукт'])