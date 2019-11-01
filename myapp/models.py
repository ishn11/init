from django.db import models
  
from django.conf import settings
from django.core.validators import RegexValidator
from django_countries.fields import CountryField
from django.shortcuts import reverse



CATEGORY_CHOICES = (
    ('CC', 'Carpet Cleaning (Houses)'),
    ('CCT', 'Carpet Cleaning (Townhouses Includes 15 Stairs)'),
    ('CCU', 'Carpet Cleaning (Units & Apartments)'),
    ('CCO', 'Carpet Cleaning (Offices/Commercial)'),
    ('MC', 'Mattress Cleaning'),
    ('SC', 'Sofa Cleaning'),
    ('RC', 'Rug Cleaning (On-site At Your Premises)'),
    ('AA', 'Anti Allergen Treatment'),


)
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

class Contact(models.Model):
    name = models.CharField('Name', max_length=120)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(max_length=70,blank=True)
    location = models.CharField('Location', max_length=120)
    description = models.TextField(blank=True)
class Free(models.Model):
    name = models.CharField('Name', max_length=120)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(max_length=70,blank=True)
    
    description = models.TextField(blank=True)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    slug = models.SlugField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    discount_price = models.FloatField(blank=True, null=True)
    
    

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('product', kwargs={
            'slug': self.slug
        })
    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={
            'slug': self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse('remove-from-cart', kwargs={
            'slug': self.slug
        })
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,blank=True,null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.category}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()




class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username