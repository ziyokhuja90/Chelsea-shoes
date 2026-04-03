from django.db import models
from enum import Enum
from django.utils.timezone import now
from config import system_variables

class ReferenceType(Enum):
    STATUS = 1               # system
    GENDER = 2               # system
    COLOR = 3
    PROFESSION = 4           # system
    QUANTITY_TYPE = 5        # system
    CURRENCY = 6             # system

    MODEL = 10
    MODEL_PART = 11

    MATERIAL_TYPE = 20       # system
    STOCK_MOVEMENT_TYPE = 21 # system

    # VARIANT TYPES (not materials!)

    LEATHER_VARIANT      = 30   # Teri
    SOLE_VARIANT         = 31   # Taglik (poshna / tag qismi)
    LINING_VARIANT       = 32   # Ichki qoplama (astarlik)
    GLUE_VARIANT         = 33   # Kley
    TEXTILE_VARIANT      = 34   # Matо / Tekstil

    THREAD_VARIANT       = 35   # Ip
    MIX_VARIANT          = 36   # Mix 
    BOX_VARIANT          = 37   # Quti (korobka)
    BUCKLE_VARIANT       = 38   # To‘qa
    ELASTIC_VARIANT      = 39   # Rezina
    RIVET_VARIANT        = 40   # Piston
    CARDBOARD_VARIANT    = 41   # Karton
    CLOTH_VARIANT        = 42   # Latta
    VISOR_VARIANT        = 43   # Ko‘zoynak soyaboni / Koziryok
    PAPER_VARIANT        = 44   # Qog‘oz
    STRETCH_VARIANT      = 45   # Cho‘ziluvchan mato
    FUR_VARIANT          = 46   # Mo‘yna
    ZIPPER_VARIANT       = 47   # Zamok
    SPONGE_VARIANT       = 48   # Gubka
    VELCRO_VARIANT       = 49   # Lipuchka (Velkro)


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
    value = models.CharField(max_length=255)
    IsDeleted = models.BooleanField(default=False)
    IsSystem = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = "references"
        
    def __str__(self):
        return self.value

class shoe_model(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255,unique=True)
    image = models.ImageField(upload_to="media/")
    description = models.TextField(verbose_name=system_variables.DESCRIPTION, null=True, blank=True)
    IsDeleted = models.BooleanField(default=False)

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
        on_delete=models.CASCADE, 
        related_name="currency_reference_client"
    )
    balance = models.DecimalField(max_digits=20 , decimal_places=2, default=0, null=True, blank=True)
    is_system = models.BooleanField(default=False)
    IsDeleted = models.BooleanField(default=False)
    class Meta:
        db_table = "clients"
        
    def __str__(self):
        return self.name

class client_payments(models.Model):
    client_id = models.ForeignKey(
        clients,
        on_delete=models.CASCADE,
        verbose_name="xaridor",
        related_name="client_id_clients"
        )
    date = models.DateField()
    amount = models.DecimalField(max_digits=20 , decimal_places=2)
    description = models.TextField(verbose_name=system_variables.DESCRIPTION, null=True, blank=True)
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "client_payments"
        
    def __str__(self):
        return f"{self.client_id} -- {self.amount}"

class Model_part_definition(models.Model):
    model_id = models.ForeignKey(shoe_model, on_delete=models.CASCADE, related_name="model_part_definition_shoe_model")
    part_ref_id = models.ForeignKey(references, on_delete=models.CASCADE, related_name="part_ref_id")
    material_type_ref_id = models.ForeignKey(references, on_delete=models.CASCADE, related_name="material_type_ref_id")
    is_required = models.BooleanField()
    unit_ref_id = models.ForeignKey(references, on_delete=models.CASCADE, related_name="unit_ref_id")
    quantity_per_pair = models.DecimalField(max_digits=10, decimal_places=2)
    waste_percent = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)

    class Meta: 
        db_table = "model_part_definition"

class Material_stock(models.Model):
    material_type_ref_id = models.ForeignKey(references, on_delete=models.CASCADE, related_name="material_type_ref_id_stock")
    variant_ref_id = models.ForeignKey(references, on_delete=models.CASCADE, related_name="variant_ref_id_stock")
    color_ref_id = models.ForeignKey(references, on_delete=models.CASCADE, related_name="color_ref_id_stock")
    unit_ref_id = models.ForeignKey(references, on_delete=models.CASCADE, related_name="unit_ref_id_stock")
    stock_quantity = models.IntegerField()
    reserved_quantity = models.IntegerField()
    available_quantity = models.IntegerField()
    updated_at = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta: 
        db_table = "material_stock"

class Supplier(models.Model):
    pass

class Purchase(models.Model):
    supplier_id = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplier_id")
    purchase_date = models.DateField()
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.ForeignKey(references, on_delete=models.CASCADE, related_name="purchase_status")
    created_at = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta: 
        db_table = "purchase"

class Purchase_item(models.Model):
    purchase_id = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="purchase_id")
    material_id = models.ForeignKey(Material_stock, on_delete=models.CASCADE, related_name="material_id_purchase_item")
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    
    class Meta: 
        db_table = "purchase_item"

class Orders(models.Model):
    client_id = models.ForeignKey(
        clients,
        on_delete=models.CASCADE,
        related_name="client_orders",
        verbose_name="xaridor"
    )
    date = models.DateField(verbose_name="Buyurtma sanasi", default=now)
    total_amount = models.DecimalField(verbose_name="buyurtma jami narxi" , max_digits=20 , decimal_places=2)
    complete_date = models.DateField(verbose_name="buyurtma topshirish sanasi")
    status = models.ForeignKey(
        references,
        models.CASCADE,
        related_name="status_orders",
        verbose_name="buyurtma xolati"
    )
    IsDeleted = models.BooleanField(default=False)
    IsSystem = models.BooleanField(default=False)
    
    class Meta:
        db_table = "orders"
        
    def __str__(self):
        return f"{self.client_id}"

class Order_details(models.Model):
    order_id = models.ForeignKey(
        Orders,
        models.CASCADE,
        related_name="order_id_orders"                                        
    )
    model_id = models.ForeignKey(
        to=shoe_model,
        on_delete=models.CASCADE,
        related_name="model_id_orders"
    )
    quantity = models.IntegerField()
    quantity_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="quantity_type_orders",
        verbose_name="buyurtma miqdor turi"
    )
    price = models.DecimalField(max_digits=20 , decimal_places=2)
    total_amount = models.DecimalField(max_digits=20 , decimal_places=2)

    IsDeleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = "Order_details"
        
    def __str__(self):
        return f"{self.model_id} -- {self.IsDeleted}"


class Stock_movement(models.Model):
    material = models.ForeignKey(
        Material_stock,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )
    quantity = models.IntegerField()
    movement_type = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )
    order = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )
    created_at = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta: 
        db_table = "stock_movement"

class Order_detail_parts(models.Model):
    order_detail = models.ForeignKey(
        Order_details,
        on_delete=models.CASCADE,
        related_name="parts"
    )
    model_part_definition = models.ForeignKey(
        Model_part_definition,
        on_delete=models.CASCADE,
        related_name="order_parts"
    )
    material_stock = models.ForeignKey(
        Material_stock,
        on_delete=models.CASCADE,
        related_name="order_parts"
    )
    quantity_required = models.IntegerField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "order_detail_parts"

class staff(models.Model):
    full_name = models.CharField(max_length=255 , verbose_name="xodim ismi")
    birth_date = models.DateField(verbose_name="xodim to'g'ilgan sanasi")
    gender = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="gender_reference",
        verbose_name="xodim jinsi"
    )
    entered_date = models.DateField(verbose_name="xodim ishga kirgan sanasi")
    profession = models.ForeignKey(
        references, 
        models.CASCADE,
        related_name="profession_reference",
        verbose_name="xodim kasbi"
    )
    phone_number = models.CharField(max_length=255 , verbose_name="xodim telefon raqami")
    balance = models.DecimalField(max_digits=20 , decimal_places=2, default=0, null=True, blank=True)
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "staff"
        
    def __str__(self):
        return f"{self.full_name} ({self.profession})"

class staff_payments(models.Model):
    staff_id = models.ForeignKey(
        staff,
        models.CASCADE,
        related_name='staff_id_staff',
        verbose_name="xodim"
    )
    date = models.DateField(verbose_name="tulov sanasi")
    amount = models.DecimalField(verbose_name="miqdori", max_digits=20 , decimal_places=2)
    description = models.TextField(verbose_name=system_variables.DESCRIPTION, null=True, blank=True)
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "staff_payments"
        
    def __str__(self):
        return f"{self.staff_id} -- {self.amount}"

class producement(models.Model):
    staff_id = models.ForeignKey(
        staff,
        models.CASCADE,
        related_name="staff_id_staff_producement",
        verbose_name="xodim"
    )
    shoe_model_id = models.ForeignKey(
        shoe_model,
        models.CASCADE,
        related_name="shoe_model_id_producement",
        verbose_name="ish modeli"
    )
    date = models.DateField(verbose_name="ish qo'shilgan sanasi")
    
    quantity = models.IntegerField(verbose_name="ish miqdori")
    quantity_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="quantity_type_producement",
        verbose_name="ish miqdor turi"
    )
    price = models.DecimalField(verbose_name="ish narxi" , max_digits=20 , decimal_places=2)
    order_id = models.ForeignKey(
        Orders,
        models.CASCADE,
        related_name="orders_producement",
        verbose_name="ish buyurtmasi",
        null=True,
        blank=True
    )
    status = models.ForeignKey(
        references,
        models.CASCADE,
        related_name="status_producement",
        verbose_name="ish xolati"
    )
    order_detail_id = models.ForeignKey(
        Order_details,
        models.CASCADE,
        related_name="order_detail_id_producement",
        verbose_name="Buyurma malumotlari",
        null=True,
        blank=True
    )
    IsDeleted = models.BooleanField(default=False)

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
        models.CASCADE,
        related_name="debts_currency",
        verbose_name="qarz pul birligi"
    )
    IsDeleted = models.BooleanField(default=False)
    class Meta:
        db_table = "debts"
        
    def __str__(self):
        return f"{self.debitor}"

class expenses(models.Model):
    date = models.DateField(verbose_name="xarajat sanasi")
    type = models.ForeignKey(
        references,
        models.CASCADE,
        related_name="type_expenses",
        verbose_name="xarajat turi"
    )
    description = models.TextField(verbose_name="xarajat tavsifi")
    amount = models.DecimalField(verbose_name="xarajat miqdori" , max_digits=20 , decimal_places=2)
    debt_id = models.ForeignKey(
        debts,
        models.CASCADE,
        related_name="debt_id_expenses",
        verbose_name="xarajat qarzi"
    )
    IsDeleted = models.BooleanField(default=False)
    class Meta:
        db_table = "expenses"
        
    def __str__(self):
        return f"{self.type}"

class Warehouse(models.Model):
    model_id = models.ForeignKey(
        to=shoe_model,
        on_delete=models.CASCADE,
        related_name="model_id_warehouse",
        verbose_name="buyurtma modeli"
    )
    quantity = models.IntegerField(verbose_name="buyurtma miqdori")
    quantity_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="quantity_type_warehouse",
        verbose_name="buyurtma miqdor turi"
    )
    price = models.DecimalField(max_digits=20 , decimal_places=2)
    total_amount = models.DecimalField(max_digits=20 , decimal_places=2)
    color_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="color_id_warehouse",
        verbose_name="buyurtma rangi"
    )

    leather_type = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="leather_type_warehouse",
        verbose_name="terisi"    
    )
    sole_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name='sole_type_warehouse',                
    )
    lining_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="lining_type_warehouse",
    )
    
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "warehouse"

    def __str__(self):
        return f"{self.model_id} - {self.quantity} - {self.total_amount}"

class Sales(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="warehouse_sales",
    )
    client = models.ForeignKey(
        clients,
        on_delete=models.CASCADE,
        related_name="client_sales",
    )
    price = models.DecimalField(max_digits=20, decimal_places=2)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField(default=now)
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "sales"
    
    def __str__(self):
        return f"{self.quantity} - {self.total_price}"

