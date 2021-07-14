from django.shortcuts import render

# Create your views here.

def starting_page(request):
    title = 'Margin Report'
    return render(request, "margin_report/index.html",context={'title':title})