from django.db import models
from enum import Enum

class ReferenceType(Enum):
    STATUS = 1
    GENDER = 2
    COLOR = 3
    LEATHER_TYPE = 4
    PROFESSION = 5
    QUANTITY_TYPE = 6
    CURRENCY = 7
    
class StatusType(Enum):
    Created = 0
    Active = 1
    Completed = 2
    Cancelled = 3
    Deleted = 4
    

# Create your models here.
class references(models.Model):
    type = models.IntegerField(
        choices=[(ref_type.value, ref_type.name.title()) for ref_type in ReferenceType],
        verbose_name="Reference Type"
    )
    value = models.CharField(max_length=255 , verbose_name="ma'lumotnoma qiymati")
    IsDeleted = models.BooleanField(default=False)
    IsSystem = models.BooleanField(default=False)
    
    class Meta:
        db_table = "references"
        
    def __str__(self):
        return self.value

class shoe_model(models.Model):
    name = models.CharField(max_length=255 , verbose_name="oyoq kiyim nomi")
    code = models.CharField(max_length=255 , verbose_name="oyoq kiyim kodi" ,unique=True)
    image = models.ImageField(upload_to="media/" , verbose_name="oyoq kiyim rasmi")
    description = models.TextField(verbose_name="oyoq kiyim tavsifi")
    
    class Meta:
        db_table = "shoe_model"
        
    def __str__(self):
        return self.name

class clients(models.Model):
    name = models.CharField(max_length=255 , verbose_name="xaridor ismi")
    phone_number = models.CharField(max_length=255 , verbose_name="xaridor telefon raqami")
    address = models.CharField(max_length=255 , verbose_name="xaridor manzili")
    currency = models.ForeignKey(
        references,
        on_delete=models.DO_NOTHING, 
        related_name="currency_reference_client"
    )
    class Meta:
        db_table = "clients"
        
    def __str__(self):
        return self.name

class client_payments(models.Model):
    client_id = models.ForeignKey(
        clients,
        on_delete=models.DO_NOTHING,
        verbose_name="xaridor",
        related_name="client_id_clients"
        )
    date = models.DateField(verbose_name="tulov sanasi")
    amount = models.DecimalField(verbose_name="miqdori" , max_digits=20 , decimal_places=2)
    
    class Meta:
        db_table = "client_payments"
        
    def __str__(self):
        return f"{self.client_id} -- {self.amount}"

class orders(models.Model):
    client_id = models.ForeignKey(
        clients,
        on_delete=models.DO_NOTHING,
        related_name="client_orders",
        verbose_name="xaridor"
    )
    date = models.DateField(verbose_name="Buyurtma sanasi")
    model_id = models.ForeignKey(
        to=shoe_model,
        on_delete=models.DO_NOTHING,
        related_name="model_id_orders",
        verbose_name="buyurtma modeli"
    )
    quantity = models.IntegerField(verbose_name="buyurtma miqdori")
    quantity_type_id = models.ForeignKey(
        to=references,
        on_delete=models.DO_NOTHING,
        related_name="quantity_type_orders",
        verbose_name="buyurtma miqdor turi"
    )
    price = models.DecimalField(verbose_name="buyurtma narxi" , max_digits=20 , decimal_places=2)
    total_amount = models.DecimalField(verbose_name="buyurtma jami narxi" , max_digits=20 , decimal_places=2)
    color_id = models.ForeignKey(
        to=references,
        on_delete=models.DO_NOTHING,
        related_name="color_id_orders",
        verbose_name="buyurtma rangi"
    )
    leather_id = models.ForeignKey(
        to=references,
        on_delete=models.DO_NOTHING,
        related_name="leather_id_reference",
        verbose_name="terisi"    
    )
    
    complete_date = models.DateField(verbose_name="buyurtma topshirish sanasi")
    status = models.ForeignKey(
        references,
        models.DO_NOTHING,
        related_name="status_orders",
        verbose_name="buyurtma xolati"
    )
    
    class Meta:
        db_table = "orders"
        
    def __str__(self):
        return f"{self.model_id}"

class staff(models.Model):
    full_name = models.CharField(max_length=255 , verbose_name="xodim ismi")
    birth_date = models.DateField(verbose_name="xodim to'g'ilgan sanasi")
    gender = models.ForeignKey(
        to=references,
        on_delete=models.DO_NOTHING,
        related_name="gender_reference",
        verbose_name="xodim jinsi"
    )
    entered_date = models.DateField(verbose_name="xodim ishga kirgan sanasi")
    profession = models.ForeignKey(
        references, 
        models.DO_NOTHING,
        related_name="profession_reference",
        verbose_name="xodim kasbi"
    )
    phone_number = models.CharField(max_length=255 , verbose_name="xodim telefon raqami")
    
    class Meta:
        db_table = "staff"
        
    def __str__(self):
        return f"{self.full_name} -- {self.profession}"

class staff_payments(models.Model):
    staff_id = models.ForeignKey(
        staff,
        models.DO_NOTHING,
        related_name='staff_id_staff',
        verbose_name="xodim"
    )
    date = models.DateField(verbose_name="tulov sanasi")
    amount = models.DecimalField(verbose_name="miqdori" , max_digits=20 , decimal_places=2)
    
    class Meta:
        db_table = "staff_payments"
        
    def __str__(self):
        return f"{self.staff_id} -- {self.amount}"

class producement(models.Model):
    staff_id = models.ForeignKey(
        staff,
        models.DO_NOTHING,
        related_name="staff_id_staff_producement",
        verbose_name="xodim"
    )
    shoe_model_id = models.ForeignKey(
        shoe_model,
        models.DO_NOTHING,
        related_name="shoe_model_id_producement",
        verbose_name="ish modeli"
    )
    date = models.DateField(verbose_name="ish qo'shilgan sanasi")
    color_id = models.ForeignKey(
        to=references,
        on_delete=models.DO_NOTHING,
        related_name="color_id_producement",
        verbose_name="ish rangi"
    )
    leather_type = models.ForeignKey(
        to=references,
        on_delete=models.DO_NOTHING,
        related_name="leather_type_reference",
        verbose_name="terisi"    
    )
    solo_type = models.ForeignKey(
        to=references,
        on_delete=models.DO_NOTHING,
        related_name="solo_type_reference",
        verbose_name="tagliki"    
    )
    quantity = models.IntegerField(verbose_name="ish miqdori")
    quantity_type_id = models.ForeignKey(
        to=references,
        on_delete=models.DO_NOTHING,
        related_name="quantity_type_producement",
        verbose_name="ish miqdor turi"
    )
    price = models.DecimalField(verbose_name="ish narxi" , max_digits=20 , decimal_places=2)
    order_id = models.ForeignKey(
        orders,
        models.DO_NOTHING,
        related_name="orders_producement",
        verbose_name="ish buyurtmasi",
        null=True,
        blank=True
    )
    status = models.ForeignKey(
        references,
        models.DO_NOTHING,
        related_name="status_producement",
        verbose_name="ish xolati"
    )
    
    class Meta:
        db_table = "producement"
        
    def __str__(self):
        return f"{self.shoe_model_id}"

class debts(models.Model):
    debitor = models.CharField(max_length=255 , verbose_name="qarzdor")
    description = models.TextField(verbose_name="qarz tavsifi")
    date = models.DateField(verbose_name="qarz sanasi")
    amount = models.DecimalField(verbose_name="miqdori" , max_digits=20 , decimal_places=2)
    balance = models.DecimalField(verbose_name="qoldiq" , max_digits=20 , decimal_places=2)
    currency = models.ForeignKey(
        references,
        models.DO_NOTHING,
        related_name="debts_currency",
        verbose_name="qarz pul birligi"
    )
    class Meta:
        db_table = "debts"
        
    def __str__(self):
        return f"{self.debitor}"

class expenses(models.Model):
    date = models.DateField(verbose_name="xarajat sanasi")
    type = models.ForeignKey(
        references,
        models.DO_NOTHING,
        related_name="type_expenses",
        verbose_name="xarajat turi"
    )
    description = models.TextField(verbose_name="xarajat tavsifi")
    amount = models.DecimalField(verbose_name="xarajat miqdori" , max_digits=20 , decimal_places=2)
    debt_id = models.ForeignKey(
        debts,
        models.DO_NOTHING,
        related_name="debt_id_expenses",
        verbose_name="xarajat qarzi"
    )
    class Meta:
        db_table = "expenses"
        
    def __str__(self):
        return f"{self.type}"
    