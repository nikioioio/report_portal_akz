import os
import numpy as np
import datetime
import json
import logging
from io import StringIO, BytesIO
from modules.margin_report.module_ssmp import get_ssmp_ukpf
from modules.margin_report.get_amd_sebes import get_amd_sebes
from modules.margin_report.get_ss_amp import get_ss_amp
from modules.margin_report.get_ss_sku import get_ss_sku

import xlsxwriter
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from multiprocessing import Pool
import sys
from modules.margin_report.builtin_functions import generate_exlx_for_ajax,generate_exlx_for_ajax_test
import traceback
# Create your views here.
from modules.margin_report.perralel_read_files import get_files
import base64
# Функция превращает массив df в кодировку для отправки на фронт
def toBase64_arr(arr):
    t = []
    for i, df in enumerate(range(len(arr))):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df = arr[i]
        df.to_excel(writer, sheet_name='test')
        writer.save()
        output = base64.b64encode(output.getvalue()).decode()
        t.append(output)
    return t
# Функция превращает массив кодировок в df
def fromBase64to_arr(base64Arr, dict_pars):
    t = []
    for i, df in enumerate(range(len(base64Arr))):
        if dict_pars[i] == 'ost_nach':
            df = pd.read_excel(base64.b64decode(base64Arr[i]),index_col=0)
            t.append(df)
        elif dict_pars[i] == 0:
            df = pd.read_excel(base64.b64decode(base64Arr[i]))
            t.append(df)
        else:
            df = pd.read_excel(base64.b64decode(base64Arr[i]), header=dict_pars[i])
            t.append(df)
    return t
# Функция превращает словарь df в кодировку для отправки на фронт
def toBase64_dict(dict_):
    for key in dict_.keys():
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df = dict_[key]
        df.to_excel(writer, sheet_name='test')
        writer.save()
        output = base64.b64encode(output.getvalue()).decode()
        dict_[key] = output
    return dict_
# Функция убирает unnamed наименования столбцов И меняет их на ''
def replace_unnamed(df):
    cons = []
    col_list = list(df.columns)
    for i, val in enumerate(col_list):
        lst = list(col_list[i])
        for j, val in enumerate(lst):
            lst[j] = str(lst[j])
            try:
                if lst[j].find('Unnamed')!=-1:
                    lst[j]=''
            except AttributeError:
                pass

        cons.append(tuple(lst))

    df.columns = pd.MultiIndex.from_tuples(cons)
    df = df.set_index('Артикул').drop('',axis = 1)

    cons = []
    col_list = list(df.columns)
    for i, val in enumerate(col_list):
        lst = list(col_list[i])
        for j, val in enumerate(lst):
            try:
                lst[j] = datetime.datetime.strptime(lst[j], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

        cons.append(tuple(lst))

    df.columns = pd.MultiIndex.from_tuples(cons)

    return df

# Функция зименяет ключи словаря в формате даты на тип строки для преедачи на клиенту
def replaceDatetimeKeysToStr(dict_):
    for key in dict_.copy():
        dict_[str(key)] = dict_.pop(key)
    return dict_


# Функция зименяет ключи словаря в формате строки на тип даты
def replaceStrTODatetime(dict_):
    for key in dict_.copy():
        dict_[datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S')] = dict_.pop(key)
    return dict_

# Функция превращает словарь из кодировке base 64 в словарь с df
def fromBase64to_dict(dict_):
    for key in dict_:
            df = pd.read_excel(base64.b64decode(dict_[key]))
            dict_[key] = df
    return dict_

logger = logging.getLogger(__name__)
# Показ стартовой страницы по маржинальности
def starting_page(request):
    title = 'Margin Report'
    return render(request, "margin_report/index.html", context={'title': title})



# Прием файлов и расчет
@csrf_exempt
def upload_files(request):
    # try:
    #     a = 1/0
    #     # raise TypeError('hi')
    # except Exception as e:
    #     return HttpResponse(e.args,status=500)

    if request.method == 'POST':
        try:
            df_amp_and_amd = request.FILES['amp_and_amd']
            df_mpf = request.FILES['МПФ']
            df_ukpf = request.FILES['УКПФ']
            df_mapping = request.FILES['mapping']
            df_koef_cen = request.FILES['koef_cen']
            df_ost_mpf = request.FILES['ost_mpf']
            df_ost_ukpf = request.FILES['ost_ukpf']
            df_ost_amd = request.FILES['ost_amd']
            df_ost_amp = request.FILES['ost_amp']
            df_amort = request.FILES['amort']
            year_ = request.POST['year']
            month_ = request.POST['month']


            dict_pars = [['Продажи ГП', 0],
                         ['Остатки', 0],
                         ['Адм', 0],
                         ['РР', 0],
                         ['3 передел', 0],
                         ['2 передел мясо', 0],
                         ['2 передел гп', 0],
                         ['2 передел потери', 0],
                         ['1 передел', 0],
                         ['Накладные затраты', [0, 1, 2]],
                         ['УиС', 0],
                         ['Общие данные по выходу', 0],
                         ['Выпуск ГП', 0],
                         ['ММО', [0, 1]]]



            try:

                arrs_input_func_ukpf = [(df_ukpf, x[0], x[1], int(year_), int(month_)) for x in dict_pars] + [
                    (df_mapping, 'Mapping', [0, 1], int(year_), int(month_)),
                    (df_koef_cen, 'Лист1', 0, int(year_), int(month_)),
                    (df_ost_ukpf, 'Sheet1', 'ost_nach', int(year_), int(month_))]

                arrs_input_func_mpf = [(df_mpf, x[0], x[1], int(year_), int(month_)) for x in dict_pars] + [
                    (df_mapping, 'Mapping', [0, 1], int(year_), int(month_)),
                    (df_koef_cen, 'Лист1', 0, int(year_), int(month_)),
                    (df_ost_mpf, 'Sheet1', 'ost_nach', int(year_), int(month_))]

                pool = Pool(processes=4)
                df_list_ukpf = pool.map(get_files, arrs_input_func_ukpf)
                df_list_mpf = pool.map(get_files, arrs_input_func_mpf)


                pool.close()





            except Exception as e:
                pool.close()
                logger.error(str(traceback.format_exc()).encode())
                return JsonResponse({'error': str(traceback.format_exc()).encode().decode('utf-8', 'ignore'),
                                     'error1': str(e.args).encode().decode('utf-8', 'ignore')}, status=500)

            return JsonResponse({'df_list_ukpf':toBase64_arr(df_list_ukpf),
                                 'df_list_mpf': toBase64_arr(df_list_mpf),
                                 'month_':month_,
                                 'year_':year_})
            # return  generate_exlx_for_ajax(int(year_),ost_MPF,ost_UKPF,prod_MPF,prod_UKPF,per_1_mpf,per_2_mpf,per_1_UKPF, per_2_UKPF,ss_sku,zak_u_amd_amp,sebes_real_pr_AMD,ost_AMD,ost_AMP_d)

        except Exception as e:
            logger.error(str(traceback.format_exc()).encode())
            return JsonResponse({'error': str(traceback.format_exc()).encode().decode('utf-8', 'ignore'),
                                 'error1': str(e.args).encode().decode('utf-8', 'ignore')}, status=500)

@csrf_exempt
def secondIteration(request):
    if request.method == 'POST':
        try:
            dict_pars = [0,
                         0,
                         0,
                         0,
                         0,
                         0,
                         0,
                         0,
                         0,
                         [0, 1, 2],
                         0,
                         0,
                         0,
                         [0, 1],
                         [0, 1],
                         0,
                         'ost_nach'
                         ]



            global_index = ['Артикул', 'Продукция', 'Номенклатура', 'Канал', 'Тип']
            df_amp_and_amd = request.FILES['amp_and_amd']
            df_ost_amd = request.FILES['ost_amd']
            df_ost_amp = request.FILES['ost_amp']
            df_amort = request.FILES['amort']
            df_mapping = request.FILES['mapping']
            df_mpf = request.FILES['МПФ']
            df_ukpf = request.FILES['УКПФ']


            firstIteration = request.POST['firstIteration']

            jsonLoad = json.loads(firstIteration)

            df_list_ukpf = fromBase64to_arr(jsonLoad['df_list_ukpf'], dict_pars)
            df_list_mpf = fromBase64to_arr(jsonLoad['df_list_mpf'], dict_pars)
            month_ = jsonLoad['month_']
            year_ = jsonLoad['year_']

            arrs_get_ssmp = [(df_list_mpf, int(month_), global_index, 'МПФ', int(year_)),
                             (df_list_ukpf, int(month_), global_index, 'УКПФ', int(year_))]

            pool = Pool(processes=4)

            ss_mp = pool.map(get_ssmp_ukpf, arrs_get_ssmp)

            # pool.close()

            prod_MPF, ost_MPF, per_1_mpf, per_2_mpf = ss_mp[0]

            prod_UKPF, ost_UKPF, per_1_UKPF, per_2_UKPF = ss_mp[1]
            # amd_sebes
            arrs_for_amd_sebes = [  (df_ost_amd, 'Sheet1', 'ost_nach', int(year_), int(month_)),
                                    (df_amp_and_amd, 'Продажи бюдж', [0, 1], int(year_), int(month_)),
                                    (df_amp_and_amd, 'Остатки АМД', [0, 1], int(year_), int(month_)),
                                    (df_amp_and_amd, 'Отчет СС АМП', [0, 1, 2], int(year_), int(month_)),
                                    (df_amp_and_amd, 'Остатки АМП', 0, int(year_), int(month_)),
                                    (df_amp_and_amd, 'Для СС АМП', [0, 1], int(year_), int(month_))]

            # pool = Pool(processes=4)
            df_list_amd = pool.map(get_files, arrs_for_amd_sebes)
            # pool.close()

            ost_AMD, budj_AMD, bolv, sebes_amp, ost_AMP, sebes_amp_new = get_amd_sebes(prod_UKPF,
                                                                                       ost_UKPF,
                                                                                       prod_MPF,
                                                                                       ost_MPF,
                                                                                       int(year_),
                                                                                       df_list_amd,
                                                                                       int(month_),
                                                                                       global_index)

            pool.close()




        except Exception as e:
            print(e)
            logger.error(str(traceback.format_exc()).encode())
            return JsonResponse({'error': str(traceback.format_exc()).encode().decode('utf-8', 'ignore'),
                                 'error1': str(e.args).encode().decode('utf-8', 'ignore')}, status=500)



        return JsonResponse({'month_':month_,
                            'year_':year_,
                            'budj_AMD':toBase64_arr(list([budj_AMD.reset_index()])),
                             'bolv': toBase64_arr(list([bolv])),
                             'ost_AMD':toBase64_arr(list([ost_AMD])),
                             'sebes_amp': toBase64_arr(list([sebes_amp.reset_index()])),
                             'ost_AMP': toBase64_arr(list([ost_AMP])),
                             'sebes_amp_new':toBase64_arr(list([sebes_amp_new.reset_index()])),
                             'ost_MPF': toBase64_arr(list([ost_MPF])),
                             'ost_UKPF': toBase64_arr(list([ost_UKPF])),
                             'prod_MPF': replaceDatetimeKeysToStr(toBase64_dict(prod_MPF)),
                             'prod_UKPF': replaceDatetimeKeysToStr(toBase64_dict(prod_UKPF)),
                             'per_1_mpf': replaceDatetimeKeysToStr(toBase64_dict(per_1_mpf)),
                             'per_2_mpf': replaceDatetimeKeysToStr(toBase64_dict(per_2_mpf)),
                             'per_1_UKPF': replaceDatetimeKeysToStr(toBase64_dict(per_1_UKPF)),
                             'per_2_UKPF': replaceDatetimeKeysToStr(toBase64_dict(per_2_UKPF))})





@csrf_exempt
def thirdIteration(request):

    if request.method == 'POST':
        try:

            global_index = ['Артикул', 'Продукция', 'Номенклатура', 'Канал', 'Тип']


            df_ost_amp = request.FILES['ost_amp']
            df_mapping = request.FILES['mapping']
            df_amort = request.FILES['amort']
            df_amp_and_amd = request.FILES['amp_and_amd']
            df_mpf = request.FILES['МПФ']
            df_ukpf = request.FILES['УКПФ']

            secondIteration = request.POST['secondIteration']
            jsonLoad = json.loads(secondIteration)
            month_ = jsonLoad['month_']
            year_ = jsonLoad['year_']

            budj_AMD = replace_unnamed(fromBase64to_arr(jsonLoad['budj_AMD'], [[0,1]])[0])


            bolv = fromBase64to_arr(jsonLoad['bolv'], [[0]])[0]
            ost_AMD = replace_unnamed(fromBase64to_arr(jsonLoad['ost_AMD'], [[0,1,2]])[0]).reset_index()
            sebes_amp = replace_unnamed(fromBase64to_arr(jsonLoad['sebes_amp'], [[0,1]])[0])
            ost_AMP = fromBase64to_arr(jsonLoad['ost_AMP'], [[0]])[0]
            sebes_amp_new = replace_unnamed(fromBase64to_arr(jsonLoad['sebes_amp_new'], [[0,1,2]])[0])


            # для  сохранения

            ost_MPF = replace_unnamed(fromBase64to_arr(jsonLoad['ost_MPF'], [[0,1,2]])[0])
            ost_UKPF = replace_unnamed(fromBase64to_arr(jsonLoad['ost_UKPF'], [[0,1,2]])[0])
            prod_MPF = fromBase64to_dict(replaceStrTODatetime(jsonLoad['prod_MPF']))
            prod_UKPF = fromBase64to_dict(replaceStrTODatetime(jsonLoad['prod_UKPF']))
            per_1_mpf = fromBase64to_dict(replaceStrTODatetime(jsonLoad['per_1_mpf']))
            per_2_mpf = fromBase64to_dict(replaceStrTODatetime(jsonLoad['per_2_mpf']))
            per_1_UKPF = fromBase64to_dict(replaceStrTODatetime(jsonLoad['per_1_UKPF']))
            per_2_UKPF = fromBase64to_dict(replaceStrTODatetime(jsonLoad['per_2_UKPF']))

            # # get_ss_amp
            arrs_for_amp_sebes = [(df_ost_amp, 'Sheet1', 'ost_nach', int(year_), int(month_)),
                                  (df_mapping, 'Mapping', [0, 1], int(year_), int(month_)),
                                  (df_amort, 'Амортизация', 0, int(year_), int(month_))]

            pool = Pool(processes=4)
            df_list_amp = pool.map(get_files, arrs_for_amp_sebes)
            # pool.close()
            #
            #
            ost_AMP_d, template_for_ss_sku, mapping, zak_u_amd_amp, sebes_real_pr_AMD = get_ss_amp(int(month_),
                                                                                                   budj_AMD,
                                                                                                   global_index,
                                                                                                   int(year_),
                                                                                                   bolv,
                                                                                                   ost_AMD,
                                                                                                   sebes_amp,
                                                                                                   df_list_amp,
                                                                                                   ost_AMP,
                                                                                                   sebes_amp_new)
            #
            #
            # #     get_ss_sku
            #
            arrs_for_ss_sku_itog = [(df_amp_and_amd, 'РР АМД', 0, int(year_), int(month_)),
                                    (df_amp_and_amd, 'РР АМП', 0, int(year_), int(month_)),
                                    (df_mpf, 'РР', 0, int(year_), int(month_)),
                                    (df_ukpf, 'РР', 0, int(year_), int(month_)),
                                    (df_amp_and_amd, 'ОАР АМП', 0, int(year_), int(month_)),
                                    (df_amp_and_amd, 'ОАР АМД', 0, int(year_), int(month_))]

            # pool = Pool(processes=4)
            df_list_ss_sku_itog = pool.map(get_files, arrs_for_ss_sku_itog)

            #
            ss_sku = get_ss_sku(template_for_ss_sku, budj_AMD, ost_AMP_d, ost_AMD, mapping, int(month_), int(year_),
                                df_list_ss_sku_itog, global_index)

            pool.close()




        except Exception as e:
            print(e)
            logger.error(str(traceback.format_exc()).encode())
            return JsonResponse({'error': str(traceback.format_exc()).encode().decode('utf-8', 'ignore'),
                                 'error1': str(e.args).encode().decode('utf-8', 'ignore')}, status=500)



        return  generate_exlx_for_ajax(int(year_),ost_MPF,ost_UKPF,prod_MPF,prod_UKPF,per_1_mpf,per_2_mpf,per_1_UKPF, per_2_UKPF,ss_sku,zak_u_amd_amp,sebes_real_pr_AMD,ost_AMD,ost_AMP_d)




@csrf_exempt
def test_get_json(request):
    if request.method == 'POST':
        return generate_exlx_for_ajax_test()


@csrf_exempt
def test_get_json1(request):
    if request.method == 'POST':
        # df_amp_and_amd = request.FILES['amp_and_amd']
        ff = request.POST['amp_and_amd']
        bytes_io = base64.b64decode(ff)
        df = pd.read_excel(bytes_io,sheet_name='Остатки МПФ')
        print(df)
        return JsonResponse({'status':200})