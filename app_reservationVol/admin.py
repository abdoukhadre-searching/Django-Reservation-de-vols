from django.contrib import admin
from app_reservationVol import models

# Register your models here.
admin.site.register(models.Compagnies)
admin.site.register(models.Trajet)
admin.site.register(models.Vols)
admin.site.register(models.Reservation)
