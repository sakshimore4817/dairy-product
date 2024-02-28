from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render,redirect,HttpResponseRedirect
from django.http import HttpResponse
from django.views import View 
import razorpay
from .models import Product ,Cart,Payment,Customer,OrderPlaced,Wishlist
from . forms import CustomerRegistrationForm,CustomerProfileForm,Customer
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.db.models import Q 
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import AnonymousUser


# Create your views here.

def home(request):
    if request.user.is_authenticated:
        totalitem = 0
        wishlist_count = 0
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request,'app/home.html',locals())
    else:
        return HttpResponseRedirect('login/')

def about(request):
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/about.html',locals())



def contact(request):
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/contact.html',locals())

class CategoryView(View):
    def get(self,request,val):
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,'app/category.html',locals())

class CategoryTitle(View):
    def get(self,request,val):
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request,'app/category.html',locals())


class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request,'app/productdetail.html',locals())

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request, 'app/customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Congralution! User Register Successfully')
        else:
            messages.warning(request,'Invalid Input Data')
        return render(request, 'app/customerregistration.html',locals())

class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request,'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congralutions! Profile save Successfully')
        else:
            messages.warning(request,'Invalid Input Data')
        return render(request,'app/profile.html',locals())

def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishlist_count=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/address.html',locals())


class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,'Congratulations! profile update successfully')
        else:
            messages.warning(request,'Invalid Input Data')
        return redirect('address')

def Logout(request):
    return HttpResponseRedirect('/login/')

def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart/')


def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    totalitem = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/addtocart.html',locals())

def plus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) &   Q(user=request.user) )
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount

        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) &   Q(user=request.user) )
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount

        }
        return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) &   Q(user=request.user) )
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'amount':amount,
            'totalamount':totalamount

        }
        return JsonResponse(data)

class CheckoutView(View):
    def get(self, request):
        totalitem = 0
        wishlist_count = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        razorpayamount = int(totalamount*100)
        print(totalamount)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
        data = {"amount":razorpayamount,"currency":"INR","receipt":"order_rcptid_12"}
        payment_response=client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status = order_status,
            )
            payment.save()
        
        return render(request, 'app/checkout.html', locals())

       
def payment_done(request):
    order_id=request.GET.get('order_id')
    payment_id=request.GET.get('payment_id')
    cust_id=request.GET.get('cust_id')
    user=request.user
    customer=Customer.objects.get(id=cust_id)
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid=True
    payment.razorpay_payment_id=payment_id
    payment.save()
    cart=Cart.objects.filter(user=user)
    for c in cart:  
        OrderPlaced.objects.create(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()
        
    return redirect('orders')


def order_confirmation(request):
    cart_items=Cart.objects.filter(user=request.user)
    famount = 0
    for p in cart_items:
        value = p.quantity * p.product.discounted_price
        famount = famount + value
    totalamount = famount + 40
    razorpayamount = int(totalamount * 100)
    client = razorpay.Client(auth=("rzp_test_9BZyJ3buu1pncT", "6QKQl4eZL8qSwxmeZy02o4tv"))
    data = { "amount": razorpayamount, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    context={
        'amt': razorpayamount,'user':request.user
    }

    return render(request,'app/pay.html',context)

@csrf_exempt
def orders(request):
    totalitem = 0
    wishlist_count = 0
    order_placed = []
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user_id=request.user).count()
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        order_placed=OrderPlaced.objects.filter(user=request.user)
        user = request.user
    context={
        'totalitem':totalitem,
        'wishlist_count':wishlist_count,
        'order_placed':order_placed
    }
    return render(request,'app/orders.html',context)


def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        if not Wishlist.objects.filter(user=user, product=product).exists():
            Wishlist(user=user, product=product).save()

        data = {'message': 'Wishlist Added Successfully'}
        return JsonResponse(data)

def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user, product=product).delete()

        data = {'message': 'Wishlist Removed Successfully'}
        return JsonResponse(data)

        

def search(request):
    query=request.GET['search']
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request,'app/search.html',locals())