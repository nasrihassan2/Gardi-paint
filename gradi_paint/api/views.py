from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client, Project, AdditionalService, Employee, ProjectEmployee, Cost
from .serializers import ClientSerializer, ProjectSerializer, AdditionalServiceSerializer, EmployeeSerializer, ProjectEmployeeSerializer, CostSerializer 

#  Project ViewSet with Filtering
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'address', 'job_type']  # Allow filtering by status, city (address), and job type
    search_fields = ['description']  # Allow searching in descriptions

class CostViewSet(viewsets.ModelViewSet):
    queryset = Cost.objects.all()
    serializer_class = CostSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class AdditionalServiceViewSet(viewsets.ModelViewSet):
    queryset = AdditionalService.objects.all()
    serializer_class = AdditionalServiceSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class ProjectEmployeeViewSet(viewsets.ModelViewSet):
    queryset = ProjectEmployee.objects.all()
    serializer_class = ProjectEmployeeSerializer