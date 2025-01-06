from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import producement, staff, staff_payments

@receiver(post_save, sender=producement)
@receiver(post_delete, sender=producement)
def update_staff_balance_on_producement(sender, instance, **kwargs):
    """
    Update staff balance when a producement is created, updated, or deleted.
    """
    staff_member = instance.staff_id

    # Recalculate balance
    completed_productions = producement.objects.filter(
        staff_id=staff_member, status__value="Bajarildi"
    )
    total_price = sum(p.price * p.quantity for p in completed_productions)

    # Update staff balance
    payments = staff_payments.objects.filter(staff_id=staff_member)
    total_payments = sum(p.amount for p in payments)

    # Update the staff's balance
    staff_member.balance = total_price - total_payments
    staff_member.save()

@receiver(post_save, sender=staff_payments)
@receiver(post_delete, sender=staff_payments)
def update_staff_balance_on_payment(sender, instance, **kwargs):
    """
    Update staff balance when a payment is created, updated, or deleted.
    """
    staff_member = instance.staff_id

    # Recalculate balance
    completed_productions = producement.objects.filter(
        staff_id=staff_member, status__value="Bajarildi"
    )
    total_price = sum(p.price * p.quantity for p in completed_productions)

    # Update staff balance
    payments = staff_payments.objects.filter(staff_id=staff_member)
    total_payments = sum(p.amount for p in payments)

    # Update the staff's balance
    staff_member.balance = total_price - total_payments
    staff_member.save()
