import json
from decimal import Decimal
from django.shortcuts import render, redirect
from django.conf import settings 
from django.http import HttpResponse, JsonResponse, Http404, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Prefetch

from allauth.account.views import LoginView, SignupView, PasswordResetFromKeyView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from payments.models import ProviderPay
from payments.providers import pm

from .models import Category, Order, Service, Subcategory, PromoCode
from .forms import OrderForm, MyLogInForm, MySignupForm, PayProfileForm, MyResetPasswordKeyForm, CommentForm
from .serializers import PromoCodeSerializer, ServiceSerializer, SubcategorySerializer, SubcategorySlugSerializer, ServiceInfoSerializer
from .exceptions import BalanceException
from .tasks import cancel_order, send_email_register_user


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class FormsMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_login = MyLogInForm()
        form_signup = MySignupForm()
        context.update({
            'form_login': form_login,
            'form_signup': form_signup,
        })
        return context


class AjaxLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            response = self.form_valid(form)
            return JsonResponse({'location': response.url})
        else:
            form.errors
            return JsonResponse({'errors': form.errors, 'errors_non_fields': form.non_field_errors()})


class AjaxSignupView(SignupView):
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            response = self.form_valid(form)
            email = form.cleaned_data['email']
            send_email_register_user(email=email)
            return JsonResponse({'location': response.url})
        else:
            return JsonResponse({'errors': form.errors, 'errors_non_fields': form.non_field_errors()})

    
class PasswordResetDoneView(FormsMixin, TemplateView):
    template_name = "my_site/account/password_reset_done.html"


class MyPasswordResetFromKeyView(FormsMixin, PasswordResetFromKeyView):
    template_name: str = "my_site/account/password_reset_from_key.html"
    form_class = MyResetPasswordKeyForm


class MyPasswordResetFromKeyDoneView(FormsMixin, TemplateView):
    template_name = "my_site/account/password_reset_from_key_done.html"


def index(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('profile')
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
        'base_url': settings.BASE_URL,
    }
    return render(request=request, template_name='my_site/index.html', context=context)


def faq(request):
    form_login = MyLogInForm()
    form_signup = MySignupForm()
    context = {
        'form_login': form_login,
        'form_signup': form_signup,
        'base_url': settings.BASE_URL,
    }
    return render(request=request, template_name='my_site/faq.html', context=context)


@api_view(['GET'])
def categories(request, category_slug):
    try:
        cat = Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:
        return Response([])
    sub_cats = cat.sub_cat.all()
    if len(sub_cats) == 0:
        return Response([])
    serializer = SubcategorySlugSerializer(sub_cats, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def services_filter(request, social, category):
    
    if social and category:
        tariffs = Service.objects.filter(category__slug=social, sub_cat__slug=category, is_published=True).prefetch_related(
            'category',
            Prefetch('category__sub_cat', queryset=Subcategory.objects.filter(slug=category)))
        serializer = ServiceInfoSerializer(tariffs, many=True)
        return Response(serializer.data)
    else: return Response([])
    

def create_order(request, tarif):
    try:
        service = Service.objects.get(slug=tarif)
    except Service.DoesNotExist:
        return Http404(request)
    return render(request=request, template_name='my_site/create_order.html', context={'service': service})


def services(request):
    services = Service.objects.filter(is_published=True)
    cats = Category.objects.all()
    return render(request=request, template_name='my_site/services.html', context={'services': services,
                                                                                   'cats': cats})


@csrf_exempt
def AJAX_profile(request):
    if request.method == 'POST' and is_ajax(request):
        form = PayProfileForm(request.POST)
        if form.is_valid():
            sum = Decimal(str(form.cleaned_data.get('sum')))
            pay_provider = form.cleaned_data.get('pay_provider')
            redirect = pm.create_pay_profile(pay_provider=pay_provider, 
                                             client=request.user, 
                                             price=sum
                                            )
            return JsonResponse({'redirect': redirect})
        else:
            errors = []
            for field in form.errors:
                for error in form.errors[field]:
                    errors.append(error)
            return JsonResponse({'error': errors})


def table_orders(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            orders = request.user.orders.exclude(status=Order.NO_PAY).order_by('-date_create')
            # Условие необходимо для добавления в контекст 'orders'
            # Так как в шаблоне отобраается таблица только если есть 'orders'
            if len(orders) > 0:
                return render(request=request, template_name='my_site/orders.html', context={'orders': orders, 
                                                                                             'email': request.user.email,
                                                                                             'base_url': settings.BASE_URL})
    form_login = MyLogInForm()
    form_signup = MySignupForm()
    context = {
        'form_login': form_login,
        'form_signup': form_signup,
        'base_url': settings.BASE_URL,
    }
    return render(request=request, template_name='my_site/orders.html', context=context)


def sort_orders(request):
    form_login = MyLogInForm()
    form_signup = MySignupForm()
    context = {
        'form_login': form_login,
        'form_signup': form_signup,
        'base_url': settings.BASE_URL,
    }

    if request.method == 'GET':
        email = request.GET.get('email')
        status = request.GET.get('status')
        if email:
            context.update({'email': email})
            if status:
                context.update({
                    'status': status
                })
                if status == 'ALL':
                    orders = Order.objects.filter(email=email).exclude(status=Order.NO_PAY).order_by('-date_create')
                else:
                    orders = Order.objects.filter(email=email, status=status).order_by('-date_create')
            else:
                orders = Order.objects.filter(email=email).order_by('-date_create')
                # Условие необходимо для добавления в контекст 'orders'
                # Так как в шаблоне отобраается таблица только если есть 'orders'
            if len(orders) > 0:
                context.update({'orders': orders})

                return render(request=request, template_name='my_site/orders.html', context=context)
            else:
                context.update({'error': f'{email} не найден.'})

    return render(request=request, template_name='my_site/orders.html', context=context)


def search_orders(request):
    form_login = MyLogInForm()
    form_signup = MySignupForm()
    context = {
        'form_login': form_login,
        'form_signup': form_signup,
    }
    if request.method == 'GET':
        email = request.GET.get('email')
        
        if email:
            orders = Order.objects.filter(email=email).exclude(status=Order.NO_PAY).order_by('-date_create')
            # Условие необходимо для добавления в контекст 'orders'
            # Так как в шаблоне отобраается таблица только если есть 'orders'
            if len(orders) > 0:
                context.update({'orders': orders,
                                'email': email})
                return render(request=request, template_name='my_site/orders.html', context=context)
            else:
                context.update({'error': f'{email} не найден.'})
            
    return render(request=request, template_name='my_site/orders.html', context=context)


def AJAX_pay(request):
    return JsonResponse({'good': 'goood'})


def successful_pay(request):
    return HttpResponse(f'POST: {request.POST}\nGET: {request.GET}')


@csrf_exempt
def AJAX_checked_pay(request):
    if request.method == 'POST' and is_ajax(request):
        order_id = request.POST.get('order_id', None)
        if order_id is None:
            return JsonResponse({'error': 'error None'})
        try:
            order = Order.objects.get(order_id=order_id)
            if order.is_paid:
                url = settings.BASE_URL
                return JsonResponse({'redirect': f'{url}orders/search?email={order.email}'})
            else:
                return JsonResponse({'error': 'Оплата еще не дошла до нас, попробуйте еще раз.'})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'error not order'})


@csrf_exempt
def new_order(request: HttpRequest):
    if request.POST:
        form = OrderForm(user = request.user, request=request, data=request.POST)
        if form.is_valid():
            order: Order = form.save()
            return JsonResponse({'success': True, 'order_id': order.order_id})
        else:
            return JsonResponse({'errors': form.errors})
    
    return JsonResponse({'success': False, 'error_message': 'Неверный запрос'})


@login_required(login_url='account_login')
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, client=request.user)
        pay_p = []
        for provider, name in ProviderPay.PROVIDERS:
            img = next((img for p, img in ProviderPay.IMG if p == provider), None)
            pay_p.append({
                'provider': provider,
                'name': name,
                'img': img
            })
        return render(request=request, template_name='my_site/confirm_order.html', context={'order': order, 
                                                                                            'pay_p': pay_p})
    except Order.DoesNotExist:
        return redirect('index')


def order_pay(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': "Server error"}, status=400)
        form = PayProfileForm(data=data)
        if form.is_valid():
            try:
                order = Order.objects.get(order_id=data.get('order_id'))
            except Order.DoesNotExist:
                return JsonResponse({'error': "Server error"}, status=400)
            if order.status != order.NO_PAY:
                return JsonResponse({'error', 'Этот заказ уже оплачен!'})
                
            pm.create_pay(pay_provider=form.cleaned_data.get('pay_provider'), order=order)
            if order.transaction and order.transaction.pay_provider == ProviderPay.PRF:
                try:
                    order.transaction.pay_from_balance()
                    
                    return JsonResponse({'redirect': order.transaction.pay_url})

                except BalanceException as e:
                    return JsonResponse({'error': str(e)}, status=400)

            if order.transaction and order.transaction.pay_url:
                return JsonResponse({'redirect': order.transaction.pay_url})
            return JsonResponse({'redirect': redirect})
        else:
            errors = []
            for field in form.errors:
                for error in form.errors[field]:
                    print(field, ': ', error)
                    errors.append(error)
            return JsonResponse({'error': errors})
    else:
        return JsonResponse({'error': "Server error"}, status=400)


@api_view(['GET'])
def get_promocode(request, promocode):
    try:
        code = PromoCode.objects.get(code=promocode)
        if not code.is_active():
            return Response({'error': 'Промокод не найден'})
        serializer = PromoCodeSerializer(code)
        return Response(serializer.data)
    except PromoCode.DoesNotExist:
        return Response({'error': 'Промокод не найден'})
        

@api_view(['GET'])
def subcategories_with_services(request, category_slug):
    # Получаем сервисы, связанные с категорией
    services_qs = Service.objects.filter(category__slug=category_slug, is_published=True)

    # Получаем подкатегории с предварительной загрузкой сервисов
    subcategories = Subcategory.objects.prefetch_related(
        Prefetch('services', queryset=services_qs)
    ).filter(categories__slug=category_slug)

    # Сериализуем данные
    serializer = SubcategorySerializer(subcategories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_tariffs(request, cat_slug, sub_slug):
    tariffs = Service.objects.filter(category__slug=cat_slug, sub_cat__slug=sub_slug, is_published=True)
    
    serializer = ServiceSerializer(tariffs, many=True)
    return Response(serializer.data)
    

def AJAX_order_cancel(request):
    if request.method == 'POST' and is_ajax(request=request):
        order_id = request.POST.get('order_id')
        print(f'Запрос отмены заказа: {order_id}')
        order = Order.objects.get(order_id=order_id)
        cancel_order.delay(order_id)
        order.set_status(Order.WAITCANCEL, True)
        return JsonResponse({'status': order.status})


@csrf_exempt
def pay_test(request):
    if request.method == 'POST' and is_ajax(request):
        try:
            order_id = request.POST.get('order_id')
            order = Order.objects.get(order_id=order_id)
            if order.transaction and order.transaction.pay_provider == ProviderPay.PRF:
                try:
                    order.transaction.pay_from_balance()
                    return JsonResponse({'redirect': order.transaction.pay_url, 'pay': order.transaction.pay_provider})

                except BalanceException as e:
                    return JsonResponse({'error': str(e), 'pay': order.transaction.pay_provider})

            if order.transaction and order.transaction.pay_url:
                return JsonResponse({'redirect': order.transaction.pay_url, 'pay': order.transaction.pay_provider})

            return JsonResponse({'redirect': '/'})

        except Order.DoesNotExist:
            return JsonResponse({'redirect': '/'})
    else:
        return JsonResponse({'redirect': '/'})


def add_comment(request, order_id: int):
    if request.user.is_authenticated:
        try:
            form = CommentForm()
            order = Order.objects.get(order_id=order_id)
            # Проверка есть отзыв на данный заказ
            if not hasattr(order, 'review'):
                if request.method == 'POST':
                    form = CommentForm(request.POST)
                    if form.is_valid():
                        form.save(user=request.user, order=order)
                        return redirect('orders')
                    
                context = {'form': form,
                            'order': order,
                            'order_id': order_id,
                            'base_url': settings.BASE_URL}
                return render(request=request, template_name='my_site/comment.html', context=context)
        except (Order.DoesNotExist):
                pass
        
    return redirect('orders')
    

def oferta(request: HttpRequest):
    return render(request=request, template_name='my_site/oferta.html')

def policy(request: HttpRequest):
    return render(request=request, template_name='my_site/policy.html')