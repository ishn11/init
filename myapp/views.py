from django.shortcuts import render

from django.views.generic import View
from django.http import HttpResponse 
from django.views.generic.base import TemplateView
from .forms import ContactForm,FreeForm
from django.shortcuts import render , redirect, get_object_or_404
from django.contrib import messages

from django.views.generic import ListView, DetailView

from django.utils import timezone
from .models import Item, OrderItem,  Order,Payment,BillingAddress
from .forms import CheckoutForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
stripe.api_key = "	sk_test_NjwX7NOFXmGub8K3Pl88BuBn0066ujKEvY"
def contac(request):
    form_class = ContactForm
    
    return render(request, 'myapp/index.html', {
        'form': form_class,
    })


def about(request):
    return render(request, 'myapp/about.html', {'title': 'About'})



def contact(request): 
  
        if request.method =='POST':   
            form = ContactForm(request.POST)
            # Pass the form data to the form class 
             
            
            # In the 'form' class the clean function  
            # is defined, if all the data is correct  
            # as per the clean function, it returns true 
            if form.is_valid():
                supply = form.save(commit = False) # Temporarily make an object to be add some 
                supply.name = request.user
                supply.save()# logic into the data if there is such a need  
                return redirect("contact")
            return render(request, 'myapp/index.html', {'form':form})
        else:
            form = ContactForm()     
            return render(request, 'myapp/index.html', {'form':form})

class AddCommentView(TemplateView):

    post_form_class = ContactForm
    comment_form_class = FreeForm
    template_name = 'myapp/index.html'

    def post(self, request):
        post_data = request.POST or None
        post_form = self.post_form_class(post_data, prefix='post')
        comment_form = self.comment_form_class(post_data, prefix='comment')

        context = self.get_context_data(post_form=post_form,
                                        comment_form=comment_form)

        if post_form.is_valid():
            self.form_save(post_form)
        if comment_form.is_valid():
            self.form_save(comment_form)

        return self.render_to_response(context)     

    def form_save(self, form):
        obj = form.save()
        messages.success(self.request, "Thank You . Your request was successfully submitted ")
        return obj

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
class HomeView(ListView):
    model = Item
    template_name = "myapp/cleanto/index.html"

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'myapp/cleanto/order_summary.html',context)
            
            
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")
        
        

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect('product', slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect('product', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect('product', slug=slug)

   
        

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect('product', slug=slug)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('product', slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect('product', slug=slug)

class PaymentView(View):
    def get(self, *args, **kwargs):
        
        return render(self.request, "myapp/cleanto/payment.html")
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.error(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")

        

        order.ordered = True

    
class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request,"myapp/cleanto/inde.html", context)
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO: add redirect to the selected payment option
                return redirect('checkout')
            messages.warning(self.request, "Failed checkout")
            return redirect('checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")

class ItemDetailView(DetailView):
    model = Item
    template_name = "myapp/cleanto/product.html"

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect('order-summary')
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('product', slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect( 'product', slug=slug)