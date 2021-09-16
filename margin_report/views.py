import os
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
logger = logging.getLogger(__name__)
# Показ стартовой страницы по маржинальности
def starting_page(request):
    title = 'Margin Report'
    return render(request, "margin_report/index.html", context={'title': title})

# Прием файлов и расчет
@csrf_exempt
async def upload_files(request):
    # try:
    #     a = 1/0
    #     # raise TypeError('hi')
    # except Exception as e:
    #     return HttpResponse(e.args,status=500)
    pool = Pool(processes=4)
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

            factries = ['УКПФ.xlsx', 'МПФ.xlsx']
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



                df_list_ukpf = pool.map(get_files, arrs_input_func_ukpf)
                df_list_mpf = pool.map(get_files, arrs_input_func_mpf)
                global_index = ['Артикул', 'Продукция', 'Номенклатура', 'Канал', 'Тип']




                arrs_get_ssmp = [(df_list_mpf, int(month_), global_index, 'МПФ', int(year_)),
                                 (df_list_ukpf, int(month_), global_index, 'УКПФ', int(year_))]

                ss_mp = pool.map(get_ssmp_ukpf, arrs_get_ssmp)

                pool.close()

                prod_MPF, ost_MPF, per_1_mpf, per_2_mpf = ss_mp[0]

                prod_UKPF, ost_UKPF, per_1_UKPF, per_2_UKPF = ss_mp[1]
                # amd_sebes
                arrs_for_amd_sebes = [  (df_ost_amd, 'Sheet1', 'ost_nach', int(year_), int(month_)),
                                        (df_amp_and_amd, 'Продажи бюдж', [0, 1], int(year_), int(month_)),
                                        (df_amp_and_amd, 'Остатки АМД', [0, 1], int(year_), int(month_)),
                                        (df_amp_and_amd, 'Отчет СС АМП', [0, 1, 2], int(year_), int(month_)),
                                        (df_amp_and_amd, 'Остатки АМП', 0, int(year_), int(month_)),
                                        (df_amp_and_amd, 'Для СС АМП', [0, 1], int(year_), int(month_))]

                pool = Pool(processes=4)
                df_list_amd = pool.map(get_files, arrs_for_amd_sebes)
                pool.close()

                ost_AMD, budj_AMD, bolv, sebes_amp, ost_AMP, sebes_amp_new = get_amd_sebes(prod_UKPF,
                                                                                           ost_UKPF,
                                                                                           prod_MPF,
                                                                                           ost_MPF,
                                                                                           int(year_),
                                                                                           df_list_amd,
                                                                                           int(month_),
                                                                                           global_index)
                # # get_ss_amp
                arrs_for_amp_sebes = [(df_ost_amp, 'Sheet1', 'ost_nach', int(year_), int(month_)),
                                      (df_mapping, 'Mapping', [0, 1], int(year_), int(month_)),
                                      (df_amort, 'Амортизация', 0, int(year_), int(month_))]

                pool = Pool(processes=4)
                df_list_amp = pool.map(get_files, arrs_for_amp_sebes)
                pool.close()
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

                pool = Pool(processes=4)
                df_list_ss_sku_itog = pool.map(get_files, arrs_for_ss_sku_itog)

                #
                ss_sku = get_ss_sku(template_for_ss_sku, budj_AMD, ost_AMP_d, ost_AMD, mapping, int(month_), int(year_), df_list_ss_sku_itog,global_index)

                pool.close()





            except Exception as e:
                pool.close()
                print(e)
                logger.error(str(traceback.format_exc()).encode())
                return JsonResponse({'error': str(traceback.format_exc()).encode().decode('utf-8', 'ignore'),
                                     'error1': str(e.args).encode().decode('utf-8', 'ignore')}, status=500)


            return await generate_exlx_for_ajax(int(year_),ost_MPF,ost_UKPF,prod_MPF,prod_UKPF,per_1_mpf,per_2_mpf,per_1_UKPF, per_2_UKPF,ss_sku,zak_u_amd_amp,sebes_real_pr_AMD,ost_AMD,ost_AMP_d)

        except MultiValueDictKeyError:
            return HttpResponse('При загрузке Файла произошла ошибка')




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