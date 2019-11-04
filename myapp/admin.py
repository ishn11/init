from django.contrib import admin

# Register your models here.
from .models import Item, OrderItem, Order ,Contact , Free,Payment,Coupon,Address

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'billing_address',
                    'shipping_address',
                    'payment',
                    'coupon'
                    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']

    

    list_display_links = [
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    #actions = [make_refund_accepted]
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order , OrderAdmin)
admin.site.register(Contact)
admin.site.register(Free)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Address, AddressAdmin)