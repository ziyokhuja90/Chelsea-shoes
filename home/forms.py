from django import forms
from . import models


class shoe_model_forms(forms.ModelForm):
    class Meta:
        model = models.shoe_model
        fields = ['name' , 'code', 'image' ,'description']
        
        widgets = {
            "name":forms.TextInput(attrs={"class":"form-control"}),
            "code":forms.TextInput(attrs={"class":"form-control"}),
            "image":forms.ClearableFileInput(attrs={"class":"form-control"}),    
            "description":forms.Textarea(attrs={"class":"form-control"}),    
        }

class staff_forms(forms.ModelForm):
    class Meta:
        model = models.staff
        fields = ['full_name', 'birth_date', 'gender', 'entered_date', 'profession', 'phone_number']

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "entered_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "profession": forms.Select(attrs={"class": "form-control"}),
            "phone_number": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter gender options
        self.fields['gender'].queryset = models.references.objects.filter(type=models.ReferenceType.GENDER.value)
        
        # Filter profession options
        self.fields['profession'].queryset = models.references.objects.filter(type=models.ReferenceType.PROFESSION.value)

class clients_forms(forms.ModelForm):
    class Meta:
        model = models.clients
        fields = ['name' , 'phone_number' , 'address' , 'currency']
        
        widgets = {
            'name':forms.TextInput(attrs={"class":"form-control"}),
            'phone_number':forms.TextInput(attrs={"class":"form-control"}),
            'address':forms.TextInput(attrs={"class":"form-control"}),
            'currency':forms.Select(attrs={"class": "form-control"})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['currency'].queryset = models.references.objects.filter(type=models.ReferenceType.CURRENCY.value)

class orders_forms(forms.ModelForm):
    class Meta:
        model = models.orders
        fields = ['client_id' , 'date' , 'model_id' , 'quantity' , 'quantity_type_id' , 'price' , 'color_id' , 'leather_id' , 'complete_date' , 'status']
        
        widgets = {
            'client_id':forms.Select(attrs={'class':'form-control'}),
            'date':forms.DateInput(attrs={'class':'form-control' , "type":"date"}),
            'model_id':forms.Select(attrs={'class':'form-control'}),
            'quantity':forms.NumberInput(attrs={'class':'form-control'}),
            'quantity_type_id':forms.Select(attrs={'class':'form-control'}),
            'price':forms.NumberInput(attrs={'class':'form-control'}),
            'color_id':forms.Select(attrs={'class':'form-control'}),
            'leather_id':forms.Select(attrs={'class':'form-control'}),
            'complete_date':forms.DateInput(attrs={'class':'form-control' , "type":"date"}),
            'status':forms.Select(attrs={'class':'form-control'}),
            
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['quantity_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.QUANTITY_TYPE.value)
        self.fields['color_id'].queryset = models.references.objects.filter(type=models.ReferenceType.COLOR.value)
        self.fields['leather_id'].queryset = models.references.objects.filter(type=models.ReferenceType.LEATHER_TYPE.value)
        self.fields['status'].queryset = models.references.objects.filter(type=models.ReferenceType.STATUS.value)
        
class producement_forms(forms.ModelForm):
    class Meta:
        model = models.producement
        fields = [
            'staff_id', 'shoe_model_id', 'date',
            'color_id', 'leather_type', 'solo_type',
            'quantity', 'quantity_type_id', 'price',
            'order_id', 'status'
        ]
        widgets = {
            "staff_id": forms.Select(attrs={'class': 'form-control'}),
            "shoe_model_id": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "color_id": forms.Select(attrs={"class": "form-control"}),
            "leather_type": forms.Select(attrs={"class": "form-control"}),
            "solo_type": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "quantity_type_id": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "order_id": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['quantity_type_id'].queryset = models.references.objects.filter(type=models.ReferenceType.QUANTITY_TYPE.value)
        self.fields['color_id'].queryset = models.references.objects.filter(type=models.ReferenceType.COLOR.value)
        self.fields['leather_type'].queryset = models.references.objects.filter(type=models.ReferenceType.LEATHER_TYPE.value)
        self.fields['solo_type'].queryset = models.references.objects.filter(type=models.ReferenceType.SOLO_TYPE.value)
        self.fields['status'].queryset = models.references.objects.filter(type=models.ReferenceType.STATUS.value)
