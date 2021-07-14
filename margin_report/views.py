import os
from io import StringIO, BytesIO
from typing import IO

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
            file = request.FILES['test']
            df = pd.read_excel(file,sheet_name='Для СС АМП',header=[0,1])
            df = df.set_index('№ п/п')
            # df = pd.DataFrame({'hhhh':[1,2,3]})

            output = BytesIO()

            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1')
            writer.save()

            output.seek(0)
            # workbook = output.getvalue()

            response = StreamingHttpResponse(output,
                                             content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename=test.xlsx'

            return response

        except MultiValueDictKeyError:
            return HttpResponse('При загрузке Файла произошла ошибка')