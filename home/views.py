from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import *
from django.http.response import HttpResponse
from .forms import *
from django.forms import modelformset_factory
from django.core.paginator import Paginator
from django.db.models import Case, When, Q, IntegerField, Prefetch
from collections import defaultdict
# Create your views here.
import json

from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation

SYSTEM_REFERENCE_TYPES = {
    ReferenceType.STATUS,
    ReferenceType.GENDER,
    ReferenceType.QUANTITY_TYPE,
    ReferenceType.CURRENCY,
    ReferenceType.MATERIAL_TYPE,
    ReferenceType.STOCK_MOVEMENT_TYPE,
    ReferenceType.PROFESSION,
}

NON_SYSTEM_REFERENCE_TYPES = [
    ReferenceType.COLOR,
    ReferenceType.MODEL,
    ReferenceType.MODEL_PART,

    ReferenceType.LEATHER_VARIANT,
    ReferenceType.SOLE_VARIANT,
    ReferenceType.LINING_VARIANT,
    ReferenceType.GLUE_VARIANT,
    ReferenceType.TEXTILE_VARIANT,

    ReferenceType.THREAD_VARIANT,
    ReferenceType.MIX_VARIANT,
    ReferenceType.BOX_VARIANT,
    ReferenceType.BUCKLE_VARIANT,
    ReferenceType.ELASTIC_VARIANT,
    ReferenceType.RIVET_VARIANT,
    ReferenceType.CARDBOARD_VARIANT,
    ReferenceType.CLOTH_VARIANT,
    ReferenceType.VISOR_VARIANT,
    ReferenceType.PAPER_VARIANT,
    ReferenceType.STRETCH_VARIANT,
    ReferenceType.FUR_VARIANT,
    ReferenceType.ZIPPER_VARIANT,
    ReferenceType.SPONGE_VARIANT,
    ReferenceType.VELCRO_VARIANT,
]


REFERENCE_TYPE_UI_KEY = {
    ReferenceType.STATUS: "STATUS",
    ReferenceType.MODEL: "MODEL",
    ReferenceType.MODEL_PART: "MODEL_PART",
    ReferenceType.GENDER: "GENDER",
    ReferenceType.COLOR: "COLOR",
    ReferenceType.PROFESSION: "PROFESSION",
    ReferenceType.QUANTITY_TYPE: "QUANTITY_TYPE",
    ReferenceType.CURRENCY: "CURRENCY",
    ReferenceType.MATERIAL_TYPE: "MATERIAL_TYPE",

    ReferenceType.LEATHER_VARIANT: "LEATHER_TYPE",
    ReferenceType.SOLE_VARIANT: "SOLE_TYPE",
    ReferenceType.LINING_VARIANT: "LINING",
    ReferenceType.GLUE_VARIANT: "GLUE",
    ReferenceType.TEXTILE_VARIANT: "TEXTILE",   

    ReferenceType.THREAD_VARIANT: "THREAD",
    ReferenceType.MIX_VARIANT: "MIX",
    ReferenceType.BOX_VARIANT: "BOX",
    ReferenceType.BUCKLE_VARIANT: "BUCKLE",
    ReferenceType.ELASTIC_VARIANT: "ELASTIC",
    ReferenceType.RIVET_VARIANT: "RIVET",
    ReferenceType.CARDBOARD_VARIANT: "CARDBOARD",
    ReferenceType.CLOTH_VARIANT: "CLOTH",
    ReferenceType.VISOR_VARIANT: "VISOR",
    ReferenceType.PAPER_VARIANT: "PAPER",
    ReferenceType.STRETCH_VARIANT: "STRETCH",
    ReferenceType.FUR_VARIANT: "FUR",
    ReferenceType.ZIPPER_VARIANT: "ZIPPER",
    ReferenceType.SPONGE_VARIANT: "SPONGE",
    ReferenceType.VELCRO_VARIANT: "VELCRO",
}

REFERENCE_MATERIAL_TYPE_VALUE_REFENRECE_TYPE_VALUE = {
    system_variables.LEATHER: ReferenceType.LEATHER_VARIANT.value,
    system_variables.SOLE: ReferenceType.SOLE_VARIANT.value,
    system_variables.LINING: ReferenceType.LINING_VARIANT.value,
    system_variables.GLUE: ReferenceType.GLUE_VARIANT.value,
    system_variables.TEXTILE: ReferenceType.TEXTILE_VARIANT.value,
    system_variables.THREAD: ReferenceType.THREAD_VARIANT.value,
    system_variables.MIX: ReferenceType.MIX_VARIANT.value,
    system_variables.BOX: ReferenceType.BOX_VARIANT.value,
    system_variables.BUCKLE: ReferenceType.BUCKLE_VARIANT.value,
    system_variables.ELASTIC: ReferenceType.ELASTIC_VARIANT.value,
    system_variables.RIVET: ReferenceType.RIVET_VARIANT.value,
    system_variables.CARDBOARD: ReferenceType.CARDBOARD_VARIANT.value,
    system_variables.CLOTH: ReferenceType.CLOTH_VARIANT.value,
    system_variables.VISOR: ReferenceType.VISOR_VARIANT.value,
    system_variables.PAPER: ReferenceType.PAPER_VARIANT.value,
    system_variables.STRETCH: ReferenceType.STRETCH_VARIANT.value,
    system_variables.FUR: ReferenceType.FUR_VARIANT.value,
    system_variables.ZIPPER: ReferenceType.ZIPPER_VARIANT.value,
    system_variables.SPONGE: ReferenceType.SPONGE_VARIANT.value,
    system_variables.VELCRO: ReferenceType.VELCRO_VARIANT.value,    
}



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
    # finished_producements = producement.objects.filter(status__value='BAJARILDI', IsDeleted=False)
    # quantity_producements = dict()
    # for item in finished_producements:
    #     if item.shoe_model_id.name not in quantity_producements:
    #         quantity_producements[item.shoe_model_id.name] = {"quantity":[item.quantity]}
    #     else:
    #         quantity_producements[item.shoe_model_id.name]["quantity"].append(item.quantity)
        
    #     quantity_producements[item.shoe_model_id.name]["total"] = sum(quantity_producements[item.shoe_model_id.name]["quantity"])

  
        
    # quantity_producements_json = json.dumps(quantity_producements)
    context ={
        "shoe_models":shoe_models,
        # "quantity_producements":quantity_producements_json,
    }
    
    return render(request , "index.html" , context=context)



def reference_view(request):
    # ==========================
    # POST: create reference
    # ==========================
    if request.method == "POST":
        type_str = request.POST.get("type")
        value = request.POST.get("value", "").strip().upper()

        # basic validation
        if not type_str or not value:
            return redirect("reference")

        try:
            ref_type = ReferenceType(int(type_str))
        except ValueError:
            # invalid enum value
            return redirect("reference")

        # 🚫 block system reference creation
        if ref_type in SYSTEM_REFERENCE_TYPES:
            return redirect("reference")

        # 🚫 block types not allowed for manual creation
        if ref_type not in NON_SYSTEM_REFERENCE_TYPES:
            return redirect("reference")

        # prevent duplicates (case-insensitive handled by upper())
        exists = references.objects.filter(
            type=ref_type.value,
            value=value,
            IsDeleted=False
        ).exists()

        if not exists:
            references.objects.create(
                type=ref_type.value,
                value=value,
                IsDeleted=False
            )

        return redirect("reference")

    # ==========================
    # GET: load & prepare data
    # ==========================
    reference_qs = references.objects.filter(IsDeleted=False).order_by("order", "value")

    grouped = []

    
    for rt in ReferenceType:
        items = reference_qs.filter(type=rt.value)
        if items.exists():
            ui_key = REFERENCE_TYPE_UI_KEY.get(rt)
            print("------------------------------")
            print(f"Processing reference type: {rt} with UI key: {ui_key}")
            print("------------------------------")
            # 🔥 THIS is the important line
            ui_label = getattr(system_variables, ui_key, rt.name)

            grouped.append({
                "type": rt,
                "label": ui_label,   # already Uzbek
                "items": items,
                "is_system": rt in SYSTEM_REFERENCE_TYPES,
            })


    # map type -> human label (template-safe)
    allowed_create_types_resolved = []

    for rt in NON_SYSTEM_REFERENCE_TYPES:
        ui_key = REFERENCE_TYPE_UI_KEY.get(rt)
        ui_label = getattr(system_variables, ui_key, rt.name)

        allowed_create_types_resolved.append({
            "value": rt.value,
            "label": ui_label
        })

    context = {
        "grouped_references": grouped,
        "allowed_create_types": allowed_create_types_resolved,  
        "system_types": {rt.value for rt in SYSTEM_REFERENCE_TYPES},
    }

    return render(request, "references.html", context)



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
    model_part_definations = models.Model_part_definition.objects.filter(model_id=shoe_model_item, is_deleted=False).order_by('id')
    
    context = {
        "shoe_model_item":shoe_model_item,
        "model_part_definations":model_part_definations,
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
        "shoe_model_item":shoe_model_item,
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
    payment_list = staff_payments.objects.filter(staff_id=staff_item, IsDeleted=False).order_by('date')
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
            new_staff = forms.save(commit=False)
            phone = phone_to_int(new_staff.phone_number)
            new_staff.phone_number = phone
            new_staff.save()

            return redirect('staff_view')
    
    forms = staff_forms(instance=staff_item)
    context = {
        "forms":forms,
        "back_url_name":"staff_view"
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
        "back_url_name":"clients_view"
    }
    return render(request , "update.html" , context=context)

def clients_delete(request, pk):
    client_item = clients.objects.get(pk=pk)
    client_item.IsDeleted = True
    client_item.save()
    return redirect('clients_view')

# suppliers
def supplier_view(request):
    suppliers_list = Supplier.objects.filter(IsDeleted=False).order_by('id')

    name = request.GET.get('name')
    phone = request.GET.get('phone')
    address = request.GET.get('address')

    if name:
        suppliers_list = suppliers_list.filter(name__icontains=name)
    if phone:
        suppliers_list = suppliers_list.filter(phone_number__icontains=phone)
    if address:
        suppliers_list = suppliers_list.filter(address__icontains=address)

    total_balance = sum(s.balance or 0 for s in suppliers_list)

    context = {
        'suppliers_list': suppliers_list,
        'balance': total_balance,
    }
    return render(request, 'supplier/suppliers.html', context=context)


def supplier_create(request):
    if request.method == 'POST':
        forms = supplier_forms(request.POST)
        if forms.is_valid():
            supplier = forms.save(commit=False)
            supplier.phone_number = phone_to_int(supplier.phone_number)
            supplier.save()
            return redirect('supplier_view')

    context = {'forms': supplier_forms()}
    return render(request, 'supplier/supplier_create.html', context=context)


def supplier_update(request, pk):
    supplier_item = get_object_or_404(Supplier, pk=pk, IsDeleted=False)

    if request.method == 'POST':
        forms = supplier_forms(request.POST, instance=supplier_item)
        if forms.is_valid():
            supplier = forms.save(commit=False)
            supplier.phone_number = phone_to_int(supplier.phone_number)
            supplier.save()
            return redirect('supplier_view')

    context = {
        'forms': supplier_forms(instance=supplier_item),
        'back_url_name': 'supplier_view',
    }
    return render(request, 'update.html', context=context)


def supplier_delete(request, pk):
    supplier_item = get_object_or_404(Supplier, pk=pk, IsDeleted=False)
    if supplier_item.is_system:
        messages.error(request, system_variables.SYSTEM_RECORD_DELETE_FORBIDDEN)
        return redirect('supplier_view')
    supplier_item.IsDeleted = True
    supplier_item.save()
    return redirect('supplier_view')

# orders

def orders_view(request):
    completed_id = references.objects.get(value=system_variables.COMPLETED)

    active_statuses = [
        system_variables.CREATED,
        system_variables.ACTIVE
    ]
    completed_statuses = [
        system_variables.COMPLETED,
        system_variables.CANCELED
    ]

    statuses = references.objects.filter(type=ReferenceType.STATUS.value)

    # ===== BASE QUERY =====
    orders = Orders.objects.filter(IsDeleted=False).annotate(
        status_order=Case(
            When(status__value__in=active_statuses, then=0),
            When(status__value__in=completed_statuses, then=1),
            default=1,
            output_field=IntegerField()
        )
    )

    # ===== GET FILTERS =====
    shoe_model_id = request.GET.get('shoe_model_id')
    color_id = request.GET.get('color_id')
    leather_type_id = request.GET.get('leather_type')
    sole_type_id = request.GET.get('solo_type')
    client_id = request.GET.get('client')
    status_id = request.GET.get('status')

    # ===== ORDER LEVEL FILTERS =====
    if client_id:
        orders = orders.filter(client_id=client_id)

    if status_id:
        orders = orders.filter(status=status_id)

    # ===== ORDER DETAILS FILTERS =====
    if shoe_model_id:
        orders = orders.filter(order_id_orders__model_id=shoe_model_id)

    if color_id:
        orders = orders.filter(order_id_orders__color_id=color_id)

    if leather_type_id:
        orders = orders.filter(order_id_orders__leather_type=leather_type_id)

    if sole_type_id:
        orders = orders.filter(order_id_orders__sole_type_id=sole_type_id)

    orders = orders.distinct().order_by('status_order', 'complete_date')

    # ===== DROPDOWNS =====
    shoe_models = models.shoe_model.objects.filter(IsDeleted=False)
    colors = models.references.objects.filter(
        type=models.ReferenceType.COLOR.value,
        IsDeleted=False
    )
    leather_types = models.references.objects.filter(
        type=models.ReferenceType.LEATHER_VARIANT.value,
        IsDeleted=False
    )
    sole_types = models.references.objects.filter(
        type=models.ReferenceType.SOLE_VARIANT.value,
        IsDeleted=False
    )
    clients = models.clients.objects.filter(
        is_system=False,
        IsDeleted=False
    )

    # ===== PAGINATION =====
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "orders_list": page_obj,
        "statuses": statuses,
        "completed_status_id": completed_id.pk,

        "shoe_models": shoe_models,
        "colors": colors,
        "leather_types": leather_types,
        "sole_types": sole_types,
        "clients": clients,

        # selected values
        "shoe_model_id": int(shoe_model_id) if shoe_model_id else None,
        "color_id": int(color_id) if color_id else None,
        "leather_type": int(leather_type_id) if leather_type_id else None,
        "solo_type": int(sole_type_id) if sole_type_id else None,
        "client_id": int(client_id) if client_id else None,
        "status_id": int(status_id) if status_id else None,
    }

    return render(request, "orders/orders.html", context)


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
    order_item = get_object_or_404(
        Orders.objects.select_related(
            'client_id', 'client_id__currency', 'status',
        ),
        pk=pk,
    )

    parts_prefetch = Prefetch(
        'parts',
        queryset=Order_detail_parts.objects.filter(is_deleted=False).select_related(
            'model_part_definition__part_ref_id',
            'model_part_definition__material_type_ref_id',
            'model_part_definition__unit_ref_id',
            'material_stock__variant_ref_id',
            'material_stock__color_ref_id',
            'material_stock__material_type_ref_id',
        ),
    )
    order_lines = list(
        Order_details.objects.filter(
            order_id=order_item.pk,
            IsDeleted=False,
        ).select_related(
            'model_id', 'quantity_type_id',
        ).prefetch_related(parts_prefetch).order_by('id')
    )

    context = {
        "order": order_item,
        "order_lines": order_lines,
    }
    return render(request, "orders/order_read.html", context=context)

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
PRODUCEMENT_PARTS_PREFETCH = Prefetch(
    'order_detail_id__parts',
    queryset=Order_detail_parts.objects.filter(is_deleted=False).select_related(
        'material_stock__material_type_ref_id',
        'material_stock__variant_ref_id',
        'material_stock__color_ref_id',
        'model_part_definition__part_ref_id',
    ),
)


def _producement_queryset_base():
    return producement.objects.filter(IsDeleted=False).select_related(
        'staff_id',
        'staff_id__profession',
        'shoe_model_id',
        'order_id',
        'order_id__client_id',
        'status',
        'order_detail_id',
        'quantity_type_id',
    ).prefetch_related(PRODUCEMENT_PARTS_PREFETCH)


def _serialize_order_details_for_producement():
    details_list = []
    details = Order_details.objects.filter(IsDeleted=False).select_related(
        'model_id', 'order_id', 'quantity_type_id',
    ).order_by('id')

    for detail in details:
        parts_summary = []
        for part in detail.parts.filter(is_deleted=False).select_related(
            'material_stock__variant_ref_id',
            'material_stock__color_ref_id',
            'material_stock__material_type_ref_id',
            'model_part_definition__part_ref_id',
        ):
            stock = part.material_stock
            parts_summary.append({
                'part': str(part.model_part_definition.part_ref_id),
                'material': str(stock.material_type_ref_id),
                'variant': str(stock.variant_ref_id),
                'color': str(stock.color_ref_id) if stock.color_ref_id else '',
            })
        details_list.append({
            'id': detail.id,
            'order_id': detail.order_id_id,
            'model_id': detail.model_id_id,
            'model_id__name': detail.model_id.name,
            'quantity': detail.quantity,
            'price': float(detail.price),
            'quantity_type_id': detail.quantity_type_id_id,
            'parts_summary': parts_summary,
        })
    return json.dumps(details_list)


def _producement_data_from_form(form):
    data = {
        'order_id': form.cleaned_data['order_id'],
        'shoe_model_id': form.cleaned_data['shoe_model_id'],
        'staff_id': form.cleaned_data['staff_id'],
        'quantity': form.cleaned_data['quantity'],
        'quantity_type_id': form.cleaned_data['quantity_type_id'],
        'price': form.cleaned_data['price'],
        'status': form.cleaned_data['status'],
        'date': form.cleaned_data['date'],
    }
    order_detail = form.cleaned_data.get('order_detail_id')
    if order_detail:
        data['order_detail_id'] = order_detail
    return data


def _producement_data_from_original(original, form):
    return {
        'staff_id': form.cleaned_data['staff_id'],
        'shoe_model_id': original.shoe_model_id,
        'date': form.cleaned_data['date'],
        'quantity': form.cleaned_data['quantity'],
        'quantity_type_id': form.cleaned_data['quantity_type_id'],
        'price': form.cleaned_data['price'],
        'order_id': original.order_id,
        'status': form.cleaned_data['status'],
        'order_detail_id': original.order_detail_id,
    }


def _create_chained_producement(form):
    selected = form.cleaned_data.get('producement_id')
    if not selected:
        form.add_error('producement_id', 'Oldingi ishni tanlang')
        return None
    original = producement.objects.get(id=selected.id)
    return producement.objects.create(**_producement_data_from_original(original, form))


def producement_view(request):
    professions = references.objects.filter(type=ReferenceType.PROFESSION.value, IsDeleted=False).order_by("order")

    producement_list = _producement_queryset_base().filter(
        ~Q(order_id__client_id__name=system_variables.WAREHOUSE.upper()),
    ).order_by('id')
    producement_sklat_list = _producement_queryset_base().filter(
        order_id__client_id__name=system_variables.WAREHOUSE.upper(),
    ).order_by('id')

    staff_list = staff.objects.filter(IsDeleted=False).order_by('id')
    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    statuses = references.objects.filter(IsDeleted=False, type=ReferenceType.STATUS.value).order_by('id')
    order_list = Orders.objects.filter(IsDeleted=False).order_by('id')

    staff_id = request.GET.get('staff_id')
    model = request.GET.get('shoe_model_id')
    status = request.GET.get('status')
    order = request.GET.get('order')

    valid_filters = {}
    if any([staff_id, model, status, order]):
        filters = {
            'staff_id': staff_id,
            'shoe_model_id': model,
            'status': status,
            'order_id': order,
            'IsDeleted': False,
        }
        valid_filters = {key: int(value) for key, value in filters.items() if value not in [None, '']}

        producement_list = producement_list.filter(**valid_filters).order_by('id')
        producement_sklat_list = producement_sklat_list.filter(**valid_filters).order_by('id')

    paginator = Paginator(producement_list, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    paginator_sklat = Paginator(producement_sklat_list, 10)
    page_obj_sklat = paginator_sklat.get_page(request.GET.get('page_sklat', 1))

    active_tab = request.GET.get("active_tab", "#profession-1")
    context = {
        "professions": professions,
        "producement_list": page_obj,
        "producement_sklat_list": page_obj_sklat,
        "staff_list": staff_list,
        "shoe_models": shoe_models,
        "statuses": statuses,
        "order_list": order_list,
        **valid_filters,
        "active_tab": active_tab,
    }
    return render(request, 'producement/producement.html', context=context)

def producement_create(request, ProducementForms):
    details_json = _serialize_order_details_for_producement()
    if request.method == "POST":
        forms = ProducementForms(request.POST)
        if forms.is_valid():
            producement.objects.create(**_producement_data_from_form(forms))
            return redirect('producement_view')
    else:
        forms = ProducementForms()
    return render(request, "producement/producement_create.html", {
        "forms": forms,
        "details": details_json,
    })


def producement_create_kroy(request):
    return producement_create(request, ProducementKroyForms)


def producement_create_zakatop(request):
    details_json = _serialize_order_details_for_producement()
    if request.method == "POST":
        form = ProducementZakatopForms(request.POST)
        if form.is_valid():
            if _create_chained_producement(form):
                return redirect('producement_view')
    else:
        form = ProducementZakatopForms()
    return render(request, 'producement/producement_create.html', {
        "forms": form,
        "details": details_json,
    })


def producement_create_lazir(request):
    details_json = _serialize_order_details_for_producement()
    if request.method == "POST":
        form = ProducementLazirForms(request.POST)
        if form.is_valid():
            if _create_chained_producement(form):
                return redirect('producement_view')
    else:
        form = ProducementLazirForms()
    return render(request, 'producement/producement_create.html', {
        "forms": form,
        "details": details_json,
    })


def producement_create_tuquvchi(request):
    details_json = _serialize_order_details_for_producement()
    if request.method == "POST":
        form = ProducementTuquvchiForms(request.POST)
        if form.is_valid():
            if _create_chained_producement(form):
                return redirect('producement_view')
    else:
        form = ProducementTuquvchiForms()
    return render(request, 'producement/producement_create.html', {
        "forms": form,
        "details": details_json,
    })


def producement_create_kosib(request):
    details_json = _serialize_order_details_for_producement()
    if request.method == "POST":
        form = ProducementKosibForms(request.POST)
        if form.is_valid():
            if _create_chained_producement(form):
                return redirect('producement_view')
    else:
        form = ProducementKosibForms()
    return render(request, 'producement/producement_create.html', {
        "forms": form,
        "details": details_json,
    })


def producement_create_upakovkachi(request):
    details_json = _serialize_order_details_for_producement()
    if request.method == "POST":
        form = ProducementUpakovkachiForms(request.POST)
        if form.is_valid():
            if _create_chained_producement(form):
                return redirect('producement_view')
    else:
        form = ProducementUpakovkachiForms()
    return render(request, 'producement/producement_create.html', {
        "forms": form,
        "details": details_json,
    })


def producement_read(request, pk):
    producement_item = _producement_queryset_base().get(pk=pk)
    return render(request, 'producement/producement_read.html', {
        "producement": producement_item,
    })


def producement_update(request, pk, ProducementForms):
    producement_item = producement.objects.get(pk=pk)
    details_json = _serialize_order_details_for_producement()

    if request.method == "POST":
        form = ProducementForms(request.POST, instance=producement_item)
        if form.is_valid():
            for field, value in _producement_data_from_form(form).items():
                setattr(producement_item, field, value)
            producement_item.save()

            next_page = request.GET.get("next")
            if next_page == "shoe_model_read":
                return redirect("shoe_model_read", pk=producement_item.shoe_model_id.id)
            if next_page == "work":
                return redirect("staff_view")
            return redirect("producement_view")
    else:
        initial_data = {
            'order_id': producement_item.order_id,
            'order_detail_id': producement_item.order_detail_id,
            'shoe_model_id': producement_item.shoe_model_id,
            'staff_id': producement_item.staff_id,
            'quantity': producement_item.quantity,
            'quantity_type_id': producement_item.quantity_type_id,
            'price': producement_item.price,
            'status': producement_item.status,
            'date': producement_item.date,
        }
        form = ProducementForms(initial=initial_data)

    return render(request, "producement/producement_update.html", {
        "forms": form,
        "producement": producement_item,
        "details": details_json,
    })

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
    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    colors = references.objects.filter(IsDeleted=False, type=ReferenceType.COLOR.value).order_by('id')
    leather_types = references.objects.filter(IsDeleted=False, type=ReferenceType.LEATHER_TYPE.value).order_by('id')
    sole_types = references.objects.filter(IsDeleted=False, type=ReferenceType.SOLO_TYPE.value).order_by('id')
    client_list = clients.objects.filter(IsDeleted=False).order_by('id')

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
from django.db import transaction
from django.contrib import messages


def order_detail_create(request, pk):
    order = Orders.objects.get(pk=pk)

    if request.method == "POST":
        forms = orderDetails_forms(request.POST)

        if forms.is_valid():
            new_order_detail = forms.save(commit=False)
            new_order_detail.order_id = order

            new_order_detail.total_amount = (
                new_order_detail.price * new_order_detail.quantity
            )

            # -----------------------------
            # PARTS DATA PARSE
            # -----------------------------
            parts_data = {}

            for key, value in request.POST.items():
                if key.startswith("parts["):
                    part_id = key.split("[")[1].split("]")[0]
                    field_name = key.split("[")[2].split("]")[0]

                    if part_id not in parts_data:
                        parts_data[part_id] = {}

                    parts_data[part_id][field_name] = value

            warnings = []

            prepared_data = []

            for part in parts_data.values():

                model_part = Model_part_definition.objects.get(
                    id=part["model_part_definition_id"]
                )

                order_qty = Decimal(new_order_detail.quantity)
                per_pair = model_part.quantity_per_pair
                waste = model_part.waste_percent

                required = order_qty * per_pair * (1 + waste / 100)

                try:
                    stock = Material_stock.objects.get(
                        material_type_ref_id=model_part.material_type_ref_id,
                        variant_ref_id=part["material_variant_id"],
                        color_ref_id=part["color_id"],
                        is_deleted=False
                    )
                except Material_stock.DoesNotExist:
                    messages.error(request, "Material stock topilmadi")
                    return redirect('order_read', pk=pk)

                if stock.available_quantity < required:
                    warnings.append(
                        f"{model_part.id} part uchun yetarli emas "
                        f"(kerak: {required}, mavjud: {stock.available_quantity})"
                    )

                prepared_data.append({
                    "model_part": model_part,
                    "stock": stock,
                    "required": required
                })

            with transaction.atomic():

                new_order_detail.save()

                for item in prepared_data:
                    stock = item["stock"]
                    required = item["required"]
                    model_part = item["model_part"]

                    reserve_qty = int(required)
                    stock.reserved_quantity += reserve_qty
                    stock.save(update_fields=['reserved_quantity'])

                    Order_detail_parts.objects.create(
                        order_detail=new_order_detail,
                        model_part_definition=model_part,
                        material_stock=stock,
                        quantity_required=required
                    )

            if warnings:
                for w in warnings:
                    messages.warning(request, w)

            return redirect('order_read', pk=pk)
    else:

        forms = orderDetails_forms()

    context = {
        "forms": forms,
        "pk": pk
    }

    return render(
        request,
        "orderDetails/detail_create.html",
        context=context
    )

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

    staff_id   = request.GET.get('staff_id')
    model_id   = request.GET.get('shoe_model_id')
    color_id   = request.GET.get('color_id')
    leather_id = request.GET.get('leather_type')
    sole_id    = request.GET.get('solo_type')
    status     = request.GET.get('status')
    order_id   = request.GET.get('order')
    
    filters = {
        'staff_id': staff_id,           # adjust field if needed
        'model_id': model_id,      # FK from Warehouse
        'color_id': color_id,
        'leather_type_id': leather_id,
        'sole_type_id': sole_id,
        'status': status,                          # if Sales has status
        'order_id': order_id,                      # if exists
        'IsDeleted': False,
    }
    valid_filters = {key: int(value) for key, value in filters.items() if value not in [None, '']}

    
    # warehouse_items = Warehouse.objects.filter(IsDeleted=False).order_by('id')

    warehouse_items = Warehouse.objects.filter(**valid_filters).order_by('id')

    # For dropdowns
    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    colors = references.objects.filter(IsDeleted=False, type=ReferenceType.COLOR.value).order_by('id')
    leather_types = references.objects.filter(IsDeleted=False, type=ReferenceType.LEATHER_TYPE.value).order_by('id')
    sole_types = references.objects.filter(IsDeleted=False, type=ReferenceType.SOLO_TYPE.value).order_by('id')
    client_list = clients.objects.filter(IsDeleted=False).order_by('id')

    context = {
        "warehouse_items": warehouse_items,
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


@csrf_exempt
def update_producement_status(request):
    if request.method == "POST":
        producement_id = request.POST.get("producement_id")
        status_id = request.POST.get("status_id")
        try:
            producement = models.producement.objects.get(id=producement_id)
            status = references.objects.get(id=status_id)
            producement.status = status
            producement.save()
            print("--------------------------------------------")
            print(producement_id, status_id)
            print("--------------------------------------------")
            print("--------------------------------------------")
            return JsonResponse({"success": True, "message": "Status updated"})
        except Orders.DoesNotExist:
            return JsonResponse({"success": False, "message": "Producement not found"})
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


# model_parts
def model_part_create(request, pk):
    # 1) Get the parent shoe model
    model = get_object_or_404(shoe_model, pk=pk)

    # 2) Handle POST
    if request.method == "POST":
        forms = Model_part_definition_forms(request.POST)

        if forms.is_valid():
            part = forms.save(commit=False)

            # Assign parent model automatically
            part.model_id = model

            part.save()
            # Redirect back to shoe model detail page
            return redirect("shoe_model_read", model.pk)

    else:
        # 3) Handle GET
        forms = Model_part_definition_forms()

    context = {
        "forms": forms,
        "model": model,
    }

    return render(request, "model_part/model_part_create.html", context=context)

def model_part_update(request, pk):
    part = get_object_or_404(models.Model_part_definition, pk=pk)
    if request.method == "POST":
        forms = Model_part_definition_forms(request.POST, instance=part)
        if forms.is_valid():
            forms.save()
            return redirect("shoe_model_read", part.model_id.pk)
    else:
        forms = Model_part_definition_forms(instance=part)

    context = {
        "forms": forms,
        "part": part,
    }
    return render(request, "model_part/model_part_update.html", context=context)

def model_part_delete(request, pk):
    part = get_object_or_404(models.Model_part_definition, pk=pk)
    part.is_deleted = True
    part.save()
    return redirect("shoe_model_read", part.model_id.pk)

def get_model_parts(request, pk):

    parts = Model_part_definition.objects.filter(
        model_id=pk,
        is_deleted=False
    ).select_related(
        "part_ref_id",
        "material_type_ref_id"
    ).order_by('id')

    data = []

    for part in parts:

        material_value = part.material_type_ref_id.value if part.material_type_ref_id else None

        material_type_item = references.objects.get(id=part.material_type_ref_id_id)
        

        # variantlar
        reference_type_enum_value = None
        for i in REFERENCE_MATERIAL_TYPE_VALUE_REFENRECE_TYPE_VALUE:
            if i == material_value:
                reference_type_enum_value = REFERENCE_MATERIAL_TYPE_VALUE_REFENRECE_TYPE_VALUE[i]
                break
        
        print("reference_type_enum_value: ", reference_type_enum_value)

        variants = list(
            references.objects.filter(
                type=reference_type_enum_value,
                IsDeleted=False
            ).values(
                "id",
                "value"
            )
        )
        print("material_type_ref_id_id: ", part.material_type_ref_id_id)

        print("variants: ", variants)

        # ranglar
        colors = list(
            references.objects.filter(
                type=ReferenceType.COLOR.value,
                IsDeleted=False
            ).values(
                "id",
                "value"
            )
        )

        data.append({

            "id": part.id,

            "part_name":
                part.part_ref_id.value,

            "material_type":
                material_value,

            "variants":
                variants,

            "colors":
                colors,

            "quantity_per_pair": float(part.quantity_per_pair),

            "waste_percent": float(part.waste_percent),
                
            "material_type_id":
                part.material_type_ref_id_id
        })

    return JsonResponse(data, safe=False)

# Material_stock
def material_stock_view(request):
    stocks = Material_stock.objects.filter(is_deleted=False).select_related(
        'material_type_ref_id', 'variant_ref_id', 'color_ref_id', 'unit_ref_id',
    ).order_by('id')

    purchases = Purchase.objects.filter(is_deleted=False).select_related(
        'supplier_id', 'status',
    ).prefetch_related(
        'purchase_id__material_id__material_type_ref_id',
        'purchase_id__material_id__variant_ref_id',
        'purchase_id__material_id__color_ref_id',
    ).order_by('-id')

    context = {
        "stocks": stocks,
        "purchases": purchases,
    }
    return render(request, 'material_stock/index.html', context=context)


def get_material_variants(request):
    material_type_id = request.GET.get("material_type")
    variants = []
    if material_type_id:
        try:
            material_type = references.objects.get(id=material_type_id)
            ref_type = REFERENCE_MATERIAL_TYPE_VALUE_REFENRECE_TYPE_VALUE.get(material_type.value)
            if ref_type:
                variants = list(
                    references.objects.filter(type=ref_type, IsDeleted=False).values("id", "value")
                )
        except references.DoesNotExist:
            pass
    return JsonResponse(variants, safe=False)


def purchase_create(request):
    material_types = references.objects.filter(
        type=ReferenceType.MATERIAL_TYPE.value, IsDeleted=False,
    ).order_by('order')
    colors = references.objects.filter(
        type=ReferenceType.COLOR.value, IsDeleted=False,
    ).order_by('id')
    units = references.objects.filter(
        type=ReferenceType.QUANTITY_TYPE.value, IsDeleted=False,
    ).order_by('id')
    suppliers = Supplier.objects.filter(IsDeleted=False).order_by('name')

    if request.method == "POST":
        supplier_id = request.POST.get("supplier_id")
        purchase_date = request.POST.get("purchase_date")
        paid_amount_raw = request.POST.get("paid_amount") or "0"

        items = {}
        for key, value in request.POST.items():
            if key.startswith("items["):
                idx = key.split("[")[1].split("]")[0]
                field = key.split("[")[2].split("]")[0]
                items.setdefault(idx, {})[field] = value

        valid_items = [
            it for it in items.values()
            if it.get("material_type") and it.get("variant")
            and it.get("unit") and it.get("quantity") and it.get("price")
        ]

        parsed_date = None
        if purchase_date:
            try:
                parsed_date = datetime.strptime(purchase_date.strip(), '%d %m %Y').date()
            except ValueError:
                parsed_date = None

        if not supplier_id or not parsed_date or not valid_items:
            messages.error(request, system_variables.PURCHASE_VALIDATION)
        else:
            created_status = references.objects.get(value=system_variables.CREATED)
            with transaction.atomic():
                purchase = Purchase.objects.create(
                    supplier_id_id=supplier_id,
                    purchase_date=parsed_date,
                    total_amount=Decimal("0"),
                    paid_amount=Decimal(str(paid_amount_raw)),
                    status=created_status,
                )

                total = Decimal("0")
                for it in valid_items:
                    quantity = int(it["quantity"])
                    price = Decimal(str(it["price"]))
                    amount = price * quantity
                    total += amount

                    color_id = it.get("color") or None
                    stock, _ = Material_stock.objects.get_or_create(
                        material_type_ref_id_id=it["material_type"],
                        variant_ref_id_id=it["variant"],
                        color_ref_id_id=color_id,
                        unit_ref_id_id=it["unit"],
                        is_deleted=False,
                        defaults={"stock_quantity": 0, "reserved_quantity": 0},
                    )
                    stock.stock_quantity += quantity
                    stock.save(update_fields=["stock_quantity"])

                    Purchase_item.objects.create(
                        purchase_id=purchase,
                        material_id=stock,
                        quantity=quantity,
                        price=price,
                        amount=amount,
                    )

                purchase.total_amount = total
                purchase.save(update_fields=["total_amount"])

            return redirect('material_stock_view')

    context = {
        "material_types": material_types,
        "colors": colors,
        "units": units,
        "suppliers": suppliers,
    }
    return render(request, 'material_stock/purchase_create.html', context=context)

def get_material_stock(request):
    material_type = request.GET.get("material_type")
    variant = request.GET.get("variant")
    color = request.GET.get("color")
    order_quantity_raw = request.GET.get("order_quantity")
    model_part_definition_id = request.GET.get("model_part_definition_id")

    def build_required_payload():
        if not order_quantity_raw or not model_part_definition_id:
            return {}
        try:
            order_qty = Decimal(str(order_quantity_raw))
            if order_qty < 0:
                order_qty = Decimal("0")
            model_part = Model_part_definition.objects.get(
                id=model_part_definition_id,
                is_deleted=False,
            )
            if str(model_part.material_type_ref_id_id) != str(material_type):
                return {"required_error": "Material type mos emas"}
            per_pair = model_part.quantity_per_pair
            waste = model_part.waste_percent
            required = order_qty * per_pair * (Decimal("1") + waste / Decimal("100"))
            return {
                "quantity_per_pair": float(per_pair),
                "waste_percent": float(waste),
                "required": float(required),
            }
        except (Model_part_definition.DoesNotExist, InvalidOperation, TypeError):
            return {"required_error": "Hisoblashda xatolik"}

    extra = build_required_payload()

    try:
        stock = Material_stock.objects.get(
            material_type_ref_id=material_type,
            variant_ref_id=variant,
            color_ref_id=color if color else None,
            is_deleted=False
        )

        payload = {
            "available": stock.available_quantity,
            "reserved": stock.reserved_quantity,
        }
        payload.update(extra)
        if "required" in payload:
            payload["sufficient"] = stock.available_quantity >= payload["required"]
        return JsonResponse(payload)

    except Material_stock.DoesNotExist:
        payload = {
            "available": 0,
            "reserved": 0,
            "error": "Topilmadi",
        }
        payload.update(extra)
        if "required" in payload:
            payload["sufficient"] = False
        return JsonResponse(payload)