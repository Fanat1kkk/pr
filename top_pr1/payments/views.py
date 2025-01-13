from hashlib import sha1
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .providers import PayFreeCassa, PayYoomoney


def pay(request):
    return HttpResponse('YES')

@csrf_exempt
def pay_yoommany(request):
    if request.method == 'POST':
        pay = PayYoomoney()
        pay.pay_status(request.POST)
        return HttpResponse('YES')
    else:
        return Http404()


@csrf_exempt
def pay_freecassa(request):
    if request.method == 'POST':
        pay = PayFreeCassa()
        pay.pay_status(request.POST)
        return HttpResponse('YES')
    else:
        return Http404()

    
    