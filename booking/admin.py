
from django.contrib import admin
from .models import Profile, Lawyer, Appointment, Payment

admin.site.register(Profile)
admin.site.register(Lawyer)
admin.site.register(Appointment)
admin.site.register(Payment)

# Register your models here.
