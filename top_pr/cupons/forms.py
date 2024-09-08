from django import forms
from .models import Cupon, Client
from .exceptions import CuponException


class CuponForm(forms.Form):
    cupon = forms.fields.CharField(max_length=7, widget=forms.widgets.TextInput(attrs={'class': 'form-control',
                                                                                       'placeholder': 'Купон',
                                                                                       'aria-describedby': 'error'}))

    def __init__(self, user: Client = None, *args, **kwargs) -> None:
        super(CuponForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean_cupon(self):
        cupon = self.cleaned_data['cupon']
        try:
            cupon: Cupon = Cupon.objects.get(code=cupon)
            cupon.checking(self.user)

        except Cupon.DoesNotExist:
            raise forms.ValidationError('Купон не найден')
        except CuponException as e:
            raise forms.ValidationError(e)

        return cupon