from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver
from .models import producement, staff, staff_payments, Order_details, Orders, Warehouse, references, ReferenceType, clients, client_payments
from config import system_variables


@receiver(post_save, sender=Orders)
def update_producement_on_order_status(sender, instance, **kwargs):
    if instance.status.value == system_variables.CANCELED:
        producement_list = producement.objects.filter(order_id=instance)
        for i in producement_list:
            i.status = references.objects.get(value=system_variables.CANCELED)
            i.save()    

@receiver([post_delete, post_save], sender=producement)
def update_order_status_on_producement(sender, instance, **kwargs):
    order_id = instance.order_id
    if order_id.status.value == system_variables.CREATED:
        pending = references.objects.get(value=system_variables.ACTIVE)
        order_id.status = pending
        order_id.save()



@receiver([post_delete, post_save], sender=Orders)
@receiver([post_delete, post_save], sender=client_payments)
def update_client_balance_on_orders(sender, instance, **kwargs):
    
    client_member = instance.client_id

    completed_orders = Orders.objects.filter(
        client_id=client_member,
        status__value=system_variables.COMPLETED,
        IsDeleted=False
    )
    payments = client_payments.objects.filter(client_id=client_member, IsDeleted=False)

    total_orders = sum(o.total_amount for o in completed_orders)
    total_payments = sum(p.amount for p in payments)

    client_member.balance = total_payments - total_orders
    client_member.save()

@receiver(post_save, sender=producement)
@receiver(post_delete, sender=producement)
def update_staff_balance_on_producement(sender, instance, **kwargs):
   
    staff_member = instance.staff_id

    completed_productions = producement.objects.filter(
        staff_id=staff_member, status__value=system_variables.COMPLETED, IsDeleted=False
    )
    total_price = sum(p.price * p.quantity for p in completed_productions)

    payments = staff_payments.objects.filter(staff_id=staff_member, IsDeleted=False)
    total_payments = sum(p.amount for p in payments)



    staff_member.balance = total_price - total_payments
    staff_member.save()

@receiver(post_save, sender=staff_payments)
@receiver(post_delete, sender=staff_payments)
def update_staff_balance_on_payment(sender, instance, **kwargs):
   
    staff_member = instance.staff_id

    completed_productions = producement.objects.filter(
        staff_id=staff_member, status__value=system_variables.COMPLETED, IsDeleted=False
    )
    total_price = sum(p.price * p.quantity for p in completed_productions)

    payments = staff_payments.objects.filter(staff_id=staff_member, IsDeleted=False)
    total_payments = sum(p.amount for p in payments)

    staff_member.balance = total_price - total_payments
    staff_member.save()

@receiver([post_save, post_delete], sender=Order_details)
def update_order_total_amount(sender, instance, **kwargs):
    order = Orders.objects.get(pk=instance.order_id.pk)
    details = Order_details.objects.filter(order_id=order)
    total_amount = 0

    for i in details:
        total_amount += i.total_amount
    
    order.total_amount = total_amount
    order.save()


@receiver([post_save, post_delete], sender=Orders)
def details_to_warehouse(sender, instance, **kwargs):
    if instance.status.value == system_variables.COMPLETED and instance.client_id.name == system_variables.WAREHOUSE.upper():
        order_details = Order_details.objects.filter(order_id=instance, IsDeleted=False)

        for detail in order_details:
            Warehouse.objects.create(
                model_id=detail.model_id,
                quantity=detail.quantity,
                quantity_type_id=detail.quantity_type_id,
                price=detail.price,
                total_amount=detail.total_amount,
                color_id=detail.color_id,
                leather_type=detail.leather_type,
                sole_type_id=detail.sole_type_id,
                lining_type_id=detail.lining_type_id,
                IsDeleted=False
            )
    else:
        pass


@receiver(post_migrate)
def create_system_data(sender, **kwargs):
    if sender.name == "home":
        # gender
        references.objects.get_or_create(type=ReferenceType.GENDER.value, value=system_variables.MALE, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.GENDER.value, value=system_variables.FEMALE, IsSystem=True)
        # status
        references.objects.get_or_create(type=ReferenceType.STATUS.value, value=system_variables.CREATED, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.STATUS.value, value=system_variables.ACTIVE, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.STATUS.value, value=system_variables.COMPLETED, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.STATUS.value, value=system_variables.CANCELED, IsSystem=True)
        # profession
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value=system_variables.KROY, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value=system_variables.LAZIR, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value=system_variables.ZAKATOP, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value=system_variables.TUQUVCHI, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value=system_variables.KOSIB, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value=system_variables.QADOQLOVCHI, IsSystem=True)
        # quantity_type
        references.objects.get_or_create(type=ReferenceType.QUANTITY_TYPE.value, value=system_variables.COUPLE, IsSystem=True)
        # currency
        references.objects.get_or_create(type=ReferenceType.CURRENCY.value, value=system_variables.USD, IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.CURRENCY.value, value=system_variables.UZS, IsSystem=True)

        # sklad
        
        # clients.objects.get_or_create(name="SKLAD", phone_number=905647676, address="SKLAD", currency=references.objects.get(value="USD"), is_system=True)
        clients.objects.get_or_create(name=system_variables.WAREHOUSE.upper(), phone_number=905647676, address=system_variables.WAREHOUSE.upper(), currency=references.objects.get(value=system_variables.UZS), is_system=True)

