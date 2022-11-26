from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Vols

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
    
class AirportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vols
        fields = "__all__"
        lookup_field = 'slug'
        # ('code','airline', 'from_airport', 'to_airport', 'departure')
