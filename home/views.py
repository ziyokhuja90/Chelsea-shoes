from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import *
from django.http.response import HttpResponse
from .forms import *
from django.forms import modelformset_factory
from django.core.paginator import Paginator
from django.db.models import Case, When, Q

# Create your views here.
import json

from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def phone_to_int(phone_str):
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone_str))
    return digits


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
    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    finished_producements = producement.objects.filter(status__value='BAJARILDI', IsDeleted=False)
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
            if references.objects.filter(type=int(type), value=value).exists() and references.objects.filter(type=int(type), value=value.upper() ,IsDeleted=False):
                pass
            else:
                if ReferenceType(int(type)) in ReferenceType:
                    print(True)
                new_entry = references(type=int(type) , value=value.upper())
                new_entry.save()

            
    reference_models = references.objects.filter(IsDeleted=False).order_by('order')

    
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
        "forms":forms,
        "back_url_name":"home"
    }
    return render(request , 'update.html', context=context)

def shoe_model_delete(request, pk):
    shoe_model_item = shoe_model.objects.get(pk=pk)
    shoe_model_item.IsDeleted = True
    shoe_model_item.save()
    return redirect('home')

# staff
def staff_view(request):
    staff_list = staff.objects.filter(IsDeleted=False).order_by('id')
    
    producement_list = producement.objects.filter(status__value="BAJARILDI", IsDeleted=False).order_by('id')
    payment_list = staff_payments.objects.filter(IsDeleted=False).order_by('id')

    genders = references.objects.filter(type=ReferenceType.GENDER.value, IsDeleted=False).order_by("id")
    professions = references.objects.filter(type=ReferenceType.PROFESSION.value, IsDeleted=False).order_by('id')

    full_name, gender, profession, phone = request.GET.get("full_name",None),request.GET.get("gender",None),request.GET.get("profession",None),request.GET.get("phone",None)

    if full_name or gender or profession or phone:
        staff_list = staff_list.filter(full_name__icontains=full_name, gender__value__icontains=gender, profession__value__icontains=profession, phone_number__icontains=phone, IsDeleted=False).order_by('id')



    balance = sum(i.balance for i in staff_list)
    context = {
        "staff_list":staff_list,
        "producements":producement_list,
        "payment_list":payment_list,
        "balance":balance,
        "genders":genders,
        "professions":professions
    }
    return render(request , "staff/staff.html" , context=context)

def staff_read(request, pk):
    staff_item = staff.objects.get(pk=pk, IsDeleted=False)
    payment_list = staff_payments.objects.filter(IsDeleted=False).order_by('date')
    pruducements = producement.objects.filter(staff_id=staff_item, status__value="Bajarildi").order_by('date')
    context = {
        "staff":staff_item,
        "payment_list":payment_list,
        "producements":pruducements
    }
    return render(request, "staff/staff_read.html", context=context)

def staff_create(request):
    forms = staff_forms()
    if request.method == "POST":
        forms = staff_forms(request.POST)
        if forms.is_valid():
            new_staff = forms.save(commit=False)
            phone = phone_to_int(new_staff.phone_number)
            new_staff.phone_number = phone
            new_staff.save()

            return redirect('staff_view')
        else:
            forms = forms.errors

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
        "forms":forms,
        "url_back_name":"staff_view"
    }
    return render(request , "update.html" , context=context)

def staff_delete(request, pk):
    staff_item = staff.objects.get(pk=pk)
    staff_item.IsDeleted = True
    staff_item.save()
    return redirect("staff_view")

# clients   
def clients_view(request):
    clients_list = clients.objects.filter(IsDeleted=False).order_by('id')
    currencys = references.objects.filter(type=ReferenceType.CURRENCY.value, IsDeleted=False).order_by("id")
    payments = client_payments.objects.filter(IsDeleted=False).order_by('id')
    orders = Orders.objects.filter(status__value=system_variables.COMPLETED, IsDeleted=False).order_by('id')
    details = Order_details.objects.filter(
        order_id__status__value=system_variables.COMPLETED,
        order_id__client_id__is_system=False, 
        IsDeleted=False).order_by('id')

    full_name, gender, profession, phone = request.GET.get("full_name",None),request.GET.get("currency",None),request.GET.get("address",None),request.GET.get("phone",None)

    if full_name or gender or profession or phone:
        clients_list = clients_list.filter(name__icontains=full_name, currency__value__icontains=gender, address__icontains=profession, phone_number__icontains=phone, IsDeleted=False).order_by('id')

    total_balance = sum(i.balance for i in clients_list)

    context = {
        "clients_list":clients_list,
        "currencys":currencys,
        "payments":payments,
        "orders":orders,
        "details":details,
        "balance":total_balance
    }
    return render(request , "clients/clients.html" , context=context)

def clients_create(request):
    if request.method == "POST":
        forms = clients_forms(request.POST)
        if forms.is_valid():
            new_client = forms.save(commit=False)
            phone_number = phone_to_int(new_client.phone_number)
            new_client.phone_number = phone_number
            new_client.save()

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
    context = {
        "forms":forms,
        "url_back_name":"clients_view"
    }
    return render(request , "update.html" , context=context)

def clients_delete(request, pk):
    client_item = clients.objects.get(pk=pk)
    client_item.IsDeleted = True
    client_item.save()
    return redirect('clients_view')

# orders
def orders_view(request):
    # Define the statuses that are "active" or need attention
    active_statuses = ["Jarayonda", "YARATILDI"]
    completed_statuses = ["BAJARILDI", "Bekor qilindi","Qabul qilindi"]
    status = references.objects.filter(type=ReferenceType.STATUS.value)
    # Annotate orders with a custom sorting field: '0' for active, '1' for completed
    orders_list = Orders.objects.filter(IsDeleted=False).annotate(
        status__value=Case(
            When(status__value__in=active_statuses, then=0),  # Active statuses come first
            When(status__value__in=completed_statuses, then=1),  # Completed statuses come last
            default=1  # Any other status defaults to completed
        )
        ).order_by('status__value', 'complete_date')  # Sort by status first, then deadline

    paginator = Paginator(orders_list, 10)  # Paginate by 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "orders_list": page_obj,
        "statuses":status
    }
    return render(request, "orders/orders.html", context=context)

def orders_create(request):
    if request.method == "POST":
        forms  = orders_forms(request.POST)
        if forms.is_valid():
            new_entry = forms.save(commit=False)
            new_entry.total_amount = 0
            new_entry.save()
            return redirect('orders_view')
    else:
        forms = orders_forms()
    context = {
        "forms":forms
    }
    return render(request, "orders/orders_create.html", context=context)

def order_read(request, pk):
    order_item = Orders.objects.get(pk=pk)
    details = Order_details.objects.filter(order_id=order_item.pk, IsDeleted=False)

    context ={
        "order":order_item,
        "details":details
    }
    return render(request , "orders/order_read.html" , context=context)

def orders_update(request, pk):
    order_item = Orders.objects.get(pk=pk)
    
    if request.method == "POST":
        form = orders_forms(request.POST , instance=order_item)
        if form.is_valid():
            form.save()
            return redirect('orders_view')  
    
    form = orders_forms(instance=order_item)
    context = {
        "forms":form,
        "back_url_name":"orders_view"
    }
    return render(request, 'update.html', context=context)

def orders_delete(request, pk):
    order_item = Orders.objects.get(pk=pk)
    order_item.IsDeleted = True
    order_item.save()
    return redirect('orders_view')

# producement
def producement_view(request):
    professions = references.objects.filter(type=ReferenceType.PROFESSION.value, IsDeleted=False).order_by("order")

    producement_list = producement.objects.filter(~Q(order_id__client_id__name=system_variables.WAREHOUSE.upper()), IsDeleted=False).order_by('id')
    producement_sklat_list = producement.objects.filter(order_id__client_id__name=system_variables.WAREHOUSE.upper(), IsDeleted=False).order_by('id')
    
    staff_list = staff.objects.filter(IsDeleted=False)
    shoe_models = shoe_model.objects.filter(IsDeleted=False)
    colors = references.objects.filter(IsDeleted=False, type=ReferenceType.COLOR.value)
    leather_types = references.objects.filter(IsDeleted=False, type=ReferenceType.LEATHER_TYPE.value)
    sole_types = references.objects.filter(IsDeleted=False, type=ReferenceType.SOLO_TYPE.value)
    statuses = references.objects.filter(IsDeleted=False, type=ReferenceType.STATUS.value)
    order_list = Orders.objects.filter(IsDeleted=False)


    staff_id, model, color, leather, sole, status, order = request.GET.get('staff_id', None), request.GET.get('shoe_model_id',None),request.GET.get('color_id',None),request.GET.get('leather_type',None),request.GET.get('solo_type',None),request.GET.get('status',None),request.GET.get('order',None) 

    fields = [staff_id, model, color, leather, sole, status, order]
    valid_filters = {}
    
    if any(fields):
        filters = {
            'staff_id': staff_id,
            'shoe_model_id': model,
            'color_id': color,
            'leather_type': leather,
            'solo_type': sole,
            'status': status,
            'order_id': order,
            'IsDeleted': False,
        }
        valid_filters = {key: int(value) for key, value in filters.items() if value not in [None, '']}
        
        producement_list = producement.objects.filter(
            ~Q(order_id__client_id__name=system_variables.WAREHOUSE.upper(),), 
            **valid_filters

            ).order_by('id')
        
        producement_sklat_list = producement.objects.filter(
            order_id__client_id__name=system_variables.WAREHOUSE.upper(),
            **valid_filters
        ).order_by('id')



    paginator = Paginator(producement_list, 10)  # Paginate by 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    paginator_sklat = Paginator(producement_sklat_list, 10)  # Paginate by 10 items per page
    page_number_sklat = request.GET.get('page_sklat', 1)
    page_obj_sklat = paginator_sklat.get_page(page_number_sklat)


    active_tab = request.GET.get("active_tab", "#profession-1")
    context = {
        "professions":professions,
        "producement_list":page_obj,
        "producement_sklat_list":page_obj_sklat,
        "staff_list":staff_list,
        "shoe_models":shoe_models,
        "colors":colors,
        "leather_types":leather_types,
        "sole_types":sole_types,
        "statuses":statuses,
        "order_list":order_list,
        **valid_filters,
        "active_tab": active_tab

    }
    return render(request,'producement/producement.html' ,context=context)

def producement_create(request, ProducementForms):
    details = Order_details.objects.filter(IsDeleted=False).values(
        'id', 'order_id', 'model_id', 'model_id__name',
        'quantity', 'price', 'quantity_type_id',
        'color_id','leather_type','sole_type_id',
        "lining_type_id"

    )

    # Convert QuerySet to a list and handle Decimal fields
    details_list = []
    for detail in details:
        detail['price'] = float(detail['price'])  # Convert Decimal to float
        details_list.append(detail)


    details_json = json.dumps(details_list)
    if request.method == "POST":
        forms = ProducementForms(request.POST)
        if forms.is_valid():
            sole_type_id = forms.cleaned_data['order_detail_id'].sole_type_id
            producment_data = {
                'order_id': forms.cleaned_data['order_id'],
                'order_detail_id': forms.cleaned_data['order_detail_id'],
                'shoe_model_id': forms.cleaned_data['shoe_model_id'],
                'staff_id': forms.cleaned_data['staff_id'],
                'color_id': forms.cleaned_data['color_id'],
                'leather_type': forms.cleaned_data['leather_type'],
                'lining_type_id': forms.cleaned_data['lining_type_id'],
                'quantity': forms.cleaned_data['quantity'],
                'quantity_type_id': forms.cleaned_data['quantity_type_id'],
                'solo_type':sole_type_id,
                'price': forms.cleaned_data['price'],
                'status': forms.cleaned_data['status'],
                'date': forms.cleaned_data['date'],
            }
            producement.objects.create(**producment_data)
            return redirect('producement_view')
    else:
        forms = ProducementForms()
    context = {
        "forms":forms,
        "details":details_json,
    }    
    return render(request, "producement/producement_create.html", context=context)

def producement_create_kroy(request):
    details = Order_details.objects.filter(IsDeleted=False).values(
        'id', 'order_id', 'model_id', 'model_id__name',
        'quantity', 'price', 'quantity_type_id',
        'color_id','leather_type','sole_type_id',
        "lining_type_id"

    )
    details_list = []
    for detail in details:
        detail['price'] = float(detail['price'])  # Convert Decimal to float
        details_list.append(detail)


    details_json = json.dumps(details_list)

    if request.method == "POST":
        forms = ProducementKroyForms(request.POST)
        if forms.is_valid():
            sole_type_id = forms.cleaned_data['order_detail_id'].sole_type_id
            producment_data = {
                'order_id': forms.cleaned_data['order_id'],
                'shoe_model_id': forms.cleaned_data['shoe_model_id'],
                'staff_id': forms.cleaned_data['staff_id'],
                'color_id': forms.cleaned_data['color_id'],
                'leather_type': forms.cleaned_data['leather_type'],
                'lining_type_id': forms.cleaned_data['lining_type_id'],
                'quantity': forms.cleaned_data['quantity'],
                'quantity_type_id': forms.cleaned_data['quantity_type_id'],
                'solo_type':sole_type_id,
                'price': forms.cleaned_data['price'],
                'status': forms.cleaned_data['status'],
                'date': forms.cleaned_data['date'],
            }
            producement.objects.create(**producment_data)
            return redirect('producement_view')
    else:
        forms = ProducementKroyForms()
    context = {
        "forms":forms,
        "details":details_json,
    }
    return render(request, 'producement/producement_create.html', context=context)

def producement_create_zakatop(request):
    details = Order_details.objects.filter(IsDeleted=False).values(
        'id', 'order_id', 'model_id', 'model_id__name',
        'quantity', 'price', 'quantity_type_id',
        'color_id','leather_type','sole_type_id',
        "lining_type_id"
    )

    details_list = []
    for detail in details:
        detail['price'] = float(detail['price'])  # Convert Decimal to float
        details_list.append(detail)


    details_json = json.dumps(details_list)
    if request.method == "POST":
        form = ProducementZakatopForms(request.POST)
        if form.is_valid():
            # Get the selected producement_id
            selected_producement_id = form.cleaned_data['producement_id']
            try:
                # Fetch the Producement object
                original_producement = producement.objects.get(id=selected_producement_id.id)

                # Create a new Producement object
                new_producement = producement(
                    staff_id=form.cleaned_data['staff_id'],
                    shoe_model_id=original_producement.shoe_model_id,
                    date=form.cleaned_data['date'],
                    color_id=original_producement.color_id,
                    leather_type=original_producement.leather_type,
                    solo_type=original_producement.solo_type,
                    quantity=form.cleaned_data['quantity'],
                    quantity_type_id=form.cleaned_data['quantity_type_id'],
                    price=form.cleaned_data['price'],
                    order_id=original_producement.order_id,
                    status=form.cleaned_data['status'],
                    order_detail_id=original_producement.order_detail_id,
                    lining_type_id=original_producement.lining_type_id,
                    producement_id=original_producement,  # Link to original producement
                    IsDeleted=False
                )

                # Save the new Producement object
                new_producement.save()

                # Redirect to a success page or display a success message
                return redirect('producement_view')  # Replace with your success URL
            except producement.DoesNotExist:
                form.add_error('producement_id', 'Invalid Producement ID selected.')
    else:
        form = ProducementZakatopForms()
    context = {
        "forms":form
    }
    return render(request, 'producement/producement_create.html', context=context)

def producement_create_lazir(request):
    if request.method == "POST":
        form = ProducementLazirForms(request.POST)
        if form.is_valid():
            # Get the selected producement_id
            selected_producement_id = form.cleaned_data['producement_id']
            try:
                # Fetch the Producement object
                original_producement = producement.objects.get(id=selected_producement_id.id)

                # Create a new Producement object
                new_producement = producement(
                    staff_id=form.cleaned_data['staff_id'],
                    shoe_model_id=original_producement.shoe_model_id,
                    date=form.cleaned_data['date'],
                    color_id=original_producement.color_id,
                    leather_type=original_producement.leather_type,
                    solo_type=original_producement.solo_type,
                    quantity=form.cleaned_data['quantity'],
                    quantity_type_id=form.cleaned_data['quantity_type_id'],
                    price=form.cleaned_data['price'],
                    order_id=original_producement.order_id,
                    status=form.cleaned_data['status'],
                    order_detail_id=original_producement.order_detail_id,
                    lining_type_id=original_producement.lining_type_id,
                    producement_id=original_producement,  # Link to original producement
                    IsDeleted=False
                )

                # Save the new Producement object
                new_producement.save()

                # Redirect to a success page or display a success message
                return redirect('producement_view')  # Replace with your success URL
            except producement.DoesNotExist:
                form.add_error('producement_id', 'Invalid Producement ID selected.')
        else:
            for field in form:
                print(field.errors, "------------")
            print(form.errors)
    else:
        form = ProducementLazirForms()
    context = {
        "forms":form
    }
    return render(request, 'producement/producement_create.html', context=context)

def producement_create_tuquvchi(request):
    if request.method == "POST":
        form = ProducementTuquvchiForms(request.POST)
        if form.is_valid():
            # Get the selected producement_id
            selected_producement_id = form.cleaned_data['producement_id']
            try:
                # Fetch the Producement object
                original_producement = producement.objects.get(id=selected_producement_id.id)

                # Create a new Producement object
                new_producement = producement(
                    staff_id=form.cleaned_data['staff_id'],
                    shoe_model_id=original_producement.shoe_model_id,
                    date=form.cleaned_data['date'],
                    color_id=original_producement.color_id,
                    leather_type=original_producement.leather_type,
                    solo_type=original_producement.solo_type,
                    quantity=form.cleaned_data['quantity'],
                    quantity_type_id=form.cleaned_data['quantity_type_id'],
                    price=form.cleaned_data['price'],
                    order_id=original_producement.order_id,
                    status=form.cleaned_data['status'],
                    order_detail_id=original_producement.order_detail_id,
                    lining_type_id=original_producement.lining_type_id,
                    producement_id=original_producement,  # Link to original producement
                    IsDeleted=False
                )

                # Save the new Producement object
                new_producement.save()

                # Redirect to a success page or display a success message
                return redirect('producement_view')  # Replace with your success URL
            except producement.DoesNotExist:
                form.add_error('producement_id', 'Invalid Producement ID selected.')
    else:
        form = ProducementTuquvchiForms()
    context = {
        "forms":form
    }
    return render(request, 'producement/producement_create.html', context=context)

def producement_create_kosib(request):
    producement_list = producement.objects.filter(staff_id__profession__value=system_variables.TUQUVCHI ,IsDeleted=False).values(
        'id', 'solo_type'
    )
    data = list(producement_list)
    
    # Convert the list to a JSON string
    data_json = json.dumps(data)

    if request.method == "POST":
        form = ProducementKosibForms(request.POST)
        if form.is_valid():
            # Get the selected producement_id
            selected_producement_id = form.cleaned_data['producement_id']
            try:
                # Fetch the Producement object
                original_producement = producement.objects.get(id=selected_producement_id.id)

                # Create a new Producement object
                new_producement = producement(
                    staff_id=form.cleaned_data['staff_id'],
                    shoe_model_id=original_producement.shoe_model_id,
                    date=form.cleaned_data['date'],
                    color_id=original_producement.color_id,
                    leather_type=original_producement.leather_type,
                    solo_type=original_producement.solo_type,
                    quantity=form.cleaned_data['quantity'],
                    quantity_type_id=form.cleaned_data['quantity_type_id'],
                    price=form.cleaned_data['price'],
                    order_id=original_producement.order_id,
                    status=form.cleaned_data['status'],
                    order_detail_id=original_producement.order_detail_id,
                    lining_type_id=original_producement.lining_type_id,
                    producement_id=original_producement,  # Link to original producement
                    IsDeleted=False
                )

                # Save the new Producement object
                new_producement.save()

                # Redirect to a success page or display a success message
                return redirect('producement_view')  # Replace with your success URL
            except producement.DoesNotExist:
                form.add_error('producement_id', 'Invalid Producement ID selected.')
    else:
        forms = ProducementKosibForms()
    context = {
        "forms":forms,
        "producements":data_json
    }
    return render(request, 'producement/producement_create.html', context=context)

def producement_create_upakovkachi(request):
    if request.method == "POST":
        form = ProducementUpakovkachiForms(request.POST)
        if form.is_valid():
            # Get the selected producement_id
            selected_producement_id = form.cleaned_data['producement_id']
            try:
                # Fetch the Producement object
                original_producement = producement.objects.get(id=selected_producement_id.id)

                # Create a new Producement object
                new_producement = producement(
                    staff_id=form.cleaned_data['staff_id'],
                    shoe_model_id=original_producement.shoe_model_id,
                    date=form.cleaned_data['date'],
                    color_id=original_producement.color_id,
                    leather_type=original_producement.leather_type,
                    solo_type=original_producement.solo_type,
                    quantity=form.cleaned_data['quantity'],
                    quantity_type_id=form.cleaned_data['quantity_type_id'],
                    price=form.cleaned_data['price'],
                    order_id=original_producement.order_id,
                    status=form.cleaned_data['status'],
                    order_detail_id=original_producement.order_detail_id,
                    lining_type_id=original_producement.lining_type_id,
                    producement_id=original_producement,  # Link to original producement
                    IsDeleted=False
                )

                # Save the new Producement object
                new_producement.save()

                # Redirect to a success page or display a success message
                return redirect('producement_view')  # Replace with your success URL
            except producement.DoesNotExist:
                form.add_error('producement_id', 'Invalid Producement ID selected.')
    else:
        form = ProducementUpakovkachiForms()
    context = {
        "forms":form
    }
    return render(request, 'producement/producement_create.html', context=context)

def producement_read(request, pk):
    producement_item = producement.objects.get(pk=pk)
    context = {
        "producement":producement_item
    }
    return render(request , 'producement/producement_read.html' , context=context)

def producement_update(request, pk, ProducementForms):
    producement_item = producement.objects.get(pk=pk)

    # Prepare Order_details JSON (same as in create)
    details = Order_details.objects.filter(IsDeleted=False).values(
        'id', 'order_id', 'model_id', 'model_id__name',
        'quantity', 'price', 'quantity_type_id',
        'color_id', 'leather_type', 'sole_type_id',
        'lining_type_id'
    )
    details_list = []
    for detail in details:
        detail['price'] = float(detail['price'])  # Decimal to float
        details_list.append(detail)
    details_json = json.dumps(details_list)

    if request.method == "POST":
        form = ProducementForms(request.POST, instance=producement_item)
        if form.is_valid():
            # Update manually
            sole_type_id = form.cleaned_data['order_detail_id'].sole_type_id
            producment_data = {
                'order_id': form.cleaned_data['order_id'],
                'order_detail_id': form.cleaned_data['order_detail_id'],
                'shoe_model_id': form.cleaned_data['shoe_model_id'],
                'staff_id': form.cleaned_data['staff_id'],
                'color_id': form.cleaned_data['color_id'],
                'leather_type': form.cleaned_data['leather_type'],
                'lining_type_id': form.cleaned_data['lining_type_id'],
                'quantity': form.cleaned_data['quantity'],
                'quantity_type_id': form.cleaned_data['quantity_type_id'],
                'solo_type': sole_type_id,
                'price': form.cleaned_data['price'],
                'status': form.cleaned_data['status'],
                'date': form.cleaned_data['date'],
            }

            # Manually update fields
            for field, value in producment_data.items():
                setattr(producement_item, field, value)
            producement_item.save()

            next_page = request.GET.get("next")
            if next_page == "shoe_model_read":
                return redirect("shoe_model_read", pk=producement_item.shoe_model_id.id)
            elif next_page == "work":
                return redirect("staff_view")
            else:
                return redirect("producement_view")
    else:
        # Set initial values from instance manually
        initial_data = {
            'order_id': producement_item.order_id,
            'order_detail_id': producement_item.order_detail_id,
            'shoe_model_id': producement_item.shoe_model_id,
            'staff_id': producement_item.staff_id,
            'color_id': producement_item.color_id,
            'leather_type': producement_item.leather_type,
            'lining_type_id': producement_item.lining_type_id,
            'quantity': producement_item.quantity,
            'quantity_type_id': producement_item.quantity_type_id,
            'price': producement_item.price,
            'status': producement_item.status,
            'date': producement_item.date,
        }
        form = ProducementForms(initial=initial_data)

    context = {
        "forms": form,
        "producement": producement_item,
        "details": details_json,
    }
    return render(request, "producement/producement_update.html", context=context)

def producement_delete(request ,pk):
    producement_item = producement.objects.get(pk=pk)
    producement_item.IsDeleted = True
    producement_item.save()
    return redirect('producement_view') 

# staff_payments
def staff_payment_create(request):
    if request.method == "POST":
        forms = staff_payments_forms(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect('staff_view')
    else:
        forms = staff_payments_forms()
    
    context = {
        "forms":forms
    }
    return render(request, 'staff/staff_payment_create.html', context=context)

def staff_payment_read_create(request, pk):
    staff_item = staff.objects.get(pk=pk)
    if request.method == "POST":
        forms = staff_payments_read_forms(request.POST)

        print("-----------------------00---------------------")
        if forms.is_valid():
            staff_p = forms.save(commit=False)
            staff_p.staff_id = staff_item
            staff_p.save()
            return redirect('staff_read', pk=pk)
        else:
            print("form errors: ", forms.errors)
    else:
        forms = staff_payments_read_forms()
    
    context = {
        "forms":forms
    }
    return render(request, 'staff/staff_payment_create.html', context=context)

def staff_payment_update(request, pk):
    staff_payment_item = staff_payments.objects.get(pk=pk)
    if request.method == "POST":
        forms = staff_payments_forms(request.POST, instance=staff_payment_item)
        if forms.is_valid():
            forms.save()
            return redirect('staff_view')
    else:
        forms = staff_payments_forms(instance=staff_payment_item)
    
    context = {
        "forms":forms
    }
    return render(request, 'staff/staff_payment_update.html', context=context)

def staff_payment_delete(request, pk):
    staff_payment_item = staff_payments.objects.get(pk=pk)
    staff_payment_item.IsDeleted = True
    staff_payment_item.save()

    return redirect('staff_view')

# Sale 
def sales_view(request):
    
    staff_id   = request.GET.get('staff_id')
    model_id   = request.GET.get('shoe_model_id')
    color_id   = request.GET.get('color_id')
    leather_id = request.GET.get('leather_type')
    sole_id    = request.GET.get('solo_type')
    status     = request.GET.get('status')
    order_id   = request.GET.get('order')

    # Put them in a dict
    filters = {
        'warehouse__staff_id': staff_id,           # adjust field if needed
        'warehouse__model_id': model_id,      # FK from Warehouse
        'warehouse__color_id': color_id,
        'warehouse__leather_type_id': leather_id,
        'warehouse__sole_type_id': sole_id,
        'status': status,                          # if Sales has status
        'order_id': order_id,                      # if exists
        'IsDeleted': False,
    }

    # Remove None or empty values
    valid_filters = {key: int(value) for key, value in filters.items() if value not in [None, '']}

    # Query sales
    sold_items = Sales.objects.filter(**valid_filters).order_by('id')

    # For dropdowns
    shoe_models = shoe_model.objects.filter(IsDeleted=False)
    colors = references.objects.filter(IsDeleted=False, type=ReferenceType.COLOR.value)
    leather_types = references.objects.filter(IsDeleted=False, type=ReferenceType.LEATHER_TYPE.value)
    sole_types = references.objects.filter(IsDeleted=False, type=ReferenceType.SOLO_TYPE.value)
    client_list = clients.objects.filter(IsDeleted=False)

    context = {
        "sold_items": sold_items,
        "shoe_models": shoe_models,
        "colors": colors,
        "leather_types": leather_types,
        "sole_types": sole_types,
        "clients": client_list,
        "shoe_model_id": model_id,
        "color_id": color_id,
        "leather_type": leather_id,
        "solo_type": sole_id,
        "status": status,
        "order": order_id,
        "staff_id": staff_id,
        
    }

    return render(request, 'Sale/sale.html', context=context)

def sales_create(request):
    if request.method == "POST":
        forms = SalesForm(request.POST)
        if forms.is_valid():
            new = forms.save(commit=False)
            new.total_price = new.quantity * new.price
            new.save()
            return redirect('sale')
    else:
        forms = SalesForm()

    context = {
        "forms": forms
    }
    return render(request, 'Sale/sales_create.html', context=context)

def sales_update(request, pk):
    sale = Sales.objects.get(pk=pk)
    if request.method == "POST":
        forms = SalesForm(request.POST, instance=sale)
        if forms.is_valid():
            new = forms.save(commit=False)
            # new.total_price = new.quantity * new.price
            new.save()
            return redirect('sale')
    else:
        forms = SalesForm(instance=sale)

    context = {
        "forms": forms
    }
    return render(request, 'Sale/sales_update.html', context=context)

def sales_delete(request, pk):
    sale = Sales.objects.get(pk=pk)
    sale.IsDeleted = True
    sale.save()
    return redirect('sale')


# order_details
def order_detail_create(request, pk):
    order = Orders.objects.get(pk=pk)
    if request.method == "POST":
        forms = orderDetails_forms(request.POST)
        if forms.is_valid():
            new_order_detail = forms.save(commit=False)

            # Try to find an existing match
            existing_detail = Order_details.objects.filter(
            order_id=order,
            model_id=new_order_detail.model_id,
            leather_type=new_order_detail.leather_type,
            color_id=new_order_detail.color_id,
            lining_type_id=new_order_detail.lining_type_id,
            price=new_order_detail.price,
            sole_type_id=new_order_detail.sole_type_id
            ).first()

            if existing_detail:
                # Update quantity
                existing_detail.quantity += new_order_detail.quantity
                existing_detail.total_amount = existing_detail.price * existing_detail.quantity
                existing_detail.save()
            else:
                # Set order and total for new entry
                new_order_detail.order_id = order
                new_order_detail.total_amount = new_order_detail.price * new_order_detail.quantity
                new_order_detail.save()

            return redirect('order_read', pk=pk)
    else:
        forms = orderDetails_forms()
    
    context = {
        "forms":forms,
        "pk":pk
    }
    return render(request, "orderDetails/detail_create.html", context=context)

def order_detail_update(request, pk):
    detail = Order_details.objects.get(pk=pk)
    if request.method == "POST":
        forms = orderDetails_forms(request.POST, instance=detail)
        if forms.is_valid():
            new_order_detail = forms.save(commit=False)
            new_order_detail.total_amount = new_order_detail.price * new_order_detail.quantity
            new_order_detail.save()
            return redirect('order_read', pk=detail.order_id.pk)
    else:
        forms = orderDetails_forms(instance=detail)

    context = {
        "forms":forms
    }
    return render(request, 'orderDetails/detail_update.html', context=context)

def order_detail_delete(request, pk):
    detail = Order_details.objects.get(pk=pk)
    detail.IsDeleted = True
    detail.save()
    return redirect('order_read', pk=detail.order_id.pk)


# warehouse
def warehouse_view(request):
    warehouse_items = Warehouse.objects.filter(IsDeleted=False).order_by('id')
    context = {
        "warehouse_items": warehouse_items
    }
    return render(request, 'warehouse/warehouse.html', context=context)




# next
def order_next_status(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    current_ref = order.status
    next_status = references.objects.filter(
        IsDeleted=False,
        type=ReferenceType.STATUS.value, 
        order__gt=current_ref.order
    ).order_by('order').first()
    if next_status:
        order.status = next_status
        order.save()
    return redirect('orders_view')  # adjust to your list view

# previuos
def order_prev_status(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    current_ref = order.status
    prev_status = references.objects.filter(
        IsDeleted=False,
        type=ReferenceType.STATUS.value,
        order__lt=current_ref.order
    ).order_by('-order').first()
    if prev_status:
        order.status = prev_status
        order.save()
    return redirect('orders_view')

@csrf_exempt
def update_order_status(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status_id = request.POST.get("status_id")

        try:
            order = Orders.objects.get(id=order_id)
            status = references.objects.get(id=status_id)
            order.status = status
            order.save()
            return JsonResponse({"success": True, "message": "Status updated"})
        except Orders.DoesNotExist:
            return JsonResponse({"success": False, "message": "Order not found"})
        except references.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid status"})

    return JsonResponse({"success": False, "message": "Invalid request"})

# client_payments

def client_payment_create(request):
    if request.method == "POST":
        forms = Client_payments_forms(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect('clients_view')
    else:
        forms = Client_payments_forms()
    
    context = {
        "forms":forms
    }
    return render(request, 'clients/client_payment_update.html', context=context)


def client_payment_update(request, pk):
    client_payment_item = client_payments.objects.get(pk=pk)
    if request.method == "POST":
        forms = Client_payments_forms(request.POST, instance=client_payment_item)
        if forms.is_valid():
            forms.save()
            return redirect('clients_view')
    else:
        forms = Client_payments_forms(instance=client_payment_item)
    
    context = {
        "forms":forms
    }
    return render(request, 'clients/client_payment_update.html', context=context)

def client_payment_delete(request, pk):
    payment = client_payments.objects.get(pk=pk)
    payment.IsDeleted = True
    payment.save()
    return redirect('clients_view')