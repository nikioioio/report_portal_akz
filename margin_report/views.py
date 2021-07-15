import os
from io import StringIO, BytesIO
from modules.margin_report.module_ssmp import get_ssmp_ukpf


import xlsxwriter
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
import pandas as pd

# Create your views here.

def starting_page(request):
    title = 'Margin Report'
    return render(request, "margin_report/index.html",context={'title':title})

@csrf_exempt
def upload_files(request):

    if request.method == 'POST':
        try:

            df_amp_and_amd = request.FILES['amp_and_amd']
            df_mpf = request.FILES['МПФ']
            df_ukpf = request.FILES['УКПФ']
            df_mapping= request.FILES['mapping']
            df_koef_cen = request.FILES['koef_cen']
            df_ost_mpf = request.FILES['ost_mpf']
            df_ost_ukpf = request.FILES['ost_ukpf']
            year_ = request.POST['year']
            month_ = request.POST['month']

            df = pd.read_excel(df_mpf,sheet_name='3 передел',header=[0,1])

            global_index = ['Артикул', 'Продукция', 'Номенклатура', 'Канал', 'Тип']

            prod_MPF,ost_MPF,per_1_mpf,per_2_mpf = get_ssmp_ukpf(file_factory=df_mpf,file_mapping=df_mapping,file_coef_cenn=df_koef_cen,file_ost_nach_g=df_ost_mpf,mon=int(month_),global_index=global_index,filename='МПФ',year_report=int(year_))


            # df1 = pd.DataFrame({'hhhh':[1,2,3]})
            output = BytesIO()

            # Возврат на frontend файла excel
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            ost_MPF.to_excel(writer, sheet_name='Sheet1')
            # df1.to_excel(writer, sheet_name='Sheet2')
            writer.save()

            output.seek(0)
            # workbook = output.getvalue()

            response = StreamingHttpResponse(output,
                                             content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename=test.xlsx'

            return response


        except MultiValueDictKeyError:
            return HttpResponse('При загрузке Файла произошла ошибка')