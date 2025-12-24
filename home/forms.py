from django import forms
from . import models
from django.utils.timezone import now
from datetime import datetime

from django.forms.widgets import DateInput
from config import system_variables
from django.db.models import Sum, Q, F
from collections import OrderedDict


class shoe_model_forms(forms.ModelForm):
    class Meta:
        model = models.shoe_model
        fields = ['name' , 'code', 'image' ,'description']
        
        widgets = {
            "name":forms.TextInput(attrs={"class":"form-control uppercase-input"}),
            "code":forms.TextInput(attrs={"class":"form-control uppercase-input"}),
            "image":forms.ClearableFileInput(attrs={
                "class":"form-control",

                }),    
            "description":forms.Textarea(attrs={"class":"form-control uppercase-input" }),    
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise forms.ValidationError("Ism 3tadan kam bo'lmasligi kerak")
        return name

class staff_forms(forms.ModelForm):
    class Meta:
        model = models.staff
        fields = ['full_name', 'birth_date', 'gender', 'entered_date', 'profession', 'phone_number']

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control uppercase-input"}),
            "birth_date": forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'
            ),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "entered_date": forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'
            ),
            "profession": forms.Select(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control",
                "id": "member_phone",
                "onkeyup": "backspacerUP(this, event)",
                "onkeydown": "backspacerDOWN(this, event)",
                "maxlength": "14",
                "placeholder": "(XX) XXX-XX-XX"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['birth_date'].input_formats = ['%d %m %Y']
        self.fields['entered_date'].input_formats = ['%d %m %Y']
        self.fields['entered_date'].initial = now()


        self.fields['gender'].queryset = models.references.objects.filter(
            type=models.ReferenceType.GENDER.value
        )
        self.fields['profession'].queryset = models.references.objects.filter(
            type=models.ReferenceType.PROFESSION.value,
            IsDeleted=False
        )
        self.fields['entered_date'].initial = now()

        if self.instance and self.instance.pk and self.instance.profession:
            self.fields['profession'].queryset = (
                self.fields['profession'].queryset |
                models.references.objects.filter(pk=self.instance.profession.pk)
            ).distinct()

class clients_forms(forms.ModelForm):
    class Meta:
        model = models.clients
        fields = ['name' , 'phone_number' , 'address' , 'currency']
        
        widgets = {
            'name':forms.TextInput(attrs={"class":"form-control uppercase-input"}),
            'phone_number':forms.TextInput(attrs={                
                "class": "form-control",
                "id":"member_phone",
                "onkeyup":"backspacerUP(this, event)",
                "onkeydown":"backspacerDOWN(this, event)",
                "maxlength":"14",
                "placeholder":"(XX) XXX-XX-XX"}),
            'address':forms.TextInput(attrs={"class":"form-control uppercase-input"}),
            'currency':forms.Select(attrs={"class": "form-control"})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['currency'].queryset = models.references.objects.filter(type=models.ReferenceType.CURRENCY.value)

class orders_forms(forms.ModelForm):
    class Meta:
        model = models.Orders
        fields = ['client_id' , 'date' , 'complete_date' , 'status']
        
        widgets = {
            'client_id':forms.Select(attrs={'class':'form-control'}),
            'date':forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'),
            'complete_date':forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'),
            'status':forms.Select(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['date'].initial = now()
        self.fields['date'].input_formats = ['%d %m %Y']
        self.fields['complete_date'].input_formats = ['%d %m %Y']

        self.fields['status'].initial = models.references.objects.get(value=system_variables.CREATED)
        self.fields['status'].queryset = models.references.objects.filter(type=models.ReferenceType.STATUS.value)
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        complete_date = cleaned_data.get('complete_date')

        if date and complete_date and complete_date < date:
            self.add_error(
                'complete_date',
                system_variables.ORDER_DATE_VALIDATION
            )

        return cleaned_data

class orderDetails_forms(forms.ModelForm):
    class Meta:
        model = models.Order_details
        fields = [ 
            'model_id', 'quantity', 'quantity_type_id',
            'price',  'color_id', 'leather_type', 
            'lining_type_id','sole_type_id', 'toqa'
            ]

        widgets = {
            'model_id':forms.Select(attrs={"class":"form-control"}),
            'quantity':forms.NumberInput(attrs={"class":"form-control", "min":0}),
            'quantity_type_id':forms.Select(attrs={"class":"form-control"}),
            'price':forms.NumberInput(attrs={"class":"form-control", "min":0}),
            'color_id':forms.Select(attrs={"class":"form-control"}),
            'leather_type':forms.Select(attrs={"class":"form-control"}),
            'sole_type_id':forms.Select(attrs={"class":"form-control"}),
            'lining_type_id':forms.Select(attrs={"class":"form-control"}),
            'toqa':forms.Select(attrs={"class":"form-control"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['model_id'].queryset = models.shoe_model.objects.filter(IsDeleted=False)
        self.fields['quantity_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.QUANTITY_TYPE.value)
        self.fields['color_id'].queryset = models.references.objects.filter(type=models.ReferenceType.COLOR.value, IsDeleted=False)
        self.fields['leather_type'].queryset = models.references.objects.filter(type=models.ReferenceType.LEATHER_TYPE.value, IsDeleted=False)
        self.fields['lining_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.LINING_TYPE.value, IsDeleted=False)
        self.fields['sole_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.SOLO_TYPE.value, IsDeleted=False)
        self.fields['toqa'].queryset = models.references.objects.filter(type=models.ReferenceType.TOQA.value, IsDeleted=False)

        if 'IsDeleted' in self.fields:
            del self.fields['IsDeleted']


        if self.instance and self.instance.pk and self.instance.color_id:
            self.fields['color_id'].queryset = (
                    self.fields['color_id'].queryset | models.references.objects.filter(
                pk=self.instance.color_id.pk)
            ).distinct()

        if self.instance and self.instance.pk and self.instance.leather_type:
            self.fields['leather_type'].queryset = (
                    self.fields['leather_type'].queryset | models.references.objects.filter(
                pk=self.instance.leather_type.pk)
            ).distinct()




class producement_forms(forms.ModelForm):
    class Meta:
        model = models.producement
        fields = [
            'order_id','order_detail_id', 'shoe_model_id', 
            'date','color_id', 'leather_type', 
            'solo_type','quantity', 'quantity_type_id', 
            'price','staff_id', 'status', 
            'lining_type_id'
        ]
        widgets = {
            "staff_id": forms.Select(attrs={'class': 'form-control'}),
            "shoe_model_id": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'
            ),
            "color_id": forms.Select(attrs={"class": "form-control"}),
            "leather_type": forms.Select(attrs={"class": "form-control"}),
            "solo_type": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min":0}),
            "quantity_type_id": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "min":0}),
            "order_id": forms.Select(attrs={"class": "form-control"}),
            "order_detail_id": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "lining_type_id": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['status'].initial = models.references.objects.get(value=system_variables.CREATED)
        self.fields['date'].initial = now()
        self.fields['date'].input_formats = ['%d %m %Y']



        self.fields['shoe_model_id'].queryset = models.shoe_model.objects.filter(IsDeleted=False)
        self.fields['quantity_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.QUANTITY_TYPE.value)
        self.fields['color_id'].queryset = models.references.objects.filter(type=models.ReferenceType.COLOR.value, IsDeleted=False)
        self.fields['leather_type'].queryset = models.references.objects.filter(type=models.ReferenceType.LEATHER_TYPE.value, IsDeleted=False)
        self.fields['solo_type'].queryset = models.references.objects.filter(type=models.ReferenceType.SOLO_TYPE.value, IsDeleted=False)
        self.fields['status'].queryset = models.references.objects.filter(type=models.ReferenceType.STATUS.value)
        self.fields['lining_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.LINING_TYPE.value)
        self.fields['order_id'].queryset = models.Orders.objects.filter(IsDeleted=False)
        self.fields['staff_id'].queryset = models.staff.objects.filter(IsDeleted=False)



        if self.instance and self.instance.pk and self.instance.color_id:
            self.fields['color_id'].queryset = (
                    self.fields['color_id'].queryset | models.references.objects.filter(
                pk=self.instance.color_id.pk)
            ).distinct()

        if self.instance and self.instance.pk and self.instance.leather_type:
            self.fields['leather_type'].queryset = (
                    self.fields['leather_type'].queryset | models.references.objects.filter(
                pk=self.instance.leather_type.pk)
            ).distinct()

        if self.instance and self.instance.pk and self.instance.solo_type:
            self.fields['solo_type'].queryset = (
                    self.fields['solo_type'].queryset | models.references.objects.filter(
                pk=self.instance.solo_type.pk)
            ).distinct()

        if self.instance and self.instance.pk and self.instance.lining_type_id:
            self.fields['lining_type_id'].queryset = (
                    self.fields['lining_type_id'].queryset | models.references.objects.filter(
                pk=self.instance.lining_type_id.pk)
            ).distinct()

class staff_payments_forms(forms.ModelForm):
    class Meta:
        model  = models.staff_payments
        fields = ['staff_id', 'date', 'amount', 'description']
        
        widgets = {
            'staff_id':forms.Select(attrs={"class":"form-select"}),    
            'date': forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'
            ),
            'amount':forms.NumberInput(attrs={"class":"form-control", "min":0}),
            'description':forms.Textarea(attrs={'class':'form-control'})   
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['date'].initial = now()
        self.fields['date'].input_formats = ['%d %m %Y']

        self.fields['staff_id'].queryset = models.staff.objects.filter(IsDeleted=False)

class staff_payments_read_forms(forms.ModelForm):
    class Meta:
        model = models.staff_payments
        fields = ['date', 'amount', 'description']
        
        widgets = {
            'date': forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'
            ),
            'amount':forms.NumberInput(attrs={"class":"form-control", "min":0}),
            'description':forms.Textarea(attrs={"class":"form-control"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial date value in the proper display format

        self.fields['date'].initial = now().strftime('%d %m %Y')
        self.fields['date'].input_formats = ['%d %m %Y']


class DefaultProducementForms(forms.Form):
    order_id = forms.ModelChoiceField(
        queryset=models.Orders.objects.filter(IsDeleted=False),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.ORDER,
        widget=forms.Select(
            attrs={'class':"form-select"}
        )
    )
    order_detail_id = forms.ModelChoiceField(
        queryset=models.Order_details.objects.filter(IsDeleted=False),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.ORDER_DETAILS,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))
    
    shoe_model_id = forms.ModelChoiceField(
        queryset=models.shoe_model.objects.filter(IsDeleted=False),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.MODEL,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))

    staff_id = None  # This will be set in the subclass

    color_id = forms.ModelChoiceField(
        queryset=models.references.objects.filter(
            type=models.ReferenceType.COLOR.value,
            IsDeleted=False
        ),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.COLOR,
        widget=forms.Select(
            attrs={'class':"form-select"}
        )
    )

    leather_type = forms.ModelChoiceField(
        queryset=models.references.objects.filter(
            type=models.ReferenceType.LEATHER_TYPE.value,
            IsDeleted=False
        ),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.LEATHER_TYPE,
        widget=forms.Select(
            attrs={'class':"form-select"}
        )
    )

    lining_type_id = forms.ModelChoiceField(
        queryset=models.references.objects.filter(
            type=models.ReferenceType.LINING_TYPE.value,
            IsDeleted=False
        ),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.LINING,
        widget=forms.Select(
            attrs={'class':"form-select"}
        )
    )

    quantity = forms.IntegerField(
        min_value=0,
        label=system_variables.QUANTITY,
        widget=forms.NumberInput(
            attrs={'class':"form-control"}
        )
    )
    quantity_type_id = forms.ModelChoiceField(
        queryset=models.references.objects.filter(
            type=models.ReferenceType.QUANTITY_TYPE.value,
            IsDeleted=False
        ),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.QUANTITY_TYPE,
        initial=models.references.objects.get(value=system_variables.COUPLE),
        widget=forms.Select(
            attrs={'class':"form-select"}
        )
    )
    price = forms.FloatField(
        min_value=0,
        label=system_variables.PRICE,
        widget=forms.NumberInput(
            attrs={'class':"form-control"}
        )
    )
    status = forms.ModelChoiceField(
        queryset=models.references.objects.filter(
            type=models.ReferenceType.STATUS.value,
            IsDeleted=False
        ),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.STATUS,
        initial=models.references.objects.get(value=system_variables.CREATED),
        widget=forms.Select(
            attrs={'class':"form-select"}
        )
    )

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control datepicker",
                "placeholder": "dd mm yyyy",
            },
            format='%d %m %Y'  # Display format
        ),
        label=system_variables.DATE,
        input_formats=['%d %m %Y'],  # Accepted input formats
        initial=now().strftime('%d %m %Y')  # Initial value
    )
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

        self.fields['order_id'].label_from_instance = lambda obj: (
            "SKLAT" if obj.client_id.name == system_variables.WAREHOUSE.upper() else f"Klient: {obj.client_id.name} - Sana: {obj.date.strftime('%d %m %Y')}"
        )
        # Now you can reorder inside the base form, because 'staff_id' exists
        fields = list(self.fields.items())
        reordered_fields = []
        for key, value in fields:
            reordered_fields.append((key, value))
            if key == 'shoe_model_id':
                reordered_fields.append(('staff_id', self.fields['staff_id']))
        if 'staff_id' not in dict(reordered_fields):
            reordered_fields.append(('staff_id', self.fields['staff_id']))
        self.fields = OrderedDict(reordered_fields)

        # Initialize instance variables to store selected Order_detail and existing quantity

        self.order_detail_instance = None  # Will store selected Order_detail instance
        self.existing_quantity = 0         # Will store quantity already used

    def clean(self):
        cleaned_data = super().clean()
        order_detail = cleaned_data.get('order_detail_id')
        quantity = cleaned_data.get('quantity')
        staff_id = cleaned_data.get('staff_id')


        if order_detail and quantity is not None:
            # if updating will not calculate the already stored data
            if self.instance:
                quantity -= self.instance.quantity
            # Save for potential use
            self.order_detail_instance = order_detail

            # Calculate total produced quantity for this Order_detail
            total_produced = models.producement.objects.filter(
                staff_id__profession=staff_id.profession,
                order_detail_id=order_detail,
                IsDeleted=False
            ).aggregate(total=Sum('quantity'))['total'] or 0

            self.existing_quantity = total_produced
            
            remaining_quantity = order_detail.quantity - total_produced

            if quantity > remaining_quantity:
                self.add_error(
                    'quantity',
                    f"{system_variables.MAX_ALLOWED_Q} — {remaining_quantity}. "
                    f"{system_variables.ALREADY_PRODUCED}: {total_produced}, {system_variables.ORDERED}: {order_detail.quantity}"
                )

        return cleaned_data

class ProducementKroyForms(DefaultProducementForms):
    staff_id = forms.ModelChoiceField(
        queryset=models.staff.objects.filter(profession__value=system_variables.KROY, IsDeleted=False),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.STAFF,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['order_id'].label_from_instance = lambda obj: (
            "SKLAT" if obj.client_id.name == system_variables.WAREHOUSE.upper() else f"Klient: {obj.client_id.name} - Sana: {obj.date.strftime('%d %m %Y')}"
        )
    
    

  # Custom label for order field

    # def get_order_label(self, order):
    #     # Include the order details in the label
    #     details = order.ordeer_id_orders.all()  # Use related_name
    #     details_text = "; ".join(
    #         f"Model: {detail.model_id} | Qty: {detail.quantity} | Color: {detail.color_id}" 
    #         for detail in details
    #     )
    #     # Return a label combining order and related details
    #     return f"Order #{order.id} - Client: {order.client_id} - Details: [{details_text}]"

class ProducementLazirForms(DefaultProducementForms):
    
    staff_id = forms.ModelChoiceField(
        queryset=models.staff.objects.filter(profession__value=system_variables.LAZIR ,IsDeleted=False),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.STAFF,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))

class ProducementZakatopForms(DefaultProducementForms):

    staff_id = forms.ModelChoiceField(
        queryset=models.staff.objects.filter(profession__value=system_variables.ZAKATOP ,IsDeleted=False),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.STAFF,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))
 
class ProducementTuquvchiForms(DefaultProducementForms):
    staff_id = forms.ModelChoiceField(
        queryset=models.staff.objects.filter(profession__value=system_variables.TUQUVCHI ,IsDeleted=False),
        empty_label= system_variables.EMPTY_LABEL,
        label=system_variables.STAFF,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))

class ProducementKosibForms(DefaultProducementForms):
    staff_id = forms.ModelChoiceField(
        queryset=models.staff.objects.filter(profession__value=system_variables.KOSIB ,IsDeleted=False), 
        empty_label= system_variables.EMPTY_LABEL ,
        label=system_variables.STAFF,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))
    sole_type_id = forms.ModelChoiceField(
        queryset=models.references.objects.filter(
            type=models.ReferenceType.SOLO_TYPE.value,
            IsDeleted=False),
        empty_label= system_variables.EMPTY_LABEL ,
        label=system_variables.SOLE_TYPE,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))
    
class ProducementUpakovkachiForms(DefaultProducementForms):
    staff_id = forms.ModelChoiceField(
        queryset=models.staff.objects.filter(profession__value=system_variables.QADOQLOVCHI ,IsDeleted=False), 
        empty_label= system_variables.EMPTY_LABEL ,
        label=system_variables.STAFF,
        widget=forms.Select(
            attrs={'class':"form-select"}
        ))


class SalesForm(forms.ModelForm):
    class Meta:
        model = models.Sales
        fields = ['warehouse', 'client', 'date', 'price', 'quantity']

        widgets = {
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'date':forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['warehouse'].queryset = models.Warehouse.objects.filter(IsDeleted=False)
        self.fields['client'].queryset = models.clients.objects.filter(IsDeleted=False)
        self.fields['date'].initial = now()
        self.fields['date'].input_formats = ['%d %m %Y']


class Client_payments_forms(forms.ModelForm):
    class Meta:
        model  = models.client_payments
        fields = ['client_id', 'date', 'amount', 'description']
        
        widgets = {
            'client_id':forms.Select(attrs={"class":"form-select"}),    
            'date': forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'
            ),
            'amount':forms.NumberInput(attrs={"class":"form-control", "min":0}),
            'description':forms.Textarea(attrs={'class':'form-control'})   
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['date'].initial = now()
        self.fields['date'].input_formats = ['%d %m %Y']

        self.fields['client_id'].queryset = models.clients.objects.filter(IsDeleted=False)
