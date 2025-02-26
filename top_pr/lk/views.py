import json

from django.http import Http404, JsonResponse, HttpRequest
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage

from .forms import PasswordChangeForm, UserUpdateForm
from my_site.models import *
from my_site.forms import PayProfileForm
from payments.models import ProviderPay
from payments.providers import pm, pay_variant, pay_variant_profile
from my_site.tasks import cancel_order


@login_required(login_url='account_login')
def profile(request: HttpRequest):
    orders: Order = request.user.orders.all().prefetch_related('service').order_by('-date_create')
    if len(orders) == 0:
        orders = None
    return render(request=request, template_name='lk/profile.html', context={'orders': orders})


@login_required(login_url='account_login')
def new_order_profile(request):
    categories = Category.objects.all()
    sub_cats = []
    tariffs = []
    if len(categories) > 0:
        sub_cats = categories[0].sub_cat.all()
        tariffs = Service.objects.filter(sub_cat=sub_cats[0], category=categories[0])
    context = {
        'categories': categories,
        'sub_cats': sub_cats,
        'tariffs' : tariffs,
        # 'base_url': settings.BASE_URL,
    }
    return render(request=request, template_name='lk/new-order.html', context=context)


@login_required(login_url='account_login')
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, client=request.user)
        pay_p = pay_variant_profile()
        return render(request=request, template_name='lk/confirm_order_profile.html', context={'order': order, 
                                                                                            'pay_p': pay_p})
    except Order.DoesNotExist:
        if request.user.is_authenticated:
            return redirect('profile')
        else:
            return redirect('index')
    
    
@login_required(login_url='account_login')
def pay_balance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON"}, status=400)
        form = PayProfileForm(data)
        if form.is_valid():
            sum = Decimal(str(form.cleaned_data.get('sum')))
            pay_provider = form.cleaned_data.get('pay_provider')
            if pay_provider == 'PRF':
                return JsonResponse({'error': 'Не верный способ оплаты'})
            redirect = pm.create_pay_profile(pay_provider=pay_provider, 
                                             client=request.user, 
                                             price=sum
                                            )
            return JsonResponse({'redirect': redirect})
        else:
            errors = []
            for field in form.errors:
                for error in form.errors[field]:
                    print(field, ': ', error)
                    errors.append(error)
            return JsonResponse({'error': errors})

    else:    
        form = PayProfileForm()
        pay_p = pay_variant()
        # for provider, name in ProviderPay.PROVIDERS:
        #     if provider == 'PRF': break
            # img = next((img for p, img in ProviderPay.IMG if p == provider), None)
            # pay_p.append({
            #     'provider': provider,
            #     'name': name,
            #     'img': img
            # })
        return render(request=request, template_name='lk/pay-balance.html', context={'pay_p': pay_p,
                                                                                     'form': form})
        
        
@login_required(login_url='account_login')
def service_info(request, service_id):
    try:
        service = Service.objects.get(service_id=service_id)
    except Service.DoesNotExist:
        return Http404(request)
    return render(request=request, template_name='lk/service_info.html', context={'service': service})


@login_required(login_url='account_login')
def order_cancel(request: HttpRequest):
    if request.method == 'POST':
        order_id = json.loads(request.body).get('order_id')
        # return JsonResponse({'error': 'Заказ не может быть отменён'})
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Заказ не может быть отменён'})
        
        if order.service.is_cancellation and order.status == order.IN_WORCK:
            cancel_order.delay(order_id)
            order.set_status(Order.WAITCANCEL, True)
            return JsonResponse({'status': order.status})
        else:
            return JsonResponse({'error': 'Заказ не может быть отменён'})


@login_required(login_url='account_login')
def settings(request):
    print('first_name: ', request.user.first_name)
    if request.method == 'POST':
        # Обработка формы обновления имени и email
        if 'update_user' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                return redirect('settings')
        else: user_form = UserUpdateForm(instance=request.user)

        # Обработка формы смены пароля
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                password_form.save(request.user)
                update_session_auth_hash(request=request, user=request.user)
                return redirect('settings')
        else: password_form = PasswordChangeForm()
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm()
        
    return render(
        request=request,
        template_name='lk/settings.html',
        context={
            'user_form': user_form,
            'password_form': password_form,
        }
    )


@login_required(login_url='account_login')
def listing_history_pay(request: HttpRequest, page:int):
    transactions = request.user.transactions.profile_payments()
    paginator = Paginator(transactions, 10)
    try:
        r_page = paginator.page(page)
        next_page = r_page.has_next()
        html = render_to_string(template_name='lk/listing_pay.html', context={'page':r_page})
    except InvalidPage:
        return JsonResponse({'error': 'Invalid Page'})
    
    return JsonResponse({'ok': 
                         {'html': html,
                          'next_page': next_page}
                         })
