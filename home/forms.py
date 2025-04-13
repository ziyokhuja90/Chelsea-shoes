from django import forms
from . import models
from django.utils.timezone import now
from datetime import datetime

from django.forms.widgets import DateInput

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
        model = models.orders
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

        self.fields['status'].initial = models.references.objects.get(value="YARATILDI")
        self.fields['status'].queryset = models.references.objects.filter(type=models.ReferenceType.STATUS.value)


class orderDetails_forms(forms.ModelForm):
    class Meta:
        model = models.Order_details
        fields = [ 
            'model_id', 'quantity', 'quantity_type_id',
            'price',  'color_id', 'leather_type', 
            'lining_type_id','sole_type_id'
            ]

        widgets = {
            'model_id':forms.Select(attrs={"class":"form-control"}),
            'quantity':forms.NumberInput(attrs={"class":"form-control"}),
            'quantity_type_id':forms.Select(attrs={"class":"form-control"}),
            'price':forms.NumberInput(attrs={"class":"form-control"}),
            'color_id':forms.Select(attrs={"class":"form-control"}),
            'leather_type':forms.Select(attrs={"class":"form-control"}),
            'sole_type_id':forms.Select(attrs={"class":"form-control"}),
            'lining_type_id':forms.Select(attrs={"class":"form-control"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['model_id'].queryset = models.shoe_model.objects.filter(IsDeleted=False)
        self.fields['quantity_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.QUANTITY_TYPE.value)
        self.fields['color_id'].queryset = models.references.objects.filter(type=models.ReferenceType.COLOR.value, IsDeleted=False)
        self.fields['leather_type'].queryset = models.references.objects.filter(type=models.ReferenceType.LEATHER_TYPE.value, IsDeleted=False)
        self.fields['lining_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.LINING_TYPE.value, IsDeleted=False)
        self.fields['sole_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.SOLO_TYPE.value, IsDeleted=False)

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
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "quantity_type_id": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "order_id": forms.Select(attrs={"class": "form-control"}),
            "order_detail_id": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "lining_type_id": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['status'].initial = models.references.objects.get(value="YARATILDI")
        self.fields['date'].initial = now()
        self.fields['date'].input_formats = ['%d %m %Y']



        self.fields['shoe_model_id'].queryset = models.shoe_model.objects.filter(IsDeleted=False)
        self.fields['quantity_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.QUANTITY_TYPE.value)
        self.fields['color_id'].queryset = models.references.objects.filter(type=models.ReferenceType.COLOR.value, IsDeleted=False)
        self.fields['leather_type'].queryset = models.references.objects.filter(type=models.ReferenceType.LEATHER_TYPE.value, IsDeleted=False)
        self.fields['solo_type'].queryset = models.references.objects.filter(type=models.ReferenceType.SOLO_TYPE.value, IsDeleted=False)
        self.fields['status'].queryset = models.references.objects.filter(type=models.ReferenceType.STATUS.value)
        self.fields['lining_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.LINING_TYPE.value)
        self.fields['order_id'].queryset = models.orders.objects.filter(IsDeleted=False)
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
        fields = ['staff_id', 'date', 'amount']
        
        widgets = {
            'staff_id':forms.Select(attrs={"class":"form-select"}),    
            'date': forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'
            ),
            'amount':forms.NumberInput(attrs={"class":"form-control"})    
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['date'].initial = now()
        self.fields['date'].input_formats = ['%d %m %Y']



class staff_payments_read_forms(forms.ModelForm):
    class Meta:
        model = models.staff_payments
        fields = ['date', 'amount']
        
        widgets = {
            'date': forms.DateInput(
                attrs={"class": "form-control datepicker", "placeholder": "dd mm yyyy"},
                format='%d %m %Y'
            ),
            'amount':forms.NumberInput(attrs={"class":"form-control"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial date value in the proper display format
        print("--------------------------------------------------")

        self.fields['date'].initial = now().strftime('%d %m %Y')
        self.fields['date'].input_formats = ['%d %m %Y']
