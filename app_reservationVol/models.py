from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.contrib.auth.models import User


# Create your models here.
class Compagnies(models.Model):
    nom = models.CharField(max_length=250)
    image_path = models.ImageField(upload_to='compagnies')
    status = models.CharField(max_length=2, choices=(('1','En service'), ('2','Hors Service')), default = 1)
    # delete_flag = models.IntegerField(default = 0)
    # date_added = models.DateTimeField(default = timezone.now)
    # date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "Liste des compagnies"

    def __str__(self):
        return str(f"{self.nom}")


    def save(self, *args, **kwargs):
        super(Compagnies, self).save(*args, **kwargs)
        print(self.image_path)
        if not self.image_path == '':
            imag = Image.open(self.image_path.path)
            width = imag.width
            height = imag.height
            if imag.width > 640:
                perc = (width - 640) / width
                width = 640
                height = height - (height * perc)
            if imag.height > 480:
                perc = (height - 480) / height
                height = 480
                width = width - (width * perc)
            output_size = (width, height)
            imag.thumbnail(output_size)
            imag.save(self.image_path.path)

    def delete(self, *args, **kwargs):
        super(Compagnies, self).delete(*args, **kwargs)
        storage, path = self.image_path.storage, self.image_path.path
        storage.delete(path)
        
class Trajet(models.Model):
    depart = models.CharField(max_length=250)
    arrive = models.CharField(max_length=250)
    status = models.CharField(max_length=2, choices=(('1','En service'), ('2','Hors service')), default = 1)
    # delete_flag = models.IntegerField(default = 0)
    # date_added = models.DateTimeField(default = timezone.now)
    # date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "Liste des trajets"

    def __str__(self):
        return str(f"{self.depart}{self.arrive}")

class Vols(models.Model):
    code = models.CharField(max_length=250)
    compagnies = models.ManyToManyField(Compagnies)
    status = models.CharField(max_length=2, choices=(('1','Disponible'), ('2','Indisponible')), default = 1)
    prix = models.IntegerField()
    depart_trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name="depart_Trajet")
    destination_trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name="arrive_Trajet")    
    date_depart = models.DateTimeField()
    date_arrive = models.DateTimeField()
    # air_craft_code = models.CharField(max_length=250)
    # business_class_slots = models.IntegerField(default=0)
    # economy_slots = models.IntegerField(default=0)
    # business_class_price = models.FloatField(default=0)
    # economy_price = models.FloatField(default=0)
    # delete_flag = models.IntegerField(default = 0)
    # date_added = models.DateTimeField(default = timezone.now)
    # date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "Liste des vols"

    def __str__(self):
        return str(f"{self.code} [{self.depart_trajet.depart} - {self.destination_trajet.arrive}]")

    def b_slot(self):
        try:
            reservation = Reservation.objects.exclude(status = 2).filter(flight=self, type = 1).count()
            if reservation is None:
                reservation = 0

        except:
            reservation = 0

        return self.business_class_slots - reservation

    def e_slot(self):
        try:
            reservation = Reservation.objects.exclude(status = 2).filter(flight=self, type = 2).count()
            if reservation is None:
                reservation = 0

        except:
            reservation = 0
        return self.economy_slots - reservation

        
class Reservation(models.Model):
    vol = models.ForeignKey(Vols, on_delete=models.CASCADE, null=True)
    # type = models.CharField(max_length=50, choices=(('1','Business Class'), ('2','Economy')), default = '2')
    prenom = models.CharField(max_length=250)
    # middle_name = models.CharField(max_length=250)
    nom = models.CharField(max_length=250)
    genre = models.CharField(max_length=50, choices=(('Homme','Homme'), ('Femme','Femme')), default = 'Homme')
    email = models.CharField(max_length=250)
    contact = models.CharField(max_length=250)
    addresse = models.TextField()
    status_reservation = models.CharField(max_length=2, choices=(('0','En cours'),('1','Confirmé'), ('2','Annulé')), default = 0)
    date_ajoute = models.DateTimeField(default = timezone.now)
    date_cree = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "Liste des réservations"

    def __str__(self):
        return str(f"{self.vol.code} - {self.prenom} {self.nom}")
    
    def name(self):
        return str(f"{self.nom}, {self.prenom}")
