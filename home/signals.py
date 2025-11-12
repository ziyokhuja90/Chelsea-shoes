from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver
from .models import producement, staff, staff_payments, Order_details, orders, Warehouse, references, ReferenceType, clients
from config import system_variables


@receiver(post_save, sender=producement)
@receiver(post_delete, sender=producement)
def update_staff_balance_on_producement(sender, instance, **kwargs):
   
    staff_member = instance.staff_id

    completed_productions = producement.objects.filter(
        staff_id=staff_member, status__value="BAJARILDI", IsDeleted=False
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
        staff_id=staff_member, status__value="BAJARILDI", IsDeleted=False
    )
    total_price = sum(p.price * p.quantity for p in completed_productions)

    payments = staff_payments.objects.filter(staff_id=staff_member, IsDeleted=False)
    total_payments = sum(p.amount for p in payments)

    staff_member.balance = total_price - total_payments
    staff_member.save()

@receiver([post_save, post_delete], sender=Order_details)
def update_order_total_amount(sender, instance, **kwargs):
    order = orders.objects.get(pk=instance.order_id.pk)
    details = Order_details.objects.filter(order_id=order)
    total_amount = 0

    for i in details:
        total_amount += i.total_amount
    
    order.total_amount = total_amount
    order.save()


@receiver([post_save, post_delete], sender=orders)
def details_to_warehouse(sender, instance, **kwargs):
    print(f"--------------------------------------- {instance.status.value } ----------------------------------------------")
    if instance.status.value == system_variables.COMPLETED and instance.client_id.name == system_variables.WAREHOUSE.upper():
        print(f"--------------------------------------- {instance.status.value } ----------------------------------------------")
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
        references.objects.get_or_create(type=ReferenceType.GENDER.value, value="ERKAK", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.GENDER.value, value="AYOL", IsSystem=True)
        # status
        references.objects.get_or_create(type=ReferenceType.STATUS.value, value="YARATILDI", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.STATUS.value, value="JARAYONDA", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.STATUS.value, value="YAKUNLANDI", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.STATUS.value, value="BEKOR QILINDI", IsSystem=True)
        # profession
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value="KROY", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value="LAZIR", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value="ZAKATOP", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value="TUQUV", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.PROFESSION.value, value="KOSIB", IsSystem=True)
        # quantity_type
        references.objects.get_or_create(type=ReferenceType.QUANTITY_TYPE.value, value="JUFT", IsSystem=True)
        # currency
        references.objects.get_or_create(type=ReferenceType.CURRENCY.value, value="USD", IsSystem=True)
        references.objects.get_or_create(type=ReferenceType.CURRENCY.value, value="UZS", IsSystem=True)

        # sklad
        
        # clients.objects.get_or_create(name="SKLAD", phone_number=905647676, address="SKLAD", currency=references.objects.get(value="USD"), is_system=True)
        clients.objects.get_or_create(name="SKLAD", phone_number=905647676, address="SKLAD", currency=references.objects.get(value="UZS"), is_system=True)

