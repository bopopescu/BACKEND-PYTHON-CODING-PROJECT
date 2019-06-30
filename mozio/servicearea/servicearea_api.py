from rest_framework import serializers, viewsets
from .models import ServiceArea
from django.contrib.gis.geos import Point
from rest_framework.response import Response
from servicearea.provider_api import ProviderSerializer


class ServiceAreaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ServiceArea
        fields = '__all__' 

class ServiceAreaViewSet(viewsets.ModelViewSet):

    queryset = ServiceArea.objects.all()
    serializer_class = ServiceAreaSerializer

    def getAreas(self, request, lng=None, lat=None):
        """
            lng : longitude
            lat : latitude

            return  Response
        """
        queryset = self.queryset
        query_set = []
        #print(lng, lat)
        if lat and lng:
            pnt = Point(float(lng), float(lat)) 
            for elt in queryset:
                if pnt.within(elt.area):
                    query_set.append(elt)
        serializer = self.get_serializer(query_set, many=True)
        return Response(serializer.data)

