from rest_framework import serializers, viewsets
from .models import Provider

class ProviderSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Provider
        fields = '__all__' #('name', 'email', 'phone', 'language', 'currency')

class ProviderViewSet(viewsets.ModelViewSet):

    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    
