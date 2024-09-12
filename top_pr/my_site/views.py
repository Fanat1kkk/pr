from decimal import Decimal
from django.shortcuts import render, redirect
from django.conf import settings 
from django.http import HttpResponse, JsonResponse, Http404
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from allauth.account.views import LoginView, SignupView, PasswordResetFromKeyView

from payments.models import ProviderPay
from payments.providers import pm
from cupons.forms import CuponForm

from .models import Category, Order, Service, CustomerReview
from .forms import OrderForm, ConfirmOrderForm, MyLogInForm, MySignupForm, PayProfileForm, MyResetPasswordKeyForm, CommentForm
from .utils import del_zero
from .exceptions import BalanceException
from .tasks import cancel_order


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
            return JsonResponse({'location': response.url})
        else:
            return JsonResponse({'errors': form.errors, 'errors_non_fields': form.non_field_errors()})


# class MyPasswordResetView(FormsMixin, PasswordResetView):
#     template_name: str = 'my_site/account/password_reset.html'
    
    
class PasswordResetDoneView(FormsMixin, TemplateView):
    template_name = "my_site/account/password_reset_done.html"


class MyPasswordResetFromKeyView(FormsMixin, PasswordResetFromKeyView):
    template_name: str = "my_site/account/password_reset_from_key.html"
    form_class = MyResetPasswordKeyForm


class MyPasswordResetFromKeyDoneView(FormsMixin, TemplateView):
    template_name = "my_site/account/password_reset_from_key_done.html"


def index(request):
    categories = Category.objects.all()
    form = OrderForm(user=request.user)
    form_login = MyLogInForm()
    form_signup = MySignupForm()
    context = {
        'categories': categories,
        'form': form,
        'form_login': form_login,
        'form_signup': form_signup,
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


def profile(request):
    form_login = MyLogInForm()
    form_signup = MySignupForm()
    context = {
        'form_login': form_login,
        'form_signup': form_signup,
        'base_url': settings.BASE_URL,
    }
    if request.method == 'GET':
        cupon_form = CuponForm()
        pay_form = PayProfileForm()
        context.update({
            'cupon_form': cupon_form,
            'pay_form': pay_form,
        })
        
    elif request.method == 'POST':
        cupon_form = CuponForm(user = request.user, data=request.POST)
        pay_form = PayProfileForm()
        context.update({
            'cupon_form': cupon_form,
            'pay_form': pay_form,
        })

        if cupon_form.is_valid():
            cupon = cupon_form.cleaned_data['cupon']
            cupon.use(request.user)
            context.update({
                'cupon': cupon
            })
        else:
            errors = []
            for field in cupon_form.errors:
                for error in cupon_form.errors[field]:
                    errors.append(error)
            
            context.update({
            'cupon_errors': errors
            })
        
    return render(request=request, template_name='my_site/profile/profile.html', context=context)


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
            print(order.order_id)
            print(order.is_paid)
            if order.is_paid:
                url = settings.BASE_URL
                return JsonResponse({'redirect': f'{url}orders/search?email={order.email}'})
            else:
                return JsonResponse({'error': 'Оплата еще не дошла до нас, попробуйте еще раз.'})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'error not order'})


@csrf_exempt
def AJAX_calculate(request):
    if request.method == 'POST':

        form = OrderForm(user = request.user, data=request.POST)

        form.is_valid()

        service_error = form.errors.get('service', None)
        count_error = form.errors.get('count', None)
        promocode_error = form.errors.get('promocode', None)
        
        price = Decimal('0')
        count = 0
        errors = {}
        service_info = {}

        if count_error:
            errors.update({'count': count_error})
        else:
            count = Decimal(str(form.cleaned_data['count']))

        if service_error:
            errors.update({'service': service_error})
        else:
            service = form.cleaned_data['service']
            service_info.update({'speed': service.speed, 
                                 'quality': service.quality, 
                                 'text': service.text_info,
                                 'is_cancellation': service.is_cancellation})

            if count != 0:
                price = service.price_per_one() * count
                
        if promocode_error:
            errors.update({'promocode': promocode_error})
        else:
            if count != 0:
                promocode = form.cleaned_data.get('promocode', None)
                if promocode:
                    price = promocode.calc(price=price)

        return JsonResponse({'price': del_zero(price), 'errors': errors, 'service_info': service_info})

    return Http404(request)


def AJAX_order(request):
    if request.POST:
        form = OrderForm(user = request.user, data=request.POST)
        if form.is_valid():
            order: Order = form.save()
            order_form = ConfirmOrderForm(order=order)
            return JsonResponse({'ok': {'form': render_to_string('my_site/confirm_order.html', {'order': order,
                                                                                                'order_form': order_form}, request=request),
                                        'order': order.to_dict()}})
        else:
            return JsonResponse({'errors': form.errors})
    else:
        return Http404('Page not found')


def AJAX_get_services(request, cat_id, sub_id):
    if is_ajax(request):
        services = Service.objects.filter(sub_cat=sub_id, category=cat_id, is_published=True)
        
        data = dict()
        data_s = dict()
        for service in services:
            data_s.update({service.pk: {
                'name': service.name,
                'price': '%.2f' % service.price_per_one()
            }})

        service = services[0]
        data.update({'data_s': data_s})
        data.update({'service_info': {'speed': service.speed, 
                                      'quality': service.quality, 
                                      'text': service.text_info,
                                      'is_cancellation': service.is_cancellation}
                    })

        return JsonResponse(data=data)
    Http404('Page not found')


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
    
    
#https://pay.freekassa.ru/?m=18167&oa=100&currency=RUB&o=123&s=aa8d8d8cf24ff4713ab4dde2890b85e7