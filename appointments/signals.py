from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment

@receiver(post_save, sender=Appointment)
@receiver(post_save, sender=Appointment)
def send_appointment_notification(sender, instance, created, **kwargs):

    if instance.status == 'Confirmed':
        print(f"--- SMS NOTIFICATION SENT TO {instance.patient.phone_number} ---")
        print(f"Message: Hello {instance.patient.user.first_name}, your appointment with "
              f"Dr. {instance.doctor.last_name} is CONFIRMED for {instance.appointment_date}.")
        print(f"--------------------------")