from django.shortcuts import render,HttpResponse, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from ecommapp.models import Product,Cart,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail

# Create your views here.
def about(request):
    #return HttpResponse("Hello From views.py File")

    #x='Hello From views.py File'
    #return HttpResponse(x)

    return render(request, 'about.html')

def contact(request):
    return render(request,'contact.html')

def delete(request,rid):
    return HttpResponse("ID to be deleted")

def edit(request,eid):
    return HttpResponse("Record Edited")

class ContactForm(View):
    def get(self, request,cid):
        return HttpResponse("Class Based View...!!"+cid)

def hello(request):
    context = {}
    context['x'] = 100
    context['y'] = 50
    context['z'] = 200
    context['l'] = [10,20,30,40]
    context['product'] = [{'id':1,'image':'pimage','pname':'samsung','pcat':'mobile','price':25000},{'id':2,'image':'pimage2','pname':'jeans','pcat':'cloth','price':1700}]
    return render(request,'hello.html',context)

def message(request):
    return render(request,'message.html')

def base(request):
    return render(request, 'base.html')

def products(request):
    uid = request.user.id
    #print("Loggedin User ",uid)
    p=Product.objects.filter(is_active=True)
    #print(p)
    context={}
    context['data']=p
    return render(request,'index.html',context)

def register(request):
    context={}
    if request.method=="GET":
        return render(request,'register.html')
    else:
        n = request.POST['uname']
        p = request.POST['upass']
        cp = request.POST['ucpass']
        '''
        print(n)
        print(p)
        print(cp)
        '''

        if n=='' or p=='' or cp=='':
            context['errmsg']="Fields Cannot be blank"
            return render(request,'register.html',context)

        elif p!=cp:
            context['errmsg']="Password & Confirm Password didn't match"
            return render(request,'register.html',context)

        elif len(p)<8 and len(p)>15:
            context['errmsg']="Password must be minimum 8 & Maximum 15 characters"
            return render(request,'register.html',context)

        else:
            try:
                u=User.objects.create(username=n)
                u.set_password(p)
                u.save()
                context['success']="User Created Successfully..!!"
                return render(request,'login.html',context)
            except Exception:
                context['errmsg']="User Already exist. Please Login"
                return render(request,'register.html',context)

def user_login(request):
    if request.method=="GET":
        return render(request, 'login.html')
    else:
        n=request.POST['uname']
        p=request.POST['upass']
        #print(n)
        u=authenticate(username=n, password=p)
        #print(u)

        if u is not None:
            login(request,u)
            return redirect('/products')
        
        else:
            context={}
            context['errmsg']="Invalid username or password."
            return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    #return redirect('/login')
    return redirect('/product')

def catfilter(request,cv):
    #print(cv)
    q1 = Q(cat = cv)
    q2 = Q(is_active = True)

    p=Product.objects.filter(q1 & q2)
    context={}
    context['data']=p
    return render(request,'index.html', context)

def sort(request,sv):
    #print("Data Type of SV is : ",type(sv))
    if sv=='1':
        p=Product.objects.order_by('-price').filter(is_active=True)

    else:
        p=Product.objects.order_by('price').filter(is_active=True)
        
    context={}
    context['data']=p
    return render(request, 'index.html', context)

def filterbyprice(request):
    min = request.GET['min']
    max = request.GET['max']

    q1 = Q(price__gte=min) 
    q2 = Q(price__lte=max)

    p=Product.objects.filter(q1 & q2)
    context={}
    context['data']=p
    return render(request, 'index.html', context)

def product_details(request,pid):
    p = Product.objects.filter(id=pid)
    context={}
    context['data']=p
    return render(request,'product_details.html',context)

def cart(request,pid):
    if request.user.is_authenticated:
        u = User.objects.filter(id=request.user.id)
        p = Product.objects.filter(id=pid)
        #print(u[0])
        #uid = request.user.id
        #print('user id : ',uid)
        q1 = Q(userid=u[0])
        q2 = Q(pid=p[0])
        c = Cart.objects.filter(q1 & q2)
        n = len(c)
        context = {}
        context['data'] = p
        
        if n==1:
            context['msg'] = "Product already exist in cart"

        else:
            c = Cart.objects.create(userid=u[0],pid=p[0])
            c.save()
            context['msg'] = "Product Added Successfully in Cart..!!"
            #return HttpResponse("Product addes in Cart...!!")
        return render(request,'product_details.html',context)

    else:
        return redirect('/login')
    

def viewcart(request):
    c = Cart.objects.filter(userid=request.user.id)
    #print(c)
    #print(c[0].userid)
    #print(c[0].userid.is_staff)
    sum = 0
    for x in c:
        sum = sum + x.pid.price*x.qty
    context = {}
    context['data'] = c
    context['total'] = sum
    context['len'] = len(c)
    return render(request,'cart.html',context)

def updateqty(request,x,cid):
    c = Cart.objects.filter(id=cid)
    q = c[0].qty

    if x=='1':
        q = q+1
    elif q>1:
        q = q-1
        
    c.update(qty=q)
    return redirect('/viewcart')

def removecart(request,cid):
    c = Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def placeorder(request):
    c = Cart.objects.filter(userid = request.user.id)
    orderid = random.randrange(1000,9999)
    for x in c:
        amount = x.qty*x.pid.price
        o = Order.objects.create(orderid=orderid,qty=x.qty,pid=x.pid,userid=x.userid,amt=amount)
        o.save()
        x.delete()
    #return render(request,'placeorder.html')
    return redirect('/fetchorder')


def fetchorder(request):
    orders = Order.objects.filter(userid=request.user.id)
    #return HttpResponse("Order are Fetch..!!")

    sum = 0
    for x in orders:
        sum = sum + x.amt
    context = {}
    context['data'] = orders
    context['total'] = sum
    context['n'] = len(orders)
    return render(request,'placeorder.html',context)


def makepayment(request):
    client = razorpay.Client(auth=("rzp_test_zBcyxmDYBUMjh0", "ctXEm7HTmXbqnt3IFUF899lV"))

    order = Order.objects.filter(userid=request.user.id)
    sum = 0
    for x in order:
        sum = sum + x.amt
        oid = x.orderid
    
    data = { "amount": sum*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    print(payment)
    context = {}
    context['payment'] = payment
    #return HttpResponse("Success")
    return render(request,'pay.html',context)

def paymentsuccess(request):
    sub = 'Ekart-Order Status'
    msg = 'Thanks For Shopping'
    frm = 'sakshijuwar81120@gmail.com'
    u = User.objects.filter(id=request.user.id)
    to = u[0].email

    send_mail(
        sub,
        msg,
        frm,
        [to],
        fail_silently = False
    )

    return render(request,'paymentsuccess.html')


def search(request):
    context = {}
    query = request.GET['query']
    #print(query)
    pname = Product.objects.filter(name__icontains=query)
    pdetail = Product.objects.filter(pdetails__icontains=query)
    pcat = Product.objects.filter(cat__icontains=query)
    allproducts = pname.union(pdetail,pcat)

    if allproducts.count()==0:
        context['errmsg'] = 'Product Not Found...'
    
    context['data'] = allproducts
    return render(request,'index.html',context)

    '''
    <div style="text-align: leftt; width: 5cm;">
        <form class="d-flex">
            <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search">
            <button class="btn btn-outline-success" type="submit">Search</button>
        </form>
    </div>
    '''

def samiksha(request):
    return render(request,'samiksha.html')