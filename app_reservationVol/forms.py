from secrets import choice
from django import forms
from numpy import require
from app_reservationVol import models
#import qrcode
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User

class SaveUser(UserCreationForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    password1 = forms.CharField(max_length=250)
    password2 = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name','password1', 'password2',)

class UpdateProfile(UserChangeForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name')

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(f"Password is Incorrect")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")

class UpdatePasswords(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Old Password")
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="New Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Confirm New Password")
    class Meta:
        model = User
        fields = ('old_password','new_password1', 'new_password2')

class SaveCompagnies(forms.ModelForm):
    nom = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)
    image_path = forms.ImageField(required=False)

    class Meta:
        model = models.Compagnies
        fields = ('nom','status', 'image_path',)

    def clean_nom(self):
        id = self.data['id'] if (self.data['id']).isnumeric() else 0
        nom = self.cleaned_data['nom']
        try:
            if id > 0:
                compagnie = models.Compagnie.objects.exclude(id = id).get(nom = nom)
            else:
                compagnie = models.Compagnie.objects.get(nom = nom)
        except:
            return nom
        raise forms.ValidationError("Compagnie existe déja")


class SaveTrajets(forms.ModelForm):
    depart = forms.CharField(max_length=250)
    arrive = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Trajet
        fields = ('depart','arrive','status', )

    def clean_depart(self):
        id = self.data['id'] if (self.data['id']).isnumeric() else 0
        depart = self.cleaned_data['depart']
        # arrive = self.cleaned_data['arrive']
        try:
            if id > 0:
                trajet = models.Trajet.objects.exclude(id = id).get(depart = depart)
            else:
                trajet = models.Trajet.objects.get(depart = depart)
        except:
            return f'{depart}'
        raise forms.ValidationError("Trajet deja definit")

class SaveVols(forms.ModelForm):
    code = forms.CharField(max_length=250)
    compagnie = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)
    prix = forms.IntegerField(max_value=10)
    depart_trajet = forms.CharField(max_length=250)
    destination_trajet = forms.CharField(max_length=250)
    # air_craft_code = forms.CharField(max_length=250)
    date_depart = forms.DateTimeField()
    date_arrive = forms.DateTimeField()
    # business_class_slots = forms.CharField(max_length=250)
    # economy_slots = forms.CharField(max_length=250)
    # business_class_price = forms.CharField(max_length=250)
    # economy_price = forms.CharField(max_length=250)

    class Meta:
        model = models.Vols
        fields = ('code', 'compagnie', 'status', 'prix', 'depart_trajet', 'destination_trajet', 'date_depart', 'date_arrive',) # 'business_class_slots', 'economy_slots', 'business_class_price', 'economy_price', )

    def clean_code(self):
        id = self.data['id'] if (self.data['id']).isnumeric() else 0
        code = self.cleaned_data['code']
        try:
            if id > 0:
                vol = models.Vols.objects.exclude(id = id).get(code = code)
            else:
                vol = models.Vols.objects.get(code = code)
        except:
            return code
        raise forms.ValidationError("Code du vol deja assigné")

    def clean_compagnie(self):
        aid = self.cleaned_data['compagnie']
        try:
            compagnie = models.Compagnies.objects.get(id = aid)
            return compagnie
        except:
            raise forms.ValidationError(f"La compagnie selectionnée est invalide")
    
    def clean_depart_trajet(self):
        aid = self.cleaned_data['depart_trajet']
        try:
            trajet = models.Trajet.objects.get(id = aid)
            return trajet
        except:
            raise forms.ValidationError(f"Le lieu de depart choisi est invalide")

    def clean_destination_trajet(self):
        aid = self.cleaned_data['destination_trajet']
        try:
            trajet = models.Trajet.objects.get(id = aid)
            return trajet
        except:
            raise forms.ValidationError(f"La destination choisi est invalide")

class SaveReservation(forms.ModelForm):
    vol = forms.CharField(max_length=250)
    type = forms.CharField(max_length=250)
    prenom = forms.CharField(max_length=250)
    # midle_name = forms.CharField(max_length=250, required=False)
    nom = forms.CharField(max_length=250)
    genre = forms.CharField(max_length=250)
    contact = forms.CharField(max_length=250)
    email = forms.CharField(max_length=250)
    addresse = forms.Textarea()


    class Meta:
        model = models.Reservation
        fields = ('vol', 'type', 'prenom', 'nom', 'genre', 'contact', 'email', 'addresse', )

    def clean_vol(self):
        fid = self.cleaned_data['vol']
        try:
            vol = models.Vols.objects.get(id = fid)
            return vol
        except:
            raise forms.ValidationError(f"Vol invalide")
    