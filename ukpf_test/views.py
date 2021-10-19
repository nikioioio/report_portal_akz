from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
import json
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import os
from io import StringIO, BytesIO
from modules.margin_report.module_ssmp import get_ssmp_ukpf

import xlsxwriter
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import datetime
import numpy as np
import warnings

warnings.filterwarnings('ignore')
from multiprocessing import Pool
import sys


def starting_page(request):
    title='Модель производственного планирования ЗПП УКПФ'
    return render(request, "ukpf_test/index.html", context={'title': title})


@csrf_exempt
def upload_files(request):
    if request.method == 'POST':
        # try:
        uboi=request.FILES['uboi']
        zakaz=request.FILES['zakaz']
        df=pd.read_csv(uboi)
        # print(df)
        output=BytesIO()

        # Возврат на frontend файла excel
        writer=pd.ExcelWriter(output, engine='xlsxwriter')
        df2=pd.read_csv('планирование_зпп.csv')
        df2.to_excel(writer, sheet_name='Sheet1')
        # ost_UKPF.to_excel(writer, sheet_name='Sheet2')
        writer.save()

        output.seek(0)
        # workbook = output.getvalue()

        response=StreamingHttpResponse(output,
                                       content_type='application/vnd.ms-excel')
        response['Content-Disposition']=f'attachment; filename=margin.xlsx'

        return response


def df_to_json(df):
    def get_razd(sx_razd, v_):
        ch_razd={}
        #     если это деловая часть
        for ind in sx_razd.index:

            if sx_razd.at[ind, 'Из какой части пром'] == 0:
                v___=v_ * sx_razd.at[ind, 'Процент разделки']
                #         df_cons = df_cons.append(pd.DataFrame({'Дата забоя':df['Дата забоя'],'Градация':grad,'Наименование части':fff.at[ind,'Часть'],'Объем':v___}))
                ch_razd[sx_razd.at[ind, 'Часть']]=v___

        for ind in sx_razd.index:
            #     для пром
            if sx_razd.at[ind, 'Из какой части пром'] != 0:
                #         print(fff.at[ind,'Из какой части пром'])
                #         Процент вет брака
                pr_vetbr=sx_razd[(sx_razd['Из какой части пром'] == sx_razd.at[ind, 'Из какой части пром']) & (
                    sx_razd['Часть'] == sx_razd.at[ind, 'Часть'])]['Процент разделки'].values
                v_pochasti=ch_razd[sx_razd.at[ind, 'Из какой части пром']]
                it_prom=pr_vetbr * v_pochasti
                ch_razd[sx_razd.at[ind, 'Часть']]=it_prom
                ch_razd[sx_razd.at[ind, 'Из какой части пром']]=ch_razd[sx_razd.at[ind, 'Из какой части пром']] - \
                                                                ch_razd[sx_razd.at[ind, 'Часть']]

        #     Выбираем минимальное из деловых частей (там где больше одного элемента)
        for ind in sx_razd.index:
            ch_razd[sx_razd.at[ind, 'Часть']]=min(ch_razd[sx_razd.at[ind, 'Часть']])

        for key___ in ch_razd.keys():
            ch_razd[key___]=ch_razd[key___].sum()
        return ch_razd

    # делит по 100 гр
    def get_po_sto_gr(inp):
        inp=inp.set_index('Дата забоя')
        df=pd.DataFrame(inp.index)
        df=df.set_index('Дата забоя')
        for ind, col in enumerate(inp.columns):
            #         print(col.split('-')[0]=='2,500')
            try:
                if col.split('-')[0] == '2,500':
                    df['2,500-3,500']=inp['2,500-3,500']
                #                 print(col)

                if ind == 0 or ind % 2 == 0:
                    cols=inp.iloc[:, [ind, ind + 1]].columns
                    df[cols[0].split('-')[0] + '-' + cols[1].split('-')[1]]=inp.iloc[:, [ind, ind + 1]].sum(axis=1)


            except IndexError:
                pass
        return df.reset_index()

    # логика формирования итогового фрейма

    def get_cons_arr(df_gr, dict_, chema_r, dict_sx):

        df_cons=pd.DataFrame()
        for date in df_gr['Дата забоя'].unique():

            df=df_gr[df_gr['Дата забоя'] == date]

            for grad in dict_.keys():

                v_razd=df[grad].values * dict_[grad]
                v_cb=df[grad].values * (1 - dict_[grad])

                #         Часть с разделкой
                if v_razd > 0:

                    #             print(v_razd)

                    #             Иду по пропорции разделки
                    for el_sx in dict_sx.keys():

                        #                 Объем по схеме
                        v_=v_razd * dict_sx[el_sx]
                        #                 print(str(v_razd)+' '+ str(v_))
                        sx_razd=chema_r[chema_r['Номер'] == el_sx]
                        it_chema=get_razd(sx_razd, v_)
                        for key_ in it_chema.keys():
                            df_cons=df_cons.append(pd.DataFrame(
                                {'Дата забоя': df['Дата забоя'], 'Градация': grad, 'Наименование части': key_,
                                 'Объем': it_chema[key_]}))
                #                     print(key_)
                #                     break
                #                 break

                #                 print('общий объем'+ str(v_razd) + ' Объем на конкретную схему эту '+str(v_))

                #         Часть ЦБ
                if v_cb > 0:
                    df_cons=df_cons.append(pd.DataFrame(
                        {'Дата забоя': df['Дата забоя'], 'Градация': grad, 'Наименование части': 'ЦБ', 'Объем': v_cb}))
        return df_cons

    # разбивает часть по процентц в аргументе
    def calc_division_ch(cons2, from_name, to_name, percent):
        for_ch_okor=cons2.loc[cons2['Наименование части'] == from_name]
        ost_okor=cons2.loc[cons2['Наименование части'] == from_name]

        for col in for_ch_okor.columns:
            try:
                for_ch_okor.loc[:, col]=for_ch_okor.loc[:, col] * percent
            except TypeError:
                pass

        for col in ost_okor.columns:
            if ost_okor[col].dtype == 'float':
                cons2.loc[cons2['Наименование части'] == from_name, col]=ost_okor[col] - for_ch_okor[col]

        for_ch_okor['Наименование части']=to_name

        cons2=cons2.append(for_ch_okor).reset_index(drop=True)
        return cons2

    # формирование чахохбили
    #

    # суммирует значения с фильтром по числовому значению
    def total_sum(name_col, value_, df):
        sum_=0
        for str_ in df[df[name_col] == value_].sum():
            if isinstance(str_, np.float64):
                sum_=sum_ + str_

        return sum_

    # Формирование чахохбили из объема

    """Параметры : cons2:обрабобатываемый df
                   from_name: часть откуда бурем 
                   to_name: часть куда транспортируем объем
                   percent: процент по анатомии
                   tagret_val: целевой объем to_name"""

    def calc_dop_chakh(cons2, from_name, to_name, percent, tagret_val):

        target_calc=tagret_val * percent

        for_ch_okor=cons2.loc[cons2['Наименование части'] == from_name]
        ost_okor=cons2.loc[cons2['Наименование части'] == from_name]

        tot_sum=total_sum('Наименование части', from_name, cons2)
        if target_calc >= tot_sum:
            print('Не возможно сделать данный объем ' + to_name + ' из ' + from_name + ', уменьшите его')
            return 0
        for col in for_ch_okor.columns:
            if for_ch_okor[col].dtype == 'float':
                for_ch_okor.loc[cons2['Наименование части'] == from_name, col]=for_ch_okor.loc[cons2[
                                                                                                   'Наименование части'] == from_name, col] / tot_sum * target_calc

        for col in ost_okor.columns:
            if ost_okor[col].dtype == 'float':
                cons2.loc[cons2['Наименование части'] == from_name, col]=ost_okor[col] - for_ch_okor[col]

        for_ch_okor['Наименование части']='Сырье для чахохбили'

        cons2=cons2.append(for_ch_okor).reset_index(drop=True)

        return cons2

    df2=df[['Часть', 'Позиция SKU', 'Канал', 'Объем исполнения', 'Объем заказа']]
    # print(df2)
    df2_1=df2.groupby(['Часть']).sum().reset_index()
    cols=['Объем исполнения', 'Объем заказа']
    df2_1[cols]=df2_1[cols].round(2)
    b={}
    for i in df2_1.values:
        b[i[0]]=[i[1], i[2]]
    df2_2=df2.groupby(['Часть', 'Позиция SKU']).sum().reset_index()
    cols=['Объем исполнения', 'Объем заказа']
    df2_2[cols]=df2_2[cols].round(2)
    for i in b.keys():
        b[i].append([])
    for j in df2_2.values:
        b[j[0]][2].append({j[1]: [j[2], j[3]]})
    df2_3=df2.groupby(['Часть', 'Позиция SKU', 'Канал']).sum().reset_index()
    cols=['Объем исполнения', 'Объем заказа']
    df2_3[cols]=df2_3[cols].round(2)
    for j in df2_3.values:
        for i in range(len(b[j[0]][2])):
            try:
                b[j[0]][2][i][j[1]].append({j[2]: [j[3], j[4]]})
            except:
                pass
    return b


def json_to_df(res):
    ww=[]
    w={}
    for i in res.keys():
        for j in res[i][2]:
            for k in j.keys():
                for l in range(2, len(j[k])):
                    for f in (j[k][l].keys()):
                        w['Часть']=i
                        w['Позиция SKU']=k
                        w['Канал']=f
                        if len(j[k][l][f]) > 1:
                            w['Объем исполнения']=j[k][l][f][0]
                            w['Объем заказа']=j[k][l][f][1]
                        else:
                            w['Объем исполнения']=0
                            w['Объем заказа']=0
                        ww.append(w)
                        w={}
    df=pd.DataFrame(ww)
    return df


def reminder(df):
    return df



@csrf_exempt
def refresh(request):
    uboi=request.FILES['uboi']
    zakaz=request.FILES['zakaz']
    df1=pd.read_csv(uboi)

    df2=pd.read_csv(zakaz)
    df=pd.read_csv('mpf_test/планирование_зпп.csv')
    df=df.round(1)
    res=df_to_json(df)
    return JsonResponse(res)


@csrf_exempt
def update(request):
    if request.method == 'POST':
        df=pd.read_csv('mpf_test/планирование_зпп.csv', index_col=0)
        df1_1=df.iloc[:, [6, 2, 1, 8, 3]]
        js_orig=df_to_json(df1_1)
        cb=js_orig['ЦБ'][0]
        file=js_orig['Филе'][0]
        krylo=js_orig['Крыло'][0]
        bedro=js_orig['Бедро'][0]
        grudka=js_orig['Грудка'][0]
        spinka=js_orig['Спинка'][0]
        chetvert=js_orig['Четвертина'][0]
        #
        # print(cb, file, krylo, bedro, grudka, spinka, chetvert)

        js=request.POST['data1']
        json_obg=json.loads(js)
        # print(json_obg)
        if cb < float(json_obg['ЦБ'][0]) or grudka < float(json_obg['Грудка'][0]) or chetvert < float(
            json_obg['Четвертина'][0]):
            return JsonResponse(js_orig)
        # print(float(json_obg['ЦБ'][0]))
        cb_=cb - float(json_obg['ЦБ'][0])
        grudka_=grudka - float(json_obg['Грудка'][0])
        chetvert_=chetvert - float(json_obg['Четвертина'][0])
        if float(json_obg['ЦБ'][0]) < 21000 or float(json_obg['Грудка'][0]) < 1100 or chetvert < float(
            json_obg['Четвертина'][0]) < 1500:
            cb_=cb - 21000
            grudka_=grudka - 1100
            chetvert_=chetvert - 1500
            json_obg['ЦБ'][0]=21000
            json_obg['Грудка'][0]=1100
            json_obg['Четвертина'][0]=1500
        json_obg['Крыло'][0]=round((krylo + (cb_ * 0.08)), 1)
        json_obg['Бедро'][0]=round((bedro + (cb_ * 0.19) + (chetvert_ * 0.19)), 1)
        json_obg['Грудка'][0]=round((float(json_obg['Грудка'][0]) + (cb_ * 0.03)), 1)
        json_obg['Четвертина'][0]=round((float(json_obg['Четвертина'][0]) + (cb_ * 0.01)), 1)
        json_obg['Спинка'][0]=round((spinka + (cb_ * 0.06) + (chetvert_ * 0.06)), 1)
        json_obg['Филе'][0]=round((file + (cb_ * 0.31) + (grudka_ * 0.31)), 1)
        print(json_obg['ЦБ'][2][5].keys())
        # json_obg['ЦБ'][2][5]['ЦБ 1 кат. вес. (охл.)'][0] = round((float(json_obg['ЦБ'][2][5]['ЦБ 1 кат. групп. (охл.)'][0]) - cb_), 1)
        # json_obg['ЦБ'][2][5]['ЦБ 1 кат. групп. (охл.)'][2]['Кейтеринг'][0] = round((float(json_obg['ЦБ'][2][5]['ЦБ 1 кат. групп. (охл.)'][2]['Кейтеринг'][0]) - cb_), 1)
        return JsonResponse(json_obg)
        # return JsonResponse({'status':200})


@csrf_exempt
def test_get_json(request):
    if request.method == 'POST':
        # print(5)
        # print(request.POST)
        # df = request.POST['file']
        # js = request.POST['json']
        # json_obg = json.loads(js)
        # print(json_obg)
        df=pd.read_csv('mpf_test/планирование_зпп2.csv')
        output=BytesIO()

        # Возврат на frontend файла excel
        writer=pd.ExcelWriter(output, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='УКПФ', index=False)
        writer.save()

        output.seek(0)
        # workbook = output.getvalue()
        now=datetime.datetime.now()
        date_for_name_file=now.strftime("%d-%m-%Y %H:%M")

        response=StreamingHttpResponse(output,
                                       content_type='application/vnd.ms-excel')
        response['Content-Disposition']=f'attachment; filename=plain ' + date_for_name_file + '.xlsx'

        return response
        # return JsonResponse({'status': 200})


@csrf_exempt
def test_get_json_2(request):
    if request.method == 'POST':
        # print(5)
        # print(request.POST)
        # df = request.POST['file']
        # js = request.POST['json']
        # json_obg = json.loads(js)
        # print(json_obg)
        df=pd.read_csv('mpf_test/отчет.csv')
        output=BytesIO()

        # Возврат на frontend файла excel
        writer=pd.ExcelWriter(output, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='УКПФ', index=False)
        writer.save()

        output.seek(0)
        # workbook = output.getvalue()
        now=datetime.datetime.now()
        date_for_name_file=now.strftime("%d-%m-%Y %H:%M")

        response=StreamingHttpResponse(output,
                                       content_type='application/vnd.ms-excel')
        response['Content-Disposition']=f'attachment; filename=report ' + date_for_name_file + '.xlsx'

        return response
        # return JsonResponse({'status': 200})


@csrf_exempt
def get_table(request):
    if request.method == 'POST':
        import json
        js=request.POST['data1']
        json_obg=json.loads(js)
        df=json_to_df(json_obg)
        js_={0: ['Параметр', 'Объем заявлено', 'Объем исполнено']}
        js_[1]=['Живая птица', 77944.6, 77944.6]
        js_[2]=['Вход мясо', 75944.4, 75944.4]
        js_[3]=['Исполнение заказа', 73749.4, 67982.1]
        js_[4]=['Срезано', 0, 5720.3]
        js_[5]=['Обьем заморозки', 19997.7, 37825.3]
        js_[6]=['Обьем охл', 63570.8, 50022.8]
        js_[7]=['в т.ч. Заявка', 19997.7, 16827.6]
        js_[8]=['в т.ч. Остатки', 0, 20997.7]
        js_[9]=['Обьем подложки', 54873.6, 54994.7]
        js_[10]=['% разделки', '0%', '67%']
        # ,1:['Вход мясо',1646,646545],2:['Исполнено заказа',1646,646545]}
        return JsonResponse(js_)
