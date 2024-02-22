from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


from lizaalert.webinars.models import Webinar
from lizaalert.webinars.serializers import WebinarSerializer


class WebinarViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated,]
    serializer_class = WebinarSerializer
    queryset = Webinar.objects.all()
