from django.shortcuts import render

from rest_framework import viewsets
from .models import Client, Project, Cost, Supply, AdditionalService, Employee, ProjectEmployee
from .serializers import ClientSerializer, ProjectSerializer, CostSerializer, SupplySerializer, AdditionalServiceSerializer, EmployeeSerializer, ProjectEmployeeSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class CostViewSet(viewsets.ModelViewSet):
    queryset = Cost.objects.all()
    serializer_class = CostSerializer


class SupplyViewSet(viewsets.ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer

class AdditionalServiceViewSet(viewsets.ModelViewSet):
    queryset = AdditionalService.objects.all()
    serializer_class = AdditionalServiceSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class ProjectEmployeeViewSet(viewsets.ModelViewSet):
    queryset = ProjectEmployee.objects.all()
    serializer_class = ProjectEmployeeSerializer