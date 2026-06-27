from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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
from urllib.parse import urlencode

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
    ReferenceType.STOCK_MOVEMENT_TYPE: "MOVEMENT_TYPE",

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
    shoe_models_qs = shoe_model.objects.filter(IsDeleted=False).order_by('id')

    name = request.GET.get('name', '').strip()
    code = request.GET.get('code', '').strip()
    if name:
        shoe_models_qs = shoe_models_qs.filter(name__icontains=name)
    if code:
        shoe_models_qs = shoe_models_qs.filter(code__icontains=code)

    shoe_models_page, shoe_models_fq, shoe_models_page_param = _paginate(request, shoe_models_qs, 'page')
    context = {
        "shoe_models": shoe_models_page,
        "shoe_models_page_param": shoe_models_page_param,
        "shoe_models_filter_query": shoe_models_fq,
    }
    return render(request, "index.html", context=context)



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
        items_qs = reference_qs.filter(type=rt.value)
        if items_qs.exists():
            ui_key = REFERENCE_TYPE_UI_KEY.get(rt)
            ui_label = getattr(system_variables, ui_key, rt.name)
            page_key = f'page_ref_{rt.value}'
            items_page, items_fq, _ = _paginate(request, items_qs, page_key)
            grouped.append({
                "type": rt,
                "label": ui_label,
                "items": items_page,
                "page_key": page_key,
                "filter_query": items_fq,
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
        forms = shoe_model_forms(request.POST, request.FILES)
        if forms.is_valid():
            forms.save()
            return redirect('home')
    else:
        forms = shoe_model_forms()
    context = {
        "forms": forms,
        "cancel_url": reverse('home'),
    }
    return render(request, "shoe_model/shoe_model_create.html", context=context)

def shoe_model_read(request, pk):
    shoe_model_item = shoe_model.objects.get(pk=pk)
    parts_qs = models.Model_part_definition.objects.filter(
        model_id=shoe_model_item, is_deleted=False,
    ).select_related(
        'part_ref_id', 'material_type_ref_id', 'unit_ref_id',
    ).order_by('id')

    part_id = _safe_int(request.GET.get('part_id'))
    material_type_id = _safe_int(request.GET.get('material_type_id'))
    is_required = request.GET.get('is_required')
    if part_id:
        parts_qs = parts_qs.filter(part_ref_id_id=part_id)
    if material_type_id:
        parts_qs = parts_qs.filter(material_type_ref_id_id=material_type_id)
    if is_required in ('1', '0'):
        parts_qs = parts_qs.filter(is_required=(is_required == '1'))

    parts_page, parts_fq, parts_page_param = _paginate(request, parts_qs, 'page')

    context = {
        "shoe_model_item": shoe_model_item,
        "model_part_definations": parts_page,
        "parts_page_param": parts_page_param,
        "parts_filter_query": parts_fq,
        "parts_list": references.objects.filter(
            type=ReferenceType.MODEL_PART.value, IsDeleted=False,
        ).order_by('order', 'value'),
        "material_types": references.objects.filter(
            type=ReferenceType.MATERIAL_TYPE.value, IsDeleted=False,
        ).order_by('order', 'value'),
        "part_id": part_id,
        "material_type_id": material_type_id,
        "is_required": is_required,
    }
    return render(request, 'shoe_model/shoe_model_read.html', context=context)

def shoe_model_update(request, pk):
    shoe_model_item = shoe_model.objects.get(pk=pk)

    if request.method == "POST":
        forms = shoe_model_forms(request.POST, request.FILES, instance=shoe_model_item)
        if forms.is_valid():
            forms.save()
            return redirect('shoe_model_read', pk=pk)

    forms = shoe_model_forms(instance=shoe_model_item)
    context = {
        "forms": forms,
        "shoe_model_item": shoe_model_item,
        "cancel_url": reverse('shoe_model_read', args=[pk]),
    }
    return render(request, 'shoe_model/shoe_model_update.html', context=context)

def shoe_model_delete(request, pk):
    shoe_model_item = shoe_model.objects.get(pk=pk)
    shoe_model_item.IsDeleted = True
    shoe_model_item.save()
    return redirect('home')

# staff
def _completed_producements_queryset(**filters):
    return producement.objects.filter(
        status__value=system_variables.COMPLETED,
        IsDeleted=False,
        **filters,
    ).select_related(
        'staff_id',
        'staff_id__profession',
        'shoe_model_id',
        'status',
        'order_id',
        'order_id__client_id',
        'order_detail_id',
        'quantity_type_id',
    ).order_by('-date', '-id')


def staff_view(request):
    staff_qs = staff.objects.filter(IsDeleted=False).order_by('id')

    genders = references.objects.filter(type=ReferenceType.GENDER.value, IsDeleted=False).order_by("id")
    professions = references.objects.filter(type=ReferenceType.PROFESSION.value, IsDeleted=False).order_by('id')

    full_name = request.GET.get("full_name")
    gender = request.GET.get("gender")
    profession = request.GET.get("profession")
    phone = request.GET.get("phone")

    if full_name or gender or profession or phone:
        staff_qs = staff_qs.filter(
            full_name__icontains=full_name or '',
            gender__value__icontains=gender or '',
            profession__value__icontains=profession or '',
            phone_number__icontains=phone or '',
            IsDeleted=False,
        ).order_by('id')

    balance = sum(i.balance for i in staff_qs)

    staff_page, staff_fq, staff_page_param = _paginate(request, staff_qs, 'page_staff')

    all_staff = staff.objects.filter(IsDeleted=False).order_by('id')
    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    order_list = Orders.objects.filter(IsDeleted=False).order_by('id')

    payments_qs = staff_payments.objects.filter(IsDeleted=False).select_related('staff_id').order_by('-date', '-id')
    payment_staff = _safe_int(request.GET.get('payment_staff'))
    payment_date = _safe_date(request.GET.get('payment_date'))
    if payment_staff:
        payments_qs = payments_qs.filter(staff_id_id=payment_staff)
    if payment_date:
        payments_qs = payments_qs.filter(date=payment_date)
    payments_page, payments_fq, payments_page_param = _paginate(
        request, payments_qs, 'page_payments', {'active_tab': '#payments'},
    )

    works_qs = _completed_producements_queryset()
    work_staff = _safe_int(request.GET.get('work_staff'))
    work_model = _safe_int(request.GET.get('work_model'))
    work_order = _safe_int(request.GET.get('work_order'))
    if work_staff:
        works_qs = works_qs.filter(staff_id_id=work_staff)
    if work_model:
        works_qs = works_qs.filter(shoe_model_id_id=work_model)
    if work_order:
        works_qs = works_qs.filter(order_id_id=work_order)
    works_page, works_fq, works_page_param = _paginate(
        request, works_qs, 'page_works', {'active_tab': '#work'},
    )

    context = {
        "staff_list": staff_page,
        "staff_page_param": staff_page_param,
        "staff_filter_query": staff_fq,
        "producements": works_page,
        "works_page_param": works_page_param,
        "works_filter_query": works_fq,
        "payment_list": payments_page,
        "payments_page_param": payments_page_param,
        "payments_filter_query": payments_fq,
        "balance": balance,
        "genders": genders,
        "professions": professions,
        "all_staff": all_staff,
        "shoe_models": shoe_models,
        "order_list": order_list,
        "payment_staff": payment_staff,
        "payment_date": request.GET.get('payment_date', ''),
        "work_staff": work_staff,
        "work_model": work_model,
        "work_order": work_order,
        "active_tab": request.GET.get('active_tab', '#payments'),
    }
    return render(request, "staff/staff.html", context=context)


def staff_read(request, pk):
    staff_item = get_object_or_404(staff, pk=pk, IsDeleted=False)

    payments_qs = staff_payments.objects.filter(staff_id=staff_item, IsDeleted=False).order_by('-date')
    payment_date = _safe_date(request.GET.get('payment_date'))
    if payment_date:
        payments_qs = payments_qs.filter(date=payment_date)
    payments_page, payments_fq, payments_page_param = _paginate(
        request, payments_qs, 'page_payments', {'active_tab': '#payments'},
    )

    works_qs = _completed_producements_queryset(staff_id=staff_item)
    work_model = _safe_int(request.GET.get('work_model'))
    work_order = _safe_int(request.GET.get('work_order'))
    if work_model:
        works_qs = works_qs.filter(shoe_model_id_id=work_model)
    if work_order:
        works_qs = works_qs.filter(order_id_id=work_order)
    works_page, works_fq, works_page_param = _paginate(
        request, works_qs, 'page_works', {'active_tab': '#work'},
    )

    context = {
        "staff": staff_item,
        "payment_list": payments_page,
        "payments_page_param": payments_page_param,
        "payments_filter_query": payments_fq,
        "producements": works_page,
        "works_page_param": works_page_param,
        "works_filter_query": works_fq,
        "shoe_models": shoe_model.objects.filter(IsDeleted=False).order_by('id'),
        "order_list": Orders.objects.filter(IsDeleted=False).order_by('id'),
        "payment_date": request.GET.get('payment_date', ''),
        "work_model": work_model,
        "work_order": work_order,
        "active_tab": request.GET.get('active_tab', '#payments'),
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
    clients_qs = clients.objects.filter(IsDeleted=False).order_by('id')
    currencys = references.objects.filter(type=ReferenceType.CURRENCY.value, IsDeleted=False).order_by("id")

    full_name = request.GET.get("full_name")
    currency = request.GET.get("currency")
    address = request.GET.get("address")
    phone = request.GET.get("phone")

    if full_name or currency or address or phone:
        clients_qs = clients_qs.filter(
            name__icontains=full_name or '',
            currency__value__icontains=currency or '',
            address__icontains=address or '',
            phone_number__icontains=phone or '',
            IsDeleted=False,
        ).order_by('id')

    total_balance = sum(i.balance for i in clients_qs)

    clients_page, clients_fq, clients_page_param = _paginate(request, clients_qs, 'page_clients')

    all_clients = clients.objects.filter(IsDeleted=False).order_by('id')
    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    order_list = Orders.objects.filter(IsDeleted=False).order_by('id')

    payments_qs = client_payments.objects.filter(IsDeleted=False).select_related('client_id').order_by('-date', '-id')
    payment_client = _safe_int(request.GET.get('payment_client'))
    payment_date = _safe_date(request.GET.get('payment_date'))
    if payment_client:
        payments_qs = payments_qs.filter(client_id_id=payment_client)
    if payment_date:
        payments_qs = payments_qs.filter(date=payment_date)
    payments_page, payments_fq, payments_page_param = _paginate(
        request, payments_qs, 'page_payments', {'active_tab': '#payments'},
    )

    details_qs = Order_details.objects.filter(
        order_id__status__value=system_variables.COMPLETED,
        order_id__client_id__is_system=False,
        IsDeleted=False,
    ).select_related('order_id', 'order_id__client_id', 'model_id', 'order_id__status').order_by('-id')
    detail_client = _safe_int(request.GET.get('detail_client'))
    detail_model = _safe_int(request.GET.get('detail_model'))
    detail_order = _safe_int(request.GET.get('detail_order'))
    if detail_client:
        details_qs = details_qs.filter(order_id__client_id_id=detail_client)
    if detail_model:
        details_qs = details_qs.filter(model_id_id=detail_model)
    if detail_order:
        details_qs = details_qs.filter(order_id_id=detail_order)
    details_page, details_fq, details_page_param = _paginate(
        request, details_qs, 'page_details', {'active_tab': '#work'},
    )

    context = {
        "clients_list": clients_page,
        "clients_page_param": clients_page_param,
        "clients_filter_query": clients_fq,
        "currencys": currencys,
        "payments": payments_page,
        "payments_page_param": payments_page_param,
        "payments_filter_query": payments_fq,
        "details": details_page,
        "details_page_param": details_page_param,
        "details_filter_query": details_fq,
        "balance": total_balance,
        "all_clients": all_clients,
        "shoe_models": shoe_models,
        "order_list": order_list,
        "payment_client": payment_client,
        "payment_date": request.GET.get('payment_date', ''),
        "detail_client": detail_client,
        "detail_model": detail_model,
        "detail_order": detail_order,
        "active_tab": request.GET.get('active_tab', '#payments'),
    }
    return render(request, "clients/clients.html", context=context)

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
    suppliers_qs = Supplier.objects.filter(IsDeleted=False).order_by('id')

    name = request.GET.get('name')
    phone = request.GET.get('phone')
    address = request.GET.get('address')

    if name:
        suppliers_qs = suppliers_qs.filter(name__icontains=name)
    if phone:
        suppliers_qs = suppliers_qs.filter(phone_number__icontains=phone)
    if address:
        suppliers_qs = suppliers_qs.filter(address__icontains=address)

    total_balance = sum(s.balance or 0 for s in suppliers_qs)
    suppliers_page, suppliers_fq, suppliers_page_param = _paginate(request, suppliers_qs, 'page')

    context = {
        'suppliers_list': suppliers_page,
        'suppliers_page_param': suppliers_page_param,
        'suppliers_filter_query': suppliers_fq,
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

def _safe_int(value):
    if not value:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _safe_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


PAGE_SIZE = 10


def _paginate(request, queryset, page_param='page', extra_params=None):
    page_obj = Paginator(queryset, PAGE_SIZE).get_page(request.GET.get(page_param, 1))
    params = {k: v for k, v in request.GET.items() if v and k != page_param}
    if extra_params:
        params.update(extra_params)
    return page_obj, urlencode(params), page_param


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

    statuses = references.objects.filter(
        type=ReferenceType.STATUS.value,
        IsDeleted=False,
    ).order_by('order')

    orders = Orders.objects.filter(IsDeleted=False).select_related(
        'client_id', 'client_id__currency', 'status',
    ).annotate(
        status_order=Case(
            When(status__value__in=active_statuses, then=0),
            When(status__value__in=completed_statuses, then=1),
            default=1,
            output_field=IntegerField()
        )
    )

    shoe_model_id = _safe_int(request.GET.get('shoe_model_id'))
    color_id = _safe_int(request.GET.get('color_id'))
    leather_type_id = _safe_int(request.GET.get('leather_type'))
    sole_type_id = _safe_int(request.GET.get('solo_type'))
    client_id = _safe_int(request.GET.get('client'))
    status_id = _safe_int(request.GET.get('status'))

    if client_id:
        orders = orders.filter(client_id=client_id)

    if status_id:
        orders = orders.filter(status_id=status_id)

    active_details = Q(order_id_orders__IsDeleted=False)

    if shoe_model_id:
        orders = orders.filter(active_details, order_id_orders__model_id=shoe_model_id)

    active_parts = Q(
        order_id_orders__parts__is_deleted=False,
        order_id_orders__IsDeleted=False,
    )

    if color_id:
        orders = orders.filter(
            active_parts,
            order_id_orders__parts__material_stock__color_ref_id=color_id,
        )

    if leather_type_id:
        leather_material = references.objects.filter(
            type=ReferenceType.MATERIAL_TYPE.value,
            value=system_variables.LEATHER,
            IsDeleted=False,
        ).first()
        leather_filter = {
            'order_id_orders__parts__material_stock__variant_ref_id': leather_type_id,
        }
        if leather_material:
            leather_filter['order_id_orders__parts__material_stock__material_type_ref_id'] = leather_material.id
        orders = orders.filter(active_parts, **leather_filter)

    if sole_type_id:
        sole_material = references.objects.filter(
            type=ReferenceType.MATERIAL_TYPE.value,
            value=system_variables.SOLE,
            IsDeleted=False,
        ).first()
        sole_filter = {
            'order_id_orders__parts__material_stock__variant_ref_id': sole_type_id,
        }
        if sole_material:
            sole_filter['order_id_orders__parts__material_stock__material_type_ref_id'] = sole_material.id
        orders = orders.filter(active_parts, **sole_filter)

    orders = orders.distinct().order_by('status_order', 'complete_date')

    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    colors = references.objects.filter(
        type=ReferenceType.COLOR.value,
        IsDeleted=False,
    ).order_by('id')
    leather_types = references.objects.filter(
        type=ReferenceType.LEATHER_VARIANT.value,
        IsDeleted=False,
    ).order_by('id')
    sole_types = references.objects.filter(
        type=ReferenceType.SOLE_VARIANT.value,
        IsDeleted=False,
    ).order_by('id')
    clients_list = clients.objects.filter(
        is_system=False,
        IsDeleted=False,
    ).order_by('name')

    filter_params = {k: v for k, v in request.GET.items() if k != 'page' and v}
    filter_query = urlencode(filter_params)

    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        "orders_list": page_obj,
        "statuses": statuses,
        "completed_status_id": completed_id.pk,
        "shoe_models": shoe_models,
        "colors": colors,
        "leather_types": leather_types,
        "sole_types": sole_types,
        "clients": clients_list,
        "filter_query": filter_query,
        "shoe_model_id": shoe_model_id,
        "color_id": color_id,
        "leather_type": leather_type_id,
        "solo_type": sole_type_id,
        "client_id": client_id,
        "status_id": status_id,
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
    order_lines_qs = Order_details.objects.filter(
        order_id=order_item.pk,
        IsDeleted=False,
    ).select_related(
        'model_id', 'quantity_type_id',
    ).prefetch_related(parts_prefetch).order_by('id')

    line_model = _safe_int(request.GET.get('line_model'))
    if line_model:
        order_lines_qs = order_lines_qs.filter(model_id_id=line_model)

    order_lines_page, order_lines_fq, order_lines_page_param = _paginate(request, order_lines_qs, 'page')

    context = {
        "order": order_item,
        "order_lines": order_lines_page,
        "order_lines_page_param": order_lines_page_param,
        "order_lines_filter_query": order_lines_fq,
        "shoe_models": shoe_model.objects.filter(IsDeleted=False).order_by('id'),
        "line_model": line_model,
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


def _order_details_for_producement():
    details_list = []
    details = Order_details.objects.filter(IsDeleted=False).select_related(
        'model_id', 'order_id', 'quantity_type_id',
    ).prefetch_related(
        Prefetch(
            'parts',
            queryset=Order_detail_parts.objects.filter(is_deleted=False).select_related(
                'material_stock__variant_ref_id',
                'material_stock__color_ref_id',
                'material_stock__material_type_ref_id',
                'model_part_definition__part_ref_id',
            ),
        ),
    ).order_by('id')

    for detail in details:
        parts_summary = []
        for part in detail.parts.all():
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
    return details_list


def _chain_sources_for_form(form):
    if 'producement_id' not in form.fields:
        return []
    return [
        {
            'id': p.id,
            'order_id': p.order_id_id,
            'order_detail_id': p.order_detail_id_id,
            'shoe_model_id': p.shoe_model_id_id,
        }
        for p in form.fields['producement_id'].queryset
        if p.order_id_id and p.order_detail_id_id and p.shoe_model_id_id
    ]


def _producement_form_context(form):
    return {
        'forms': form,
        'order_details': _order_details_for_producement(),
        'chain_sources': _chain_sources_for_form(form),
    }


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


def producement_view(request):
    professions = references.objects.filter(type=ReferenceType.PROFESSION.value, IsDeleted=False).order_by("order")

    base_qs = _producement_queryset_base()

    staff_list = staff.objects.filter(IsDeleted=False).order_by('id')
    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    statuses = references.objects.filter(IsDeleted=False, type=ReferenceType.STATUS.value).order_by('id')
    order_list = Orders.objects.filter(IsDeleted=False).order_by('id')

    staff_id = _safe_int(request.GET.get('staff_id'))
    model = _safe_int(request.GET.get('shoe_model_id'))
    status = _safe_int(request.GET.get('status'))
    order = _safe_int(request.GET.get('order'))

    if any([staff_id, model, status, order]):
        filter_kwargs = {
            'staff_id': staff_id,
            'shoe_model_id': model,
            'status': status,
            'order_id': order,
        }
        valid_filters = {k: v for k, v in filter_kwargs.items() if v is not None}
        base_qs = base_qs.filter(**valid_filters)

    profession_tabs = []
    for profession in professions:
        page_key = f'page_{profession.order}'
        qs = base_qs.filter(staff_id__profession_id=profession.id).order_by('id')
        page_obj = Paginator(qs, 10).get_page(request.GET.get(page_key, 1))
        tab_params = {
            k: v for k, v in request.GET.items()
            if v and k != page_key and not k.startswith('page_')
        }
        tab_params['active_tab'] = f'#profession-{profession.order}'
        profession_tabs.append({
            'profession': profession,
            'producement_list': page_obj,
            'page_key': page_key,
            'filter_query': urlencode(tab_params),
        })

    active_tab = request.GET.get("active_tab", "#profession-1")
    context = {
        "professions": professions,
        "profession_tabs": profession_tabs,
        "staff_list": staff_list,
        "shoe_models": shoe_models,
        "statuses": statuses,
        "order_list": order_list,
        "staff_id": staff_id,
        "shoe_model_id": model,
        "status": status,
        "order_id": order,
        "active_tab": active_tab,
    }
    return render(request, 'producement/producement.html', context=context)

def producement_create(request, ProducementForms=ProducementKroyForms):
    if request.method == "POST":
        form = ProducementForms(request.POST)
        if form.is_valid():
            producement.objects.create(**_producement_data_from_form(form))
            return redirect('producement_view')
    else:
        form = ProducementForms()
    return render(
        request,
        "producement/producement_create.html",
        _producement_form_context(form),
    )


def producement_read(request, pk):
    producement_item = _producement_queryset_base().get(pk=pk)
    return render(request, 'producement/producement_read.html', {
        "producement": producement_item,
    })


def producement_update(request, pk, ProducementForms):
    producement_item = producement.objects.get(pk=pk)

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

    context = _producement_form_context(form)
    context['producement'] = producement_item
    return render(request, "producement/producement_update.html", context)

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
    staff_id = _safe_int(request.GET.get('staff_id'))
    model_id = _safe_int(request.GET.get('shoe_model_id'))
    color_id = _safe_int(request.GET.get('color_id'))
    leather_id = _safe_int(request.GET.get('leather_type'))
    sole_id = _safe_int(request.GET.get('solo_type'))
    status = _safe_int(request.GET.get('status'))
    order_id = _safe_int(request.GET.get('order'))

    filters = {
        'warehouse__staff_id': staff_id,
        'warehouse__model_id': model_id,
        'warehouse__color_id': color_id,
        'warehouse__leather_type_id': leather_id,
        'warehouse__sole_type_id': sole_id,
        'status': status,
        'order_id': order_id,
        'IsDeleted': False,
    }
    valid_filters = {key: value for key, value in filters.items() if value is not None}

    sold_qs = Sales.objects.filter(**valid_filters).select_related(
        'client', 'warehouse', 'warehouse__model_id', 'warehouse__color_id',
        'warehouse__sole_type_id', 'warehouse__lining_type_id',
    ).order_by('id')

    sold_page, sold_fq, sold_page_param = _paginate(request, sold_qs, 'page')

    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    colors = references.objects.filter(IsDeleted=False, type=ReferenceType.COLOR.value).order_by('id')
    leather_types = references.objects.filter(IsDeleted=False, type=ReferenceType.LEATHER_TYPE.value).order_by('id')
    sole_types = references.objects.filter(IsDeleted=False, type=ReferenceType.SOLO_TYPE.value).order_by('id')
    client_list = clients.objects.filter(IsDeleted=False).order_by('id')

    context = {
        "sold_items": sold_page,
        "sold_page_param": sold_page_param,
        "sold_filter_query": sold_fq,
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
        "order_id": order_id,
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
                model_part_def_id = _safe_int(part.get("model_part_definition_id"))
                variant_id = _safe_int(part.get("material_variant_id"))
                if not model_part_def_id or not variant_id:
                    continue

                model_part = Model_part_definition.objects.get(id=model_part_def_id)

                order_qty = Decimal(new_order_detail.quantity)
                per_pair = model_part.quantity_per_pair
                waste = model_part.waste_percent

                required = order_qty * per_pair * (1 + waste / 100)

                color_id = _safe_int(part.get("color_id"))
                stock_filter = {
                    'material_type_ref_id': model_part.material_type_ref_id,
                    'variant_ref_id_id': variant_id,
                    'is_deleted': False,
                }
                if color_id:
                    stock_filter['color_ref_id_id'] = color_id
                else:
                    stock_filter['color_ref_id__isnull'] = True

                try:
                    stock = Material_stock.objects.get(**stock_filter)
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

                    stock.reserved_quantity += required
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


def _warehouse_line_materials(line):
    materials = {
        'color': '—',
        'leather': '—',
        'sole': '—',
        'lining': '—',
    }
    for part in line.parts.all():
        if part.is_deleted:
            continue
        stock = part.material_stock
        if stock.color_ref_id and materials['color'] == '—':
            materials['color'] = str(stock.color_ref_id)
        mt_value = stock.material_type_ref_id.value
        if mt_value == system_variables.LEATHER and materials['leather'] == '—':
            materials['leather'] = str(stock.variant_ref_id)
        elif mt_value == system_variables.SOLE and materials['sole'] == '—':
            materials['sole'] = str(stock.variant_ref_id)
        elif mt_value == system_variables.LINING and materials['lining'] == '—':
            materials['lining'] = str(stock.variant_ref_id)
    return materials


# warehouse
def _warehouse_order_details_queryset():
    """Stock rows come from order lines for the system OMBOR client."""
    parts_prefetch = Prefetch(
        'parts',
        queryset=Order_detail_parts.objects.filter(is_deleted=False).select_related(
            'material_stock__material_type_ref_id',
            'material_stock__variant_ref_id',
            'material_stock__color_ref_id',
        ),
    )
    return Order_details.objects.filter(
        IsDeleted=False,
        order_id__IsDeleted=False,
        order_id__client_id__name=system_variables.WAREHOUSE.upper(),
    ).select_related(
        'model_id', 'quantity_type_id', 'order_id', 'order_id__status',
    ).prefetch_related(parts_prefetch).order_by('-order_id__date', '-id')


def warehouse_view(request):
    model_id = _safe_int(request.GET.get('shoe_model_id'))
    color_id = _safe_int(request.GET.get('color_id'))
    leather_id = _safe_int(request.GET.get('leather_type'))
    sole_id = _safe_int(request.GET.get('solo_type'))
    status_id = _safe_int(request.GET.get('status'))
    order_id = _safe_int(request.GET.get('order'))

    details_qs = _warehouse_order_details_queryset()

    if model_id:
        details_qs = details_qs.filter(model_id_id=model_id)
    if status_id:
        details_qs = details_qs.filter(order_id__status_id=status_id)
    if order_id:
        details_qs = details_qs.filter(order_id_id=order_id)

    active_parts = Q(parts__is_deleted=False)

    if color_id:
        details_qs = details_qs.filter(
            active_parts,
            parts__material_stock__color_ref_id_id=color_id,
        )

    if leather_id:
        leather_material = references.objects.filter(
            type=ReferenceType.MATERIAL_TYPE.value,
            value=system_variables.LEATHER,
            IsDeleted=False,
        ).first()
        leather_filter = {'parts__material_stock__variant_ref_id_id': leather_id}
        if leather_material:
            leather_filter['parts__material_stock__material_type_ref_id_id'] = leather_material.id
        details_qs = details_qs.filter(active_parts, **leather_filter)

    if sole_id:
        sole_material = references.objects.filter(
            type=ReferenceType.MATERIAL_TYPE.value,
            value=system_variables.SOLE,
            IsDeleted=False,
        ).first()
        sole_filter = {'parts__material_stock__variant_ref_id_id': sole_id}
        if sole_material:
            sole_filter['parts__material_stock__material_type_ref_id_id'] = sole_material.id
        details_qs = details_qs.filter(active_parts, **sole_filter)

    if color_id or leather_id or sole_id:
        details_qs = details_qs.distinct()

    warehouse_page, warehouse_fq, warehouse_page_param = _paginate(request, details_qs, 'page')
    for line in warehouse_page:
        line.warehouse_materials = _warehouse_line_materials(line)

    shoe_models = shoe_model.objects.filter(IsDeleted=False).order_by('id')
    colors = references.objects.filter(
        IsDeleted=False, type=ReferenceType.COLOR.value,
    ).order_by('id')
    leather_types = references.objects.filter(
        IsDeleted=False, type=ReferenceType.LEATHER_VARIANT.value,
    ).order_by('id')
    sole_types = references.objects.filter(
        IsDeleted=False, type=ReferenceType.SOLE_VARIANT.value,
    ).order_by('id')
    statuses = references.objects.filter(
        type=ReferenceType.STATUS.value, IsDeleted=False,
    ).order_by('order')
    warehouse_orders = Orders.objects.filter(
        IsDeleted=False,
        client_id__name=system_variables.WAREHOUSE.upper(),
    ).order_by('-id')

    context = {
        "warehouse_items": warehouse_page,
        "warehouse_page_param": warehouse_page_param,
        "warehouse_filter_query": warehouse_fq,
        "shoe_models": shoe_models,
        "colors": colors,
        "leather_types": leather_types,
        "sole_types": sole_types,
        "statuses": statuses,
        "warehouse_orders": warehouse_orders,
        "shoe_model_id": model_id,
        "color_id": color_id,
        "leather_type": leather_id,
        "solo_type": sole_id,
        "status_id": status_id,
        "order_id": order_id,
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
def _stock_filter_variants(material_type_id=None):
    if material_type_id:
        try:
            material_type = references.objects.get(id=material_type_id, IsDeleted=False)
            ref_type = REFERENCE_MATERIAL_TYPE_VALUE_REFENRECE_TYPE_VALUE.get(material_type.value)
            if ref_type:
                return references.objects.filter(
                    type=ref_type, IsDeleted=False,
                ).order_by('order', 'value')
        except references.DoesNotExist:
            pass

    variant_ids = Material_stock.objects.filter(
        is_deleted=False,
    ).values_list('variant_ref_id_id', flat=True).distinct()
    return references.objects.filter(
        id__in=variant_ids, IsDeleted=False,
    ).order_by('value')


def material_stock_view(request):
    stocks_qs = Material_stock.objects.filter(is_deleted=False).select_related(
        'material_type_ref_id', 'variant_ref_id', 'color_ref_id', 'unit_ref_id',
    ).order_by('id')

    purchases_qs = Purchase.objects.filter(is_deleted=False).select_related(
        'supplier_id', 'status',
    ).prefetch_related(
        Prefetch(
            'purchase_id',
            queryset=Purchase_item.objects.filter(is_deleted=False).select_related(
                'material_id__material_type_ref_id',
                'material_id__variant_ref_id',
                'material_id__color_ref_id',
            ),
        ),
    ).order_by('-id')

    movements_qs = Stock_movement.objects.filter(is_deleted=False).select_related(
        'material__material_type_ref_id',
        'material__variant_ref_id',
        'material__color_ref_id',
        'material__unit_ref_id',
        'movement_type',
        'order',
        'order__client_id',
        'purchase',
        'purchase__supplier_id',
    ).order_by('-created_at', '-id')

    stock_material_type = _safe_int(request.GET.get('stock_material_type'))
    stock_variant = _safe_int(request.GET.get('stock_variant'))
    stock_color = _safe_int(request.GET.get('stock_color'))
    stock_unit = _safe_int(request.GET.get('stock_unit'))
    if stock_material_type:
        stocks_qs = stocks_qs.filter(material_type_ref_id_id=stock_material_type)
    if stock_variant:
        stocks_qs = stocks_qs.filter(variant_ref_id_id=stock_variant)
    if stock_color:
        stocks_qs = stocks_qs.filter(color_ref_id_id=stock_color)
    if stock_unit:
        stocks_qs = stocks_qs.filter(unit_ref_id_id=stock_unit)

    purchase_supplier = _safe_int(request.GET.get('purchase_supplier'))
    purchase_status = _safe_int(request.GET.get('purchase_status'))
    purchase_date = _safe_date(request.GET.get('purchase_date'))
    if purchase_supplier:
        purchases_qs = purchases_qs.filter(supplier_id_id=purchase_supplier)
    if purchase_status:
        purchases_qs = purchases_qs.filter(status_id=purchase_status)
    if purchase_date:
        purchases_qs = purchases_qs.filter(purchase_date=purchase_date)

    movement_type = _safe_int(request.GET.get('movement_type'))
    movement_material_type = _safe_int(request.GET.get('movement_material_type'))
    movement_order = _safe_int(request.GET.get('movement_order'))
    if movement_type:
        movements_qs = movements_qs.filter(movement_type_id=movement_type)
    if movement_material_type:
        movements_qs = movements_qs.filter(material__material_type_ref_id_id=movement_material_type)
    if movement_order:
        movements_qs = movements_qs.filter(order_id=movement_order)

    active_tab = request.GET.get('active_tab', '#stock-panel')

    stocks_page, stocks_fq, stocks_page_param = _paginate(
        request, stocks_qs, 'page_stock', {'active_tab': '#stock-panel'},
    )
    purchases_page, purchases_fq, purchases_page_param = _paginate(
        request, purchases_qs, 'page_purchases', {'active_tab': '#stock-panel'},
    )
    movements_page, movements_fq, movements_page_param = _paginate(
        request, movements_qs, 'page_movements', {'active_tab': '#movement-panel'},
    )

    context = {
        "stocks": stocks_page,
        "stocks_page_param": stocks_page_param,
        "stocks_filter_query": stocks_fq,
        "purchases": purchases_page,
        "purchases_page_param": purchases_page_param,
        "purchases_filter_query": purchases_fq,
        "movements": movements_page,
        "movements_page_param": movements_page_param,
        "movements_filter_query": movements_fq,
        "active_tab": active_tab,
        "material_types": references.objects.filter(
            type=ReferenceType.MATERIAL_TYPE.value, IsDeleted=False,
        ).order_by('order', 'value'),
        "colors": references.objects.filter(
            type=ReferenceType.COLOR.value, IsDeleted=False,
        ).order_by('order', 'value'),
        "units": references.objects.filter(
            type=ReferenceType.QUANTITY_TYPE.value, IsDeleted=False,
        ).order_by('order', 'value'),
        "stock_variants": _stock_filter_variants(stock_material_type),
        "movement_types": references.objects.filter(
            type=ReferenceType.STOCK_MOVEMENT_TYPE.value, IsDeleted=False,
        ).order_by('order', 'value'),
        "suppliers": Supplier.objects.filter(IsDeleted=False).order_by('name'),
        "purchase_statuses": references.objects.filter(
            type=ReferenceType.STATUS.value, IsDeleted=False,
        ).order_by('order', 'value'),
        "order_list": Orders.objects.filter(IsDeleted=False).order_by('-id'),
        "stock_material_type": stock_material_type,
        "stock_variant": stock_variant,
        "stock_color": stock_color,
        "stock_unit": stock_unit,
        "purchase_supplier": purchase_supplier,
        "purchase_status": purchase_status,
        "purchase_date": request.GET.get('purchase_date', ''),
        "movement_type": movement_type,
        "movement_material_type": movement_material_type,
        "movement_order": movement_order,
    }
    return render(request, 'material_stock/index.html', context=context)


def material_stock_read(request, pk):
    stock_item = get_object_or_404(
        Material_stock.objects.select_related(
            'material_type_ref_id', 'variant_ref_id', 'color_ref_id', 'unit_ref_id',
        ),
        pk=pk,
        is_deleted=False,
    )

    movements_qs = Stock_movement.objects.filter(
        material=stock_item,
        is_deleted=False,
    ).select_related(
        'movement_type',
        'order',
        'order__client_id',
        'purchase',
        'purchase__supplier_id',
    ).order_by('-created_at', '-id')

    movement_type = _safe_int(request.GET.get('movement_type'))
    movement_order = _safe_int(request.GET.get('movement_order'))
    movement_date = _safe_date(request.GET.get('movement_date'))
    if movement_type:
        movements_qs = movements_qs.filter(movement_type_id=movement_type)
    if movement_order:
        movements_qs = movements_qs.filter(order_id=movement_order)
    if movement_date:
        movements_qs = movements_qs.filter(created_at=movement_date)

    movements_page, movements_fq, movements_page_param = _paginate(request, movements_qs, 'page')

    context = {
        'stock': stock_item,
        'movements': movements_page,
        'movements_page_param': movements_page_param,
        'movements_filter_query': movements_fq,
        'movement_types': references.objects.filter(
            type=ReferenceType.STOCK_MOVEMENT_TYPE.value, IsDeleted=False,
        ).order_by('order', 'value'),
        'order_list': Orders.objects.filter(IsDeleted=False).order_by('-id'),
        'movement_type': movement_type,
        'movement_order': movement_order,
        'movement_date': request.GET.get('movement_date', ''),
    }
    return render(request, 'material_stock/read.html', context=context)


def stock_movement_create(request, pk=None):
    stock_item = None
    cancel_url = f"{reverse('material_stock_view')}?active_tab=%23movement-panel"
    if pk:
        stock_item = get_object_or_404(
            Material_stock.objects.select_related(
                'material_type_ref_id', 'variant_ref_id', 'color_ref_id', 'unit_ref_id',
            ),
            pk=pk,
            is_deleted=False,
        )
        cancel_url = reverse('material_stock_read', args=[pk])

    material_locked = stock_item is not None
    initial = {'material_id': stock_item} if stock_item else {}

    if request.method == 'POST':
        post_data = request.POST.copy()
        if material_locked and stock_item:
            post_data['material_id'] = stock_item.pk
        form = StockMovementForm(post_data, material_locked=material_locked, initial=initial)
        if form.is_valid():
            with transaction.atomic():
                material = Material_stock.objects.select_for_update().get(
                    pk=form.cleaned_data['material_id'].pk,
                )
                quantity = form.cleaned_data['quantity']
                movement_type = form.cleaned_data['movement_type_id']

                if movement_type.value == system_variables.STOCK_OUT and material.available_quantity < quantity:
                    form.add_error('quantity', system_variables.STOCK_MOVEMENT_OUT_ERROR)
                else:
                    if movement_type.value == system_variables.STOCK_IN:
                        material.stock_quantity += quantity
                    else:
                        material.stock_quantity -= quantity
                    material.save(update_fields=['stock_quantity'])

                    Stock_movement.objects.create(
                        material=material,
                        quantity=quantity,
                        movement_type=movement_type,
                        order=None,
                        purchase=None,
                        created_at=form.cleaned_data['movement_date'],
                    )

            if not form.errors:
                if stock_item:
                    return redirect('material_stock_read', pk=stock_item.pk)
                return redirect(f"{reverse('material_stock_view')}?active_tab=%23movement-panel")
    else:
        form = StockMovementForm(initial=initial, material_locked=material_locked)

    return render(request, 'material_stock/stock_movement_form.html', {
        'form': form,
        'cancel_url': cancel_url,
        'stock': stock_item,
    })


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
    if request.method == "POST":
        parsed = _parse_purchase_post(request.POST)
        if parsed is None:
            messages.error(request, system_variables.PURCHASE_VALIDATION)
        else:
            supplier_id, parsed_date, paid_amount, status_id, valid_items = parsed
            created_status = references.objects.get(value=system_variables.CREATED)
            status = references.objects.filter(pk=status_id, IsDeleted=False).first() if status_id else created_status
            with transaction.atomic():
                purchase = Purchase.objects.create(
                    supplier_id_id=supplier_id,
                    purchase_date=parsed_date,
                    total_amount=Decimal("0"),
                    paid_amount=paid_amount,
                    status=status or created_status,
                )
                total = _apply_purchase_items(purchase, valid_items)
                purchase.total_amount = total
                purchase.save(update_fields=["total_amount"])
            return redirect('material_stock_view')

    context = _purchase_form_context()
    context.update({
        "form_title": system_variables.PURCHASE_MATERIALS,
        "cancel_url": reverse('material_stock_view'),
        "initial_items": "[]",
    })
    return render(request, 'material_stock/purchase_form.html', context=context)


def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk, is_deleted=False)

    if request.method == "POST":
        parsed = _parse_purchase_post(request.POST)
        if parsed is None:
            messages.error(request, system_variables.PURCHASE_VALIDATION)
        elif not _can_reverse_purchase_items(purchase):
            messages.error(request, system_variables.PURCHASE_STOCK_REVERSE_ERROR)
        else:
            supplier_id, parsed_date, paid_amount, status_id, valid_items = parsed
            with transaction.atomic():
                _reverse_purchase_items(purchase)
                purchase.supplier_id_id = supplier_id
                purchase.purchase_date = parsed_date
                purchase.paid_amount = paid_amount
                if status_id:
                    status = references.objects.filter(
                        pk=status_id, type=ReferenceType.STATUS.value, IsDeleted=False,
                    ).first()
                    if status:
                        purchase.status = status
                purchase.total_amount = _apply_purchase_items(purchase, valid_items)
                purchase.save(update_fields=[
                    'supplier_id', 'purchase_date', 'paid_amount', 'status', 'total_amount',
                ])
            return redirect('material_stock_view')

    context = _purchase_form_context()
    context.update({
        "form_title": system_variables.PURCHASE_UPDATE,
        "cancel_url": reverse('material_stock_view'),
        "purchase": purchase,
        "initial_items": json.dumps(_purchase_items_as_dicts(purchase)),
    })
    return render(request, 'material_stock/purchase_form.html', context=context)


def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk, is_deleted=False)
    if not _can_reverse_purchase_items(purchase):
        messages.error(request, system_variables.PURCHASE_STOCK_REVERSE_ERROR)
        return redirect('material_stock_view')

    with transaction.atomic():
        _reverse_purchase_items(purchase)
        purchase.is_deleted = True
        purchase.save(update_fields=['is_deleted'])

    return redirect('material_stock_view')


def _parse_purchase_date(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ('%Y-%m-%d', '%d %m %Y'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_purchase_items_from_post(post):
    items = {}
    for key, value in post.items():
        if key.startswith("items["):
            idx = key.split("[")[1].split("]")[0]
            field = key.split("[")[2].split("]")[0]
            items.setdefault(idx, {})[field] = value
    return [
        it for it in items.values()
        if it.get("material_type") and it.get("variant")
        and it.get("unit") and it.get("quantity") and it.get("price")
    ]


def _parse_purchase_post(post):
    supplier_id = _safe_int(post.get("supplier_id"))
    parsed_date = _parse_purchase_date(post.get("purchase_date"))
    paid_amount_raw = post.get("paid_amount") or "0"
    status_id = _safe_int(post.get("status_id"))
    valid_items = _parse_purchase_items_from_post(post)

    if not supplier_id or not parsed_date or not valid_items:
        return None

    try:
        paid_amount = Decimal(str(paid_amount_raw))
    except (InvalidOperation, ValueError):
        paid_amount = Decimal("0")

    return supplier_id, parsed_date, paid_amount, status_id, valid_items


def _purchase_form_context():
    return {
        "material_types": references.objects.filter(
            type=ReferenceType.MATERIAL_TYPE.value, IsDeleted=False,
        ).order_by('order'),
        "colors": references.objects.filter(
            type=ReferenceType.COLOR.value, IsDeleted=False,
        ).order_by('id'),
        "units": references.objects.filter(
            type=ReferenceType.QUANTITY_TYPE.value, IsDeleted=False,
        ).order_by('id'),
        "suppliers": Supplier.objects.filter(IsDeleted=False).order_by('name'),
        "statuses": references.objects.filter(
            type=ReferenceType.STATUS.value, IsDeleted=False,
        ).order_by('order'),
    }


def _apply_purchase_items(purchase, valid_items):
    total = Decimal("0")
    for it in valid_items:
        quantity = Decimal(str(it["quantity"]))
        price = Decimal(str(it["price"]))
        amount = price * quantity
        total += amount

        color_id = it.get("color") or None
        if color_id == "":
            color_id = None

        stock, _ = Material_stock.objects.get_or_create(
            material_type_ref_id_id=it["material_type"],
            variant_ref_id_id=it["variant"],
            color_ref_id_id=color_id,
            unit_ref_id_id=it["unit"],
            is_deleted=False,
            defaults={
                "stock_quantity": Decimal("0"),
                "reserved_quantity": Decimal("0"),
            },
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
    return total


def _can_reverse_purchase_items(purchase):
    items = Purchase_item.objects.filter(
        purchase_id=purchase, is_deleted=False,
    ).select_related('material_id')
    for item in items:
        if item.material_id.stock_quantity < item.quantity:
            return False
    return True


def _reverse_purchase_items(purchase):
    items = Purchase_item.objects.filter(
        purchase_id=purchase, is_deleted=False,
    ).select_related('material_id')
    for item in items:
        stock = Material_stock.objects.select_for_update().get(pk=item.material_id_id)
        stock.stock_quantity -= item.quantity
        stock.save(update_fields=["stock_quantity"])
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])

    Stock_movement.objects.filter(purchase=purchase, is_deleted=False).update(is_deleted=True)


def _purchase_items_as_dicts(purchase):
    rows = []
    for item in Purchase_item.objects.filter(
        purchase_id=purchase, is_deleted=False,
    ).select_related(
        'material_id__material_type_ref_id',
        'material_id__variant_ref_id',
        'material_id__color_ref_id',
        'material_id__unit_ref_id',
    ):
        material = item.material_id
        rows.append({
            "material_type": material.material_type_ref_id_id,
            "variant": material.variant_ref_id_id,
            "color": material.color_ref_id_id or "",
            "unit": material.unit_ref_id_id,
            "quantity": str(item.quantity),
            "price": str(item.price),
        })
    return rows


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
            "available": float(stock.available_quantity),
            "reserved": float(stock.reserved_quantity),
        }
        payload.update(extra)
        if "required" in payload:
            payload["sufficient"] = stock.available_quantity >= Decimal(str(payload["required"]))
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