import datetime
from django.shortcuts import redirect, render
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from app_reservationVol import models, forms
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Vols
# FOR DJANGO REST FRAMEWORK
from rest_framework import viewsets
from .serializers import UserSerializer, AirportSerializer


#views pour django rest framework
class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('date_joined')
    serializer_class = UserSerializer

class AirportViewset(viewsets.ModelViewSet):
    queryset = Vols.objects.all()
    serializer_class = AirportSerializer

def context_data():
    context = {
        'page_name' : '',
        'page_title' : '',
        'system_name' : 'Reservation de vols',
        'topbar' : True,
        'footer' : True,
    }

    return context
    
def userregister(request):
    context = context_data()
    context['topbar'] = False
    context['footer'] = False
    context['page_title'] = "User Registration"
    if request.user.is_authenticated:
        return redirect("home-page")
    return render(request, 'register.html', context)

@login_required
def upload_modal(request):
    context = context_data()
    return render(request, 'upload.html', context)

def save_register(request):
    resp={'status':'failed', 'msg':''}
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent on this request"
    else:
        form = forms.SaveUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Account has been created succesfully")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.name}] {error}.")
            
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def update_profile(request):
    context = context_data()
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = forms.UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile-page")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)

@login_required
def update_password(request):
    context =context_data()
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = forms.UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile-page")
        else:
            context['form'] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)

# Create your views here.
def login_page(request):
    context = context_data()
    context['topbar'] = False
    context['footer'] = False
    context['page_name'] = 'login'
    context['page_title'] = 'Login'
    return render(request, 'login.html', context)

def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

def recherche_vol(request):
    context = context_data()
    context['page'] = 'Recherche de vols disponibles'
    compagnies = models.Compagnies.objects.filter(status = 1).all()
    trajets = models.Trajet.objects.filter(status = 1).all()
    context['compagnies'] = compagnies
    context['trajets'] = trajets
    
    return render(request,'recherche_vol.html', context)

def search_result(request, lieuDepart=None, lieuArrive=None, date_depart = None):
    context = context_data()
    context['page'] = 'Resultat recherche'
    if lieuDepart is None and lieuArrive is None and date_depart is None:
        messages.error(request, "Saisis incorrecte")
        return redirect('public-page')
    else:
        date_depart = datetime.datetime.strptime(date_depart, "%Y-%m-%d")
        year = date_depart.strftime("%Y")
        month = date_depart.strftime("%m")
        day = date_depart.strftime("%d")
        context['vols'] = models.Vols.objects.filter(
                        date_depart__year = year,
                        date_depart__month = month,
                        date_depart__day = day,
                        ).order_by('date_depart').all()
        return render(request, 'search_result.html', context)

def save_reservation(request):
    resp = { 'status': 'failed', 'msg':'' }
    if not request.method == 'POST':
       resp['msg'] = "Aucune information n'a ete envoyé."
    else:
        form = forms.SaveReservation(request.POST)
        if form.is_valid():
            form.save()
            resp['status'] = 'success'
            resp['msg'] = "Votre réservation a été envoyé. Notre equipe vous contactera pour la confirmation de cell-ci. Merci et à bientot !"
            messages.success(request,f"{resp['msg']}")
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str("<br />")

                    resp['msg'] += str(f"[{field.name}] {error}")
    return HttpResponse(json.dumps(resp), content_type="application/json")

def reserve_form(request, pk=None):
    context = context_data()
    context['page'] = 'Resultat recherche'
    if pk is None:
        messages.error(request, "ID vol invalide")
        return redirect('public-page')
    else:
        context['vol'] = models.Vols.objects.get(id=pk)
        return render(request, 'reservation.html', context)


@login_required
def home(request):
    context = context_data()
    context['page'] = 'acceuil'
    context['page_title'] = 'acceuil'
    context['compagnies'] = models.Compagnies.objects.filter(status = 1).count()
    context['trajet'] = models.Trajet.objects.filter(status = 1).count()
    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    hour = now.strftime("%H")
    context['vol'] = models.Vols.objects.filter(
                            date_depart__year__gte = year,
                            date_depart__month__gte = month,
                            date_depart__day__gte = day,
                            date_depart__hour__gte = hour,
                            ).count()
    return render(request, 'home.html', context)

def logout_user(request):
    logout(request)
    return redirect('login-page')
    
@login_required
def profile(request):
    context = context_data()
    context['page'] = 'profile'
    context['page_title'] = "Profile"
    return render(request,'profile.html', context)

#Airline
@login_required
def list_airline(request):
    context = context_data()
    context['page_title'] = "compagnies"
    context['compagnies'] = models.Compagnies.objects.all()
    return render(request, 'airlines.html', context) 

@login_required
def manage_airline(request, pk = None):
    if pk is None:
        compagnie = {}
    else:
        compagnie = models.Compagnies.objects.get(id = pk)
    context = context_data()
    context['page_title'] ="Gestion compagnie"
    context['compagnie'] = compagnie
    return render(request, 'manage_airline.html', context) 

@login_required
def save_compagnie(request):
    resp = { 'status': 'echec', 'msg':'' }
    if not request.method == 'POST':
       resp['msg'] = "Aucune information n'a ete envoyé."
    else:
        post = request.POST
        print('post...', post)
        if not post['id'] == '':
            compagnie = models.Compagnies.objects.get(id = post['id'])
            print('compagnie...', compagnie)
            form = forms.SaveCompagnies(request.POST, request.FILES, instance = compagnie)
        else:
            form = forms.SaveCompagnies(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            resp['status'] = 'success'
            if post['id'] == '':
                resp['msg'] = "Ajout d'une nouvelle compagnie."
            else:
                resp['msg'] = "Details aéroport modifié avec succés."
            messages.success(request,f"{resp['msg']}")
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str("<br />")

                    resp['msg'] += str(f"[{field.name}] {error}")
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_compagnie(request, pk=None):
    resp = { 'status' : 'echec', 'msg' : '' }
    if pk is None:
        resp['msg'] = 'Aucun identifiant fourni'
    else:
        try:
            models.Compagnies.objects.filter(id = pk).delete()#.update(delete_flag = 1)
            resp['status'] = 'success'
            messages.success(request, "Compagnie supprimé avec succés")
        except:
            resp['msg'] = 'Echec lors de la suppression de la compagnie'
    return HttpResponse(json.dumps(resp), content_type="application/json")

    
#Trajet
@login_required
def list_trajet(request):
    context = context_data()
    context['page_title'] ="Trajets"
    context['trajets'] = models.Trajet.objects.all()
    return render(request, 'trajet.html', context) 

@login_required
def gestion_trajet(request, pk = None):
    if pk is None:
        trajet = {}
    else:
        trajet = models.Trajet.objects.get(id = pk)
    context = context_data()
    context['page_title'] ="Gestion trajet"
    context['trajet'] = trajet
    return render(request, 'gestion_trajet.html', context) 

@login_required
def save_trajets(request):
    resp = { 'status': 'echec', 'msg':'' }
    if not request.method == 'POST':
       resp['msg'] = "No data has been sent."
    else:
        post = request.POST
        if not post['id'] == '':
            trajet = models.Trajet.objects.get(id = post['id'])
            form = forms.SaveTrajets(request.POST, instance = trajet)
        else:
            form = forms.SaveTrajets(request.POST)

        if form.is_valid():
            form.save()
            resp['status'] = 'success'
            if post['id'] == '':
                resp['msg'] = "Ajout d'un nouveau trajet réussi."
            else:
                resp['msg'] = "Details trajet modifiés avec succes."
            messages.success(request,f"{resp['msg']}")
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str("<br />")

                    resp['msg'] += str(f"[{field.name}] {error}")
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_trajet(request, pk=None):
    resp = { 'status' : 'failed', 'msg' : '' }
    if pk is None:
        resp['msg'] = 'No ID has been sent'
    else:
        try:
            models.Trajet.objects.filter(id = pk).delete()# update(delete_flag = 1)
            resp['status'] = 'success'
            messages.success(request, "Trajet supprime avec succes")
        except:
            resp['msg'] = 'Echec lors de la suppression du trajet'
    return HttpResponse(json.dumps(resp), content_type="application/json")

#Flight
@login_required
def list_vols(request):
    context = context_data()
    context['page_title'] ="Vols"
    context['vols'] = models.Vols.objects.all()
    return render(request, 'vols.html', context) 

@login_required
def gestion_vol(request, pk = None):
    if pk is None:
        vol = {}
    else:
        vol = models.Vols.objects.get(id = pk)
    compagnies = models.Compagnies.objects.filter(status = 1).all()
    trajets = models.Trajet.objects.filter(status = 1).all()
    context = context_data()
    context['page_title'] ="Gestion Vol"
    context['vol'] = vol
    context['compagnies'] = compagnies
    context['trajets'] = trajets
    return render(request, 'gestion_vol.html', context) 

@login_required
def ajout_vols(request):
    resp = { 'status': 'echec', 'msg':'' }
    if not request.method == 'POST':
       resp['msg'] = "Aucune information fournie."
    else:
        post = request.POST
        print(post)
        if not post['id'] == '':
            vol = models.Vols.objects.get(id = post['id'])
            form = forms.SaveVols(request.POST, instance = vol)
        else:
            form = forms.SaveVols(request.POST)            

        if form.is_valid():
            print(form.order_fields)
            form.save()
            resp['status'] = 'success'
            if post['id'] == '':
                resp['msg'] = "Nouveau vol ajouté."
            else:
                resp['msg'] = "OK ! Details vol modifié."
            messages.success(request,f"{resp['msg']}")
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str("<br />")

                    resp['msg'] += str(f"[{field.name}] {error}")
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_vol(request, pk = None):
    if pk is None:
        vol = {}
    else:
        vol = models.Vols.objects.get(id = pk)
    context = context_data()
    context['page_title'] ="Details vol"
    context['vols'] = vol
    return render(request, 'view_vol_details.html', context) 

@login_required
def supprimer_vol(request, pk=None):
    resp = { 'status' : 'echec', 'msg' : '' }
    if pk is None:
        resp['msg'] = 'Aucun information fournie'
    else:
        try:
            models.Vols.objects.filter(id = pk).delete() #update(delete_flag = 1)
            resp['status'] = 'success'
            messages.success(request, "Vol supprime avec succes")
        except:
            resp['msg'] = 'Echec lors de la suppression du vol'
    return HttpResponse(json.dumps(resp), content_type="application/json")

#Reservation
@login_required
def list_reservation(request):
    context = context_data()
    context['page_title'] ="Reservations"
    context['reservations'] = models.Reservation.objects.all()
    return render(request, 'reservation_list.html', context) 

@login_required
def view_reservation(request, pk = None):
    if pk is None:
        reservation = {}
    else:
        reservation = models.Reservation.objects.get(id = pk)
    context = context_data()
    context['page_title'] ="Reservation Details"
    context['reservation'] = reservation
    return render(request, 'view_reservation_details.html', context) 

@login_required
def delete_reservation(request, pk=None):
    resp = { 'status' : 'echec', 'msg' : '' }
    if pk is None:
        resp['msg'] = 'Aucun information fournie'
    else:
        try:
            models.Reservation.objects.filter(id = pk).delete()
            resp['status'] = 'success'
            messages.success(request, "Suppression de la reservation")
        except:
            resp['msg'] = 'Echec lors de la suppression de la reservation'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def update_reservation(request):
    resp = { 'status' : 'echec', 'msg' : '' }
    if not request.method == 'POST':
        resp['msg'] = 'Aucun information fournie'
    else:
        try:
            models.Reservation.objects.filter(id = request.POST['id']).update(status=request.POST['status'])
            resp['status'] = 'success'
            messages.success(request, "Mise a jour du status Reservation ")
        except:
            resp['msg'] = 'Echec lors de la maj du status de la Reservation'
    return HttpResponse(json.dumps(resp), content_type="application/json")