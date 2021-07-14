from django.http import HttpResponse
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
            df = pd.read_excel(file)
            print(df)

            return HttpResponse(200)
        except MultiValueDictKeyError:
            return HttpResponse('При загрузке Файла произошла ошибка')