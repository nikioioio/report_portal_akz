from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
import json
# Create your views here.
from django.views.decorators.csrf import csrf_exempt


def starting_page(request):
    title = 'Plain_test'
    return render(request, "plain_test/index.html", context={'title': title})


@csrf_exempt
def refresh(request):
    kr = [1000, 2000,
          [
              {'Крыло ЦБ на подложке': [3402, 3347,
                                    {'КФС': [2115, 2020], 'KA': [347, 658], 'Кейтеринг': [885, 986], 'Остаток': [0]}]},
              {'Крыло ЦБ на sdvsva': [3402, 3347,
                                        {'КФС': [2115, 5000], 'KA': [347, 658], 'Кейтеринг': [885, 986],
                                         'Остаток': [0]}]}
          ]
          ]

    ее = [500, 700,
          [
              {'Крыло ЦБ на ааа': [524, 33457857,
                                   {'КФС': [21585, 2020], 'KA': [347, 658]}]},
              {'Крыло ЦБ на аasccаа': [524, 33457857,
                                       {'КФС': [21585, 2020], 'KA': [347, 658]}]}
          ],

          ]

    json = {'Крыло': kr, 'Тушка': ее}
    return JsonResponse(json)


@csrf_exempt
def update(request):
    if request.method =='POST':
        js = request.POST['data1']
        json_obg = json.loads(js)
        print(json_obg)
        return JsonResponse({'status':200})

