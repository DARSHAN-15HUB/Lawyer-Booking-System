
from django.db import models
from django.contrib.auth.models import User


# 1. User Profile Model
class Profile(models.Model):

    ROLE_CHOICES = [
        ('CLIENT', 'Client'),
        ('LAWYER', 'Lawyer'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='CLIENT'
    )

    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


# 2. Lawyer Model
class Lawyer(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    specialization = models.CharField(max_length=100)

    experience = models.PositiveIntegerField()

    qualification = models.CharField(max_length=200)

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    bio = models.TextField()

    profile_image = models.ImageField(
        upload_to='lawyers/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


# 3. Appointment Model
class Appointment(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_appointments'
    )

    lawyer = models.ForeignKey(
        Lawyer,
        on_delete=models.CASCADE,
        related_name='lawyer_appointments'
    )

    appointment_date = models.DateTimeField()

    case_details = models.TextField()

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    meeting_link = models.URLField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.lawyer.user.username}"


# 4. Payment Model

class Payment(models.Model):

    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    platform_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00
    )

    platform_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    lawyer_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    route_transfer_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='PENDING'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Payment for Appointment {self.appointment.id}"
