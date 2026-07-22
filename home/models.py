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
    MODEL_EXPENSES_TYPE = 22 # system

    # VARIANT TYPES (not materials!)

    LEATHER_VARIANT      = 30   # Teri
    SOLE_VARIANT         = 31   # Taglik (poshna / tag qismi)
    LINING_VARIANT       = 32   # Ichki qoplama (astarlik)
    GLUE_VARIANT         = 33   # Kley
    TEXTILE_VARIANT      = 34   # Mato / Tekstil

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


class references(models.Model):
    type = models.IntegerField(
        choices=[(ref_type.value, ref_type.name.title()) for ref_type in ReferenceType],
        verbose_name=system_variables.REFERENCE_TYPE,
    )
    value = models.CharField(max_length=255, verbose_name=system_variables.VALUE)
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)
    IsSystem = models.BooleanField(default=False, verbose_name=system_variables.IS_SYSTEM)
    order = models.IntegerField(default=0, verbose_name=system_variables.SORT_ORDER)

    class Meta:
        db_table = "references"

    def __str__(self):
        return self.value


class shoe_model(models.Model):
    name = models.CharField(max_length=255, verbose_name=system_variables.NAME)
    code = models.CharField(max_length=255, unique=True, verbose_name=system_variables.CODE)
    image = models.ImageField(upload_to="media/", verbose_name=system_variables.MODEL_IMAGE)
    description = models.TextField(
        verbose_name=system_variables.DESCRIPTION,
        null=True,
        blank=True,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "shoe_model"

    def __str__(self):
        return self.name


class clients(models.Model):
    name = models.CharField(max_length=255, verbose_name=system_variables.NAME)
    phone_number = models.CharField(max_length=255, verbose_name=system_variables.PHONE_NUMBER)
    address = models.CharField(max_length=255, verbose_name=system_variables.LOCATION)
    currency = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="currency_reference_client",
        verbose_name=system_variables.CURRENCY,
    )
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        verbose_name=system_variables.BALANCE,
    )
    is_system = models.BooleanField(default=False, verbose_name=system_variables.IS_SYSTEM)
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "clients"

    def __str__(self):
        return self.name


class client_payments(models.Model):
    client_id = models.ForeignKey(
        clients,
        on_delete=models.CASCADE,
        verbose_name=system_variables.CLIENT,
        related_name="client_id_clients",
    )
    date = models.DateField(verbose_name=system_variables.DATE)
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.AMOUNT,
    )
    description = models.TextField(
        verbose_name=system_variables.DESCRIPTION,
        null=True,
        blank=True,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "client_payments"

    def __str__(self):
        return f"{self.client_id} -- {self.amount}"


class Model_part_definition(models.Model):
    model_id = models.ForeignKey(
        shoe_model,
        on_delete=models.CASCADE,
        related_name="model_part_definition_shoe_model",
        verbose_name=system_variables.MODEL,
    )
    part_ref_id = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="part_ref_id",
        verbose_name=system_variables.MODEL_PART,
    )
    material_type_ref_id = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="material_type_ref_id",
        verbose_name=system_variables.MATERIAL_TYPE,
    )
    is_required = models.BooleanField(verbose_name=system_variables.REQUIRED)
    unit_ref_id = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="unit_ref_id",
        verbose_name=system_variables.UNIT,
    )
    quantity_per_pair = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=system_variables.QUANTITY_PER_PAIR,
    )
    waste_percent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=system_variables.WASTE_PERCENT,
    )
    is_deleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "model_part_definition"


class Model_expenses(models.Model):
    model_id = models.ForeignKey(
        shoe_model,
        on_delete=models.CASCADE,
        related_name="model_expenses",
        verbose_name=system_variables.MODEL,
    )
    profession_type = models.ForeignKey(
        references,  # PROFESSION — set only for ISH HAQI (labor) rows
        on_delete=models.CASCADE,
        related_name="profession_model_expenses",
        null=True,
        blank=True,
        verbose_name=system_variables.PROFESSION,
    )
    model_expenses_type = models.ForeignKey(
        references,  # MODEL_EXPENSES_TYPE
        on_delete=models.CASCADE,
        related_name="type_model_expenses",
        verbose_name=system_variables.EXPENSE_TYPE,
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.PRICE,
    )
    created_at = models.DateField(auto_now_add=True, verbose_name=system_variables.CREATED_AT)
    updated_at = models.DateField(auto_now=True, verbose_name=system_variables.UPDATED_AT)
    is_deleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "model_expenses"

    def __str__(self):
        return f"{self.model_id} - {self.model_expenses_type} - {self.price}"


class Material_stock(models.Model):
    material_type_ref_id = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="material_type_ref_id_stock",
        verbose_name=system_variables.MATERIAL_TYPE,
    )
    variant_ref_id = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="variant_ref_id_stock",
        verbose_name=system_variables.VARIANT_TYPE,
    )
    color_ref_id = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="color_ref_id_stock",
        null=True,
        blank=True,
        verbose_name=system_variables.COLOR,
    )
    unit_ref_id = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="unit_ref_id_stock",
        verbose_name=system_variables.UNIT,
    )
    stock_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=system_variables.STOCK_QUANTITY,
    )
    reserved_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=system_variables.RESERVED_QUANTITY,
    )
    updated_at = models.DateField(auto_now_add=True, verbose_name=system_variables.UPDATED_AT)
    is_deleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    @property
    def available_quantity(self):
        return self.stock_quantity - self.reserved_quantity

    class Meta:
        db_table = "material_stock"


class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name=system_variables.NAME)
    phone_number = models.CharField(max_length=255, verbose_name=system_variables.PHONE_NUMBER)
    address = models.CharField(max_length=255, verbose_name=system_variables.LOCATION)
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        verbose_name=system_variables.BALANCE,
    )
    is_system = models.BooleanField(default=False, verbose_name=system_variables.IS_SYSTEM)
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "supplier"

    def __str__(self):
        return self.name


class Purchase(models.Model):
    supplier_id = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="supplier_id",
        verbose_name=system_variables.SUPPLIER,
    )
    purchase_date = models.DateField(verbose_name=system_variables.PURCHASE_DATE)
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.TOTAL_AMOUNT,
    )
    paid_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.PAID_AMOUNT,
    )
    status = models.ForeignKey(
        references,
        on_delete=models.CASCADE,
        related_name="purchase_status",
        verbose_name=system_variables.STATUS,
    )
    created_at = models.DateField(auto_now_add=True, verbose_name=system_variables.CREATED_AT)
    is_deleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "purchase"


class Purchase_item(models.Model):
    purchase_id = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="purchase_id",
        verbose_name=system_variables.PURCHASE,
    )
    material_id = models.ForeignKey(
        Material_stock,
        on_delete=models.CASCADE,
        related_name="material_id_purchase_item",
        verbose_name=system_variables.MATERIAL_STOCK,
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=system_variables.QUANTITY,
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.PRICE,
    )
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.AMOUNT,
    )
    is_deleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "purchase_item"


class Orders(models.Model):
    client_id = models.ForeignKey(
        clients,
        on_delete=models.CASCADE,
        related_name="client_orders",
        verbose_name=system_variables.CLIENT,
    )
    date = models.DateField(verbose_name=system_variables.ORDER_DATE, default=now)
    total_amount = models.DecimalField(
        verbose_name=system_variables.TOTAL_AMOUNT,
        max_digits=20,
        decimal_places=2,
    )
    complete_date = models.DateField(verbose_name=system_variables.DEADLINE)
    status = models.ForeignKey(
        references,
        models.CASCADE,
        related_name="status_orders",
        verbose_name=system_variables.STATUS,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)
    IsSystem = models.BooleanField(default=False, verbose_name=system_variables.IS_SYSTEM)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f"{self.client_id}"

    def order_label(self):
        return f"{self.client_id} — {self.date.strftime('%Y-%m-%d')}"

    @property
    def is_warehouse_order(self):
        return self.client_id.name == system_variables.WAREHOUSE.upper()


class Order_details(models.Model):
    order_id = models.ForeignKey(
        Orders,
        models.CASCADE,
        related_name="order_id_orders",
        verbose_name=system_variables.ORDER,
    )
    model_id = models.ForeignKey(
        to=shoe_model,
        on_delete=models.CASCADE,
        related_name="model_id_orders",
        verbose_name=system_variables.MODEL,
    )
    quantity = models.IntegerField(verbose_name=system_variables.QUANTITY)
    quantity_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="quantity_type_orders",
        verbose_name=system_variables.QUANTITY_TYPE,
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.PRICE,
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.TOTAL_AMOUNT,
    )
    created_at = models.DateField(auto_now_add=True, verbose_name=system_variables.CREATED_AT)
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "Order_details"

    def __str__(self):
        return f"{self.model_id} -- {self.IsDeleted}"

    def stock_sold_quantity(self, exclude_sale_pk=None):
        qs = self.stock_sales.filter(IsDeleted=False)
        if exclude_sale_pk:
            qs = qs.exclude(pk=exclude_sale_pk)
        return qs.aggregate(total=models.Sum('quantity'))['total'] or 0

    def stock_remaining_quantity(self, exclude_sale_pk=None):
        return self.quantity - self.stock_sold_quantity(exclude_sale_pk)


class Stock_movement(models.Model):
    material = models.ForeignKey(
        Material_stock,
        on_delete=models.CASCADE,
        related_name="stock_movements",
        verbose_name=system_variables.MATERIAL_STOCK,
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=system_variables.QUANTITY,
    )
    movement_type = models.ForeignKey(
        references,  # KIRIM or CHIQIM
        on_delete=models.CASCADE,
        related_name="stock_movements",
        verbose_name=system_variables.MOVEMENT_TYPE,
    )
    order = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name="stock_movements",
        null=True,
        blank=True,
        verbose_name=system_variables.ORDER,
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="stock_movements",
        null=True,
        blank=True,
        verbose_name=system_variables.PURCHASE,
    )
    created_at = models.DateField(auto_now_add=True, verbose_name=system_variables.CREATED_AT)
    is_deleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "stock_movement"


class Order_detail_parts(models.Model):
    order_detail = models.ForeignKey(
        Order_details,
        on_delete=models.CASCADE,
        related_name="parts",
        verbose_name=system_variables.ORDER_DETAILS,
    )
    model_part_definition = models.ForeignKey(
        Model_part_definition,
        on_delete=models.CASCADE,
        related_name="order_parts",
        verbose_name=system_variables.MODEL_PART,
    )
    material_stock = models.ForeignKey(
        Material_stock,
        on_delete=models.CASCADE,
        related_name="order_parts",
        verbose_name=system_variables.MATERIAL_STOCK,
    )
    quantity_required = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=system_variables.QUANTITY_REQUIRED,
    )
    is_deleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "order_detail_parts"


class staff(models.Model):
    full_name = models.CharField(max_length=255, verbose_name=system_variables.NAME)
    birth_date = models.DateField(verbose_name=system_variables.BIRTH_DATE)
    gender = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="gender_reference",
        verbose_name=system_variables.GENDER,
    )
    entered_date = models.DateField(verbose_name=system_variables.ENTERED_DATE)
    profession = models.ForeignKey(
        references,
        models.CASCADE,
        related_name="profession_reference",
        verbose_name=system_variables.PROFESSION,
    )
    phone_number = models.CharField(max_length=255, verbose_name=system_variables.PHONE_NUMBER)
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        verbose_name=system_variables.BALANCE,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "staff"

    def __str__(self):
        return f"{self.full_name} ({self.profession})"


class staff_payments(models.Model):
    staff_id = models.ForeignKey(
        staff,
        models.CASCADE,
        related_name='staff_id_staff',
        verbose_name=system_variables.STAFF,
    )
    date = models.DateField(verbose_name=system_variables.DATE)
    amount = models.DecimalField(
        verbose_name=system_variables.AMOUNT,
        max_digits=20,
        decimal_places=2,
    )
    description = models.TextField(
        verbose_name=system_variables.DESCRIPTION,
        null=True,
        blank=True,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "staff_payments"

    def __str__(self):
        return f"{self.staff_id} -- {self.amount}"


class producement(models.Model):
    staff_id = models.ForeignKey(
        staff,
        models.CASCADE,
        related_name="staff_id_staff_producement",
        verbose_name=system_variables.STAFF,
    )
    shoe_model_id = models.ForeignKey(
        shoe_model,
        models.CASCADE,
        related_name="shoe_model_id_producement",
        verbose_name=system_variables.MODEL,
    )
    date = models.DateField(verbose_name=system_variables.WORK_DATE)
    quantity = models.IntegerField(verbose_name=system_variables.QUANTITY)
    quantity_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="quantity_type_producement",
        verbose_name=system_variables.QUANTITY_TYPE,
    )
    price = models.DecimalField(
        verbose_name=system_variables.PRICE,
        max_digits=20,
        decimal_places=2,
    )
    order_id = models.ForeignKey(
        Orders,
        models.CASCADE,
        related_name="orders_producement",
        verbose_name=system_variables.ORDER,
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        references,
        models.CASCADE,
        related_name="status_producement",
        verbose_name=system_variables.STATUS,
    )
    order_detail_id = models.ForeignKey(
        Order_details,
        models.CASCADE,
        related_name="order_detail_id_producement",
        verbose_name=system_variables.ORDER_DETAILS,
        null=True,
        blank=True,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "producement"

    def __str__(self):
        return f"{self.shoe_model_id}"


class debts(models.Model):
    debitor = models.CharField(max_length=255, verbose_name=system_variables.DEBITOR)
    description = models.TextField(verbose_name=system_variables.DESCRIPTION)
    date = models.DateField(verbose_name=system_variables.DATE)
    amount = models.DecimalField(
        verbose_name=system_variables.AMOUNT,
        max_digits=20,
        decimal_places=2,
    )
    balance = models.DecimalField(
        verbose_name=system_variables.REMAINING_BALANCE,
        max_digits=20,
        decimal_places=2,
    )
    currency = models.ForeignKey(
        references,
        models.CASCADE,
        related_name="debts_currency",
        verbose_name=system_variables.CURRENCY,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "debts"

    def __str__(self):
        return f"{self.debitor}"


class expenses(models.Model):
    date = models.DateField(verbose_name=system_variables.DATE)
    type = models.ForeignKey(
        references,
        models.CASCADE,
        related_name="type_expenses",
        verbose_name=system_variables.EXPENSE_TYPE,
    )
    description = models.TextField(verbose_name=system_variables.DESCRIPTION)
    amount = models.DecimalField(
        verbose_name=system_variables.AMOUNT,
        max_digits=20,
        decimal_places=2,
    )
    debt_id = models.ForeignKey(
        debts,
        models.CASCADE,
        related_name="debt_id_expenses",
        verbose_name=system_variables.DEBT,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "expenses"

    def __str__(self):
        return f"{self.type}"


class Warehouse(models.Model):
    model_id = models.ForeignKey(
        to=shoe_model,
        on_delete=models.CASCADE,
        related_name="model_id_warehouse",
        verbose_name=system_variables.MODEL,
    )
    quantity = models.IntegerField(verbose_name=system_variables.QUANTITY)
    quantity_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="quantity_type_warehouse",
        verbose_name=system_variables.QUANTITY_TYPE,
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.PRICE,
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.TOTAL_AMOUNT,
    )
    color_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="color_id_warehouse",
        verbose_name=system_variables.COLOR,
    )
    leather_type = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="leather_type_warehouse",
        verbose_name=system_variables.LEATHER_TYPE,
    )
    sole_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name='sole_type_warehouse',
        verbose_name=system_variables.SOLE_TYPE,
    )
    lining_type_id = models.ForeignKey(
        to=references,
        on_delete=models.CASCADE,
        related_name="lining_type_warehouse",
        verbose_name=system_variables.LINING_TYPE,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "warehouse"

    def __str__(self):
        return f"{self.model_id} - {self.quantity} - {self.total_amount}"


class Sales(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="warehouse_sales",
        verbose_name=system_variables.WAREHOUSE,
    )
    client = models.ForeignKey(
        clients,
        on_delete=models.CASCADE,
        related_name="client_sales",
        verbose_name=system_variables.CLIENT,
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.PRICE,
    )
    quantity = models.IntegerField(verbose_name=system_variables.QUANTITY)
    total_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.TOTAL_PRICE,
    )
    date = models.DateField(default=now, verbose_name=system_variables.DATE)
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "sales"

    def __str__(self):
        return f"{self.quantity} - {self.total_price}"


class Stock_sale(models.Model):
    """Sale of finished shoes from the OMBOR (warehouse) stock to a real client."""
    order_detail = models.ForeignKey(
        Order_details,
        on_delete=models.CASCADE,
        related_name="stock_sales",
        verbose_name=system_variables.WAREHOUSE,
    )
    client = models.ForeignKey(
        clients,
        on_delete=models.CASCADE,
        related_name="client_stock_sales",
        verbose_name=system_variables.CLIENT,
    )
    quantity = models.IntegerField(verbose_name=system_variables.QUANTITY)
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.PRICE,
    )
    total_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.TOTAL_PRICE,
    )
    date = models.DateField(default=now, verbose_name=system_variables.DATE)
    created_at = models.DateField(auto_now_add=True, verbose_name=system_variables.CREATED_AT)
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "stock_sale"

    def __str__(self):
        return f"{self.client} - {self.quantity} - {self.total_price}"


class SupplierPayments(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="supplier_payments",
        verbose_name=system_variables.SUPPLIER,
    )
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=system_variables.AMOUNT,
    )
    date = models.DateField(default=now, verbose_name=system_variables.DATE)
    description = models.TextField(
        verbose_name=system_variables.DESCRIPTION,
        null=True,
        blank=True,
    )
    IsDeleted = models.BooleanField(default=False, verbose_name=system_variables.IS_DELETED)

    class Meta:
        db_table = "supplier_payments"

    def __str__(self):
        return f"{self.supplier} - {self.amount} - {self.date}"
