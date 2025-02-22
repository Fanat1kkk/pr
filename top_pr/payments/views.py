import json

from hashlib import sha1
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .providers import PayYoomoney, PayYookassa


@csrf_exempt
def pay_yoommany(request):
    if request.method == 'POST':
        pay = PayYoomoney()
        pay.pay_status(request.POST)
        return HttpResponse('YES')
    else:
        return Http404()
    
    
@csrf_exempt
def pay_yookassa(request):
    print('pay_yookassa: ', request.method)
    if request.method == 'POST':
        # Декодируем сырые данные
        raw_data = request.body.decode('utf-8')
        # Если данные в формате JSON
        try:
            json_data = json.loads(raw_data)
            pay = PayYookassa()
            if not pay.verify_yookassa_signature(request):
                return JsonResponse({"error": "Invalid signature"}, status=405)
            pay.pay_status(json_data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=405)
        return JsonResponse({"status": "OK"}, status=200)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


# @csrf_exempt
# def pay_freecassa(request):
#     if request.method == 'POST':
#         pay = PayFreeCassa()
#         pay.pay_status(request.POST)
#         return HttpResponse('YES')
#     else:
#         return Http404()

    
    
