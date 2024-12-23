from django.shortcuts import render , redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import logout
from .models import references , shoe_model , staff  , clients , orders , producement, ReferenceType, StatusType , staff_payments
from django.http.response import HttpResponse
from .forms import shoe_model_forms , staff_forms , clients_forms , orders_forms ,producement_forms
# Create your views here.
import json

def logout_view(request):
    logout(request)
    messages.success(request, "Siz ro'yxatdan chiqib ketdiz")
    return redirect('/login/')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Siz ro'yxatdan o'tdingiz!")
            return redirect('/')
        else:
            messages.error(request, "Parol yoki Ism noto'g'ri.")
    else:
        form = AuthenticationForm()
        form.fields['username'].label = "Ism"
        form.fields['password'].label = "Parol"
    return render(request, 'login.html', {'form': form})

def home(request):
    shoe_models = shoe_model.objects.all()
    finished_producements = producement.objects.filter(status__value='Bajarildi')
    quantity_producements = dict()
    for item in finished_producements:
        if item.shoe_model_id.name not in quantity_producements:
            quantity_producements[item.shoe_model_id.name] = {"quantity":[item.quantity]}
        else:
            quantity_producements[item.shoe_model_id.name]["quantity"].append(item.quantity)
        
        quantity_producements[item.shoe_model_id.name]["total"] = sum(quantity_producements[item.shoe_model_id.name]["quantity"])

  
        
    quantity_producements_json = json.dumps(quantity_producements)
    context ={
        "shoe_models":shoe_models,
        "quantity_producements":quantity_producements_json,
    }
    
    return render(request , "index.html" , context=context)

# reference
def reference_view(request):
    if request.method == "POST":
        type = request.POST.get("type")
        value = request.POST.get("value")
        if type == "--------":
            pass
        else:
            if references.objects.filter(type=int(type), value=value).exists() and not references.objects.filter(type=int(type), value=value ,IsDeleted=True):
                pass
            else:
                if ReferenceType(int(type)) in ReferenceType:
                    print(True)
                new_entry = references(type=int(type) , value=value)
                new_entry.save()
            
            
    reference_models = references.objects.all()

    
    context = {
        "reference": reference_models,
    }
    return render(request , "references.html", context=context)

def update_reference(request, pk):
    if request.method == "POST":
        new_value = request.POST.get("value")  # Get the updated value from the form
        try:
            reference_item = references.objects.get(id=pk)
            reference_item.value = new_value  # Update the value
            reference_item.save()  # Save the changes
            return redirect("reference")  # Redirect to the reference list page after update
        except references.DoesNotExist:
            return HttpResponse("Item not found", status=404)

def delete_reference(request, pk):
    try:
        reference_item = references.objects.get(id=pk)
        reference_item.IsDeleted = True
        reference_item.save()
        return redirect("reference")
    except references.DoesNotExist:
        return HttpResponse("Item not found", status=404)

# shoemodel
def shoe_model_create(request):
    if request.method == "POST":
        forms = shoe_model_forms(request.POST , request.FILES)
        if forms.is_valid():
            forms.save()
            return redirect('home')
    else: 
        forms = shoe_model_forms()
    context = {
        "forms":forms
    }
    return render(request , "shoe_model/shoe_model_create.html" , context=context)

def shoe_model_read(request , pk):
    shoe_model_item = shoe_model.objects.get(pk=pk)
    producement_list = producement.objects.filter(status__value="Bajarildi", shoe_model_id=shoe_model_item)
    
    context = {
        "producement_list":producement_list,
        "shoe_model_item":shoe_model_item
    }
    return render(request , 'shoe_model/shoe_model_read.html' , context=context)  

def shoe_model_update(request, pk):
    shoe_model_item = shoe_model.objects.get(pk=pk)
    
    if request.method == "POST":
        forms = shoe_model_forms(request.POST , request.FILES , instance=shoe_model_item)
        if forms.is_valid():
            forms.save()
            return redirect('home')

    forms = shoe_model_forms(instance=shoe_model_item)
    context = {
        "forms":forms
    }
    return render(request , 'shoe_model/shoe_model_update.html', context=context)

def shoe_model_delete(request, pk):
    shoe_model_item = shoe_model.objects.get(pk=pk)
    shoe_model_item.delete()
    return redirect('home')

# staff
def staff_view(request):
    staff_list = staff.objects.all()
    context = {
        "staff_list":staff_list,
    }
    return render(request , "staff/staff.html" , context=context)

def staff_read(request, pk):
    staff_item = staff.objects.get(pk=pk)
    payment_list = staff_payments.objects.all()
    context = {
        "staff":staff_item,
        "payment_list":payment_list
    }
    return render(request, "staff/staff_read.html", context=context)


def staff_create(request):
    forms = staff_forms()
    if request.method == "POST":
        forms = staff_forms(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect('staff_view')
        else:
            forms = forms.errors()
            print(forms)
    
    context = {
        "forms":forms
    }
    
    return render(request , "staff/staff_create.html" , context=context)

def staff_update(request, pk):
    staff_item = staff.objects.get(pk=pk)
    
    if request.method == "POST":
        forms = staff_forms(request.POST , instance=staff_item)
        if forms.is_valid():
            forms.save()
            return redirect('staff_view')
    
    forms = staff_forms(instance=staff_item)
    context = {
        "forms":forms
    }
    return render(request , "staff/staff_update.html" , context=context)

def staff_delete(request, pk):
    staff_item = staff.objects.get(pk=pk)
    staff_item.delete()
    return redirect("staff_view")
# clients

def clients_view(request):
    clients_list = clients.objects.all()
    context = {
        "clients_list":clients_list
    }
    return render(request , "clients/clients.html" , context=context)

def clients_create(request):
    if request.method == "POST":
        forms = clients_forms(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect('clients_view')
    
    forms = clients_forms()
    
    context ={
        "forms":forms
    }
    
    return render(request , "clients/clients_create.html" , context=context)

def clients_update(request, pk):
    client_item = clients.objects.get(pk=pk)
    
    if request.method == "POST":
        forms = clients_forms(request.POST , instance=client_item)
        if forms.is_valid():
            forms.save()
            return redirect('clients_view')
    
    forms = clients_forms(instance=client_item)
    context ={
        "forms":forms
    }
    return render(request , "clients/clients_update.html" , context=context)

def clients_delete(request, pk):
    client_item = clients.objects.get(pk=pk)
    client_item.delete()
    return redirect('clients_view')

# orders

def orders_view(request):
    orders_list = orders.objects.all()
    context = {
        "orders_list":orders_list
    }
    return render(request , "orders/orders.html" , context=context)

def orders_create(request):
    if request.method == "POST":
        form = orders_forms(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            order.total_amount = order.quantity * order.price
            order.save()
            return redirect('orders_view')  
    
    form = orders_forms()
    return render(request, 'orders/orders_create.html', {'forms': form})

def order_read(request , pk):
    order_item = orders.objects.get(pk=pk)
    context ={
        "order":order_item
    }
    return render(request , "orders/order_read.html" , context=context)

def orders_update(request , pk):
    order_item = orders.objects.get(pk=pk)
    
    if request.method == "POST":
        form = orders_forms(request.POST , instance=order_item)
        if form.is_valid():
            order = form.save(commit=False)
            
            order.total_amount = order.quantity * order.price
            order.save()
            return redirect('orders_view')  
    
    form = orders_forms(instance=order_item)
    return render(request, 'orders/orders_update.html', {'forms': form})

def orders_delete(request , pk):
    order_item = orders.objects.get(pk=pk)
    order_item.delete()    
    return redirect('orders_view')

# producement

def producement_view(request):
    producement_list = producement.objects.all()
    context = {
        "producement_list":producement_list
    }
    return render(request,'producement/producement.html' ,context=context)

def producement_create(request):
    if request.method == "POST":
        forms = producement_forms(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect('producement_view')
    
    forms = producement_forms()
    context = {
        "forms":forms
    }    
    return render(request, "producement/producement_create.html", context=context)

def producement_read(request, pk):
    producement_item = producement.objects.get(pk=pk)
    context = {
        "producement":producement_item
    }
    return render(request , 'producement/producement_read.html' , context=context)

def producement_update(request , pk):
    producement_item = producement.objects.get(pk=pk)
    if request.method == "POST":
        form = producement_forms(request.POST, instance=producement_item)
        if form.is_valid():
            form.save()
            next_page = request.GET.get("next")
            if next_page == "shoe_model_read":
                return redirect("shoe_model_read", pk=producement_item.shoe_model_id.id)
            else:
                return redirect("producement_view")
    else:
        form = producement_forms(instance=producement_item)
    
    context = {
        "forms": form,
        "producement": producement_item,
    }
    return render(request , "producement/producement_update.html" , context=context)

def producement_delete(request ,pk):
    producement_item = producement.objects.get(pk=pk)
    producement_item.delete()
    return redirect('producement')
