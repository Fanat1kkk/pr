from typing import Any
from django import forms
from django.http import HttpRequest
from allauth.account.forms import LoginForm, SignupForm, ResetPasswordForm, ResetPasswordKeyForm
from payments.models import ProviderPay
from payments.providers import pm
from .models import Order, Client, CustomerReview, Service



class ConfirmOrderForm(forms.Form):

    def __init__(self, order: Order, *args, **kwargs) -> None:
        super(ConfirmOrderForm, self).__init__(*args, **kwargs)
        self.fields.update({'order_id': forms.CharField(max_length=5, widget=forms.HiddenInput(attrs={'value': order.order_id}))})


class MyResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
                "type": "email",
                "placeholder": "Емаил адрес",
                "autocomplete": "email",
                "class": 'form-control'
        })


class MyResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control mb-3',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control mb-3',
        })


class MySignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
                                        "type": "email",
                                        "placeholder": "E-mail адрес",
                                        "autocomplete": "email",
                                        "class": 'form-control mb-3',
                                        'id': 'mail'
                                    })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control mb-3',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control mb-3',
        })


class MyLogInForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
                                        "type": "email",
                                        "placeholder": "E-mail адрес",
                                        "autocomplete": "email",
                                        "class": 'form-control mb-3',
                                        # 'aria-describedby': 'login_error',
                                    })

        self.fields['password'].widget.attrs.update({
            'class': 'form-control mb-3',
            # 'aria-describedby': 'password_error',
        })


class CommentForm(forms.ModelForm):
    rating_speed = forms.ChoiceField(choices=CustomerReview.CHOISES_RATING,
                                     widget=forms.Select({'class': 'form-select select-elements'}),
                                     label='Оцените скорость накрутки')
    rating_acc = forms.ChoiceField(choices=CustomerReview.CHOISES_RATING,
                                     widget=forms.Select({'class': 'form-select select-elements'}),
                                     label='Оцените качество аккаунтов')
    
    def save(self, user, order, commit: bool = True) -> Any:
        super().save(commit=False)
        self.instance.client = user
        self.instance.order = order
        self.instance.service = order.service
        
        if commit:
            self.instance.save()
        
        return self.instance
        
          
    class Meta:
        model = CustomerReview
        fields = ('rating_speed', 'rating_acc', 'comment',)
        widgets = {
            'comment': forms.Textarea(attrs={"cols": "20", "rows": "10"})
        }
        labels = {
            'comment': 'Оставте свой отзыв'
        }
    
     
class OrderForm(forms.ModelForm):
    service = forms.IntegerField(required=True)
    email = forms.EmailField(required=True)
    # promocode = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ('service', 'count', 'task_url', 'email', 'promocode')
        error_messages = {'promocode':{
            'invalid_choice': 'Код не действительный',
            'invalid_list': 'Код не действительный'
        }}

    def clean_service(self):
        service_id = self.cleaned_data.get('service', None)
        if service_id:
            try:
                service = Service.objects.get(service_id=service_id)
            except Service.DoesNotExist:
                raise forms.ValidationError('Услуга не найдена')
            return service
        else:
            raise forms.ValidationError('Не может быть пустым')
        

    def clean_count(self):
        count = self.cleaned_data['count']
        service = self.cleaned_data['service']

        if count < service.min_count:
            raise forms.ValidationError(f'Количество не может быть меньше {service.min_count}')
        elif count > service.max_count:
            raise forms.ValidationError(f'Количество не может быть больше {service.max_count}')

        return count


    def clean_promocode(self):
        promocode = self.cleaned_data.get('promocode', None)
        
        if promocode and not promocode.is_active(self.user):
            raise forms.ValidationError('Код не действительный')
        
        return promocode

    def save(self, commit=True, *args, **kwargs):
        order = super(OrderForm, self).save(commit=False, *args, **kwargs)
        
        email = self.cleaned_data['email']
        promocode = self.cleaned_data['promocode']

        client = Client.objects.get_or_creat_user_from_email(email=email, request=self.request)
        order.client = client
        if promocode:
            order.promocode = promocode 
            promocode.activate(order)
        order.order_id = order.gen_order_id()
        order.calc_price(save=False)
        
        order.save()

        return order

    def __init__(self, request: HttpRequest, user: Client = None, *args, **kwargs) -> None:
        super(OrderForm, self).__init__(*args, **kwargs)
        self.user = user
        self.request = request


class PayProfileForm(forms.Form):
    sum = forms.DecimalField(required=True ,widget=forms.widgets.NumberInput(attrs={'class': 'form-control',
                                                                                    'placeholder': '100'}))
    
    pay_provider = forms.ChoiceField(choices=ProviderPay.PROVIDERS, required=True,
                                     widget=forms.Select({'class': 'form-select select-elements',}))

    
    def clean_sum(self):
        sum = self.cleaned_data.get('sum')
        if sum <= 0 :
            raise forms.ValidationError('Сумма должна быть больше нуля!')

        return str(sum)
    