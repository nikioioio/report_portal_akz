from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

def starting_page(request):
    title = 'Plain_test'
    return render(request, "plain_test/index.html", context={'title': title})

@csrf_exempt
def refresh(request):
    kr = [1000, 2000,
          {'Крыло ЦБ на подложке': [3402, 3347,
                                    {'КФС': [2115, 2020], 'KA': [347, 658], 'Кейтеринг': [885, 986], 'Остаток': [0]}]}
          ]

    ее = [500, 700,
          {'Крыло ЦБ на ааа': [524, 33457857,
                                    {'КФС': [21585, 2020], 'KA': [347, 658]}]}
          ]



    json = {'Крыло': kr,'Тушка':ее}
    return JsonResponse(json)