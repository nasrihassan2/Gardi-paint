from rest_framework import serializers
from .models import Client, Project, AdditionalService, Employee, ProjectEmployee, Cost

#  Client Serializer (with validation)
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

#  Project Serializer (Auto-increment Job ID)
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

#  Additional Service Serializer
class AdditionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalService
        fields = '__all__'

# Employee Serializer (with first & last name)
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

#  Project-Employee Relationship Serializer
class ProjectEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectEmployee
        fields = '__all__'

class CostSerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField()  # Read-only field to get total cost

    class Meta:
        model = Cost
        fields = '__all__'  # Include all cost fields