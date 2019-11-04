from django import forms
from .models import Contact,Free
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.forms import ModelForm, Textarea,TextInput

	
class ContactForm(forms.ModelForm):
    
	

	class Meta:
		model = Contact
		fields = (
			'name',
			'phone_number',
            'email',
            'location',
            'description',
            
		) 
		widgets = {
            'name': Textarea(attrs={'cols': 29, 'rows': 1,'placeholder': 'Please Enter Your Name:', 'id': 'name'}),
            'phone_number': Textarea(attrs={'cols': 29, 'rows': 1,'placeholder': 'Please Enter Your Email Id:', 'id': 'phone_number'}),
            'email': Textarea(attrs={'cols': 29, 'rows': 1,'placeholder': 'Please Enter Your Phone No:', 'id': 'email'}),
            'location' : Textarea(attrs={'cols': 29, 'rows': 1,'placeholder': 'Suburb/Location:', 'id': 'location'}),
            'description': Textarea(attrs={'cols': 31, 'rows': 9,'placeholder': 'Your message', 'id': 'name'}),
        }
class FreeForm(forms.ModelForm):
    
	

	class Meta:
		model = Free
		fields = (
			'name',
			'phone_number',
            'email',
            'description',
            
		) 
		widgets = {
            'name': TextInput(attrs={'placeholder': 'Name *', 'id': 'name'}),
            'phone_number': TextInput(attrs={'placeholder': 'Phone *', 'id': 'name'}),
            'email': TextInput(attrs={'placeholder': 'Email Id: *', 'id': 'name'}),
            'description': Textarea(attrs={'cols': 49, 'rows': 9,'placeholder': 'Details Here *', 'id': 'name'}),
        }




PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'id': 'address'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite',
        'id': 'address-2'
    }))
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',

        }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'zip'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))
