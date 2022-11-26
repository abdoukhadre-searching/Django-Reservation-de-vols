from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewset)
router.register(r'airport', views.AirportViewset)

urlpatterns = [
    # path('',include(router.urls)),
    path('acceuil',views.recherche_vol, name='public-page'),
    path('recherche_resultat',views.search_result, name="search-result"),
    path('recherche_resultat/<int:fromA>/<int:toA>/<str:departure>',views.search_result),
    path('reserve_form/<int:pk>',views.reserve_form,name='reserve-form'),
    path('save_reservation',views.save_reservation,name='save-reservation'),
    path('home',views.home, name="home-page"),
    path('login',views.login_page,name='login-page'),
    path('register',views.userregister,name='register-page'),
    path('save_register',views.save_register,name='register-user'),
    path('user_login',views.login_user,name='login-user'),
    path('home',views.home,name='home-page'),
    path('logout',views.logout_user,name='logout'),
    path('profile',views.profile,name='profile-page'),
    path('update_password',views.update_password,name='update-password'),
    path('update_profile',views.update_profile,name='update-profile'),
    path('compagnie',views.list_airline,name='airline-page'),
    path('gestion_compagnie',views.manage_airline,name='manage-airline'),
    path('gestion_compagnie/<int:pk>',views.manage_airline,name='manage-airline-pk'),
    path('add_compagnie',views.save_compagnie,name='save-airline'),
    path('delete_compagnie/<int:pk>',views.delete_compagnie,name='delete-airline-pk'),
    path('trajet',views.list_trajet,name='airport-page'),
    path('gestion_trajet',views.gestion_trajet,name='manage-airport'),
    path('gestion_trajet/<int:pk>',views.gestion_trajet,name='manage-airport-pk'),
    path('ajout_trajet',views.save_trajets,name='save-airport'),
    path('delete_trajet/<int:pk>',views.delete_trajet,name='delete-airport-pk'),
    path('vols',views.list_vols,name='flight-page'),
    path('gestion_vol',views.gestion_vol,name='manage-flight'),
    path('gestion_vol/<int:pk>',views.gestion_vol,name='manage-flight-pk'),
    path('view_vol/<int:pk>',views.view_vol,name='view-flight-pk'),
    path('add_vols',views.ajout_vols,name='save-flight'),
    path('delete_vol/<int:pk>',views.supprimer_vol,name='delete-flight-pk'),
    path('reservation',views.list_reservation,name='reservation'),
    path('view_reservation/<int:pk>',views.view_reservation,name='view-reservation-pk'),
    path('delete_reservation/<int:pk>',views.delete_reservation,name='delete-reservation-pk'),
    path('update_reservation',views.update_reservation,name='update-reservation'),
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
