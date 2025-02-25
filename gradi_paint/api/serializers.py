from rest_framework import serializers
from .models import Client, Project, AdditionalService, Employee, ProjectEmployee, Cost, PDFDocument

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

class PDFDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = ['id', 'file', 'uploaded_at', 'processed']

class CalendarEventSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    start = serializers.DateField(source='start_date')
    end = serializers.DateField(source='end_date')
    client_name = serializers.CharField(source='client.name')
    client_email = serializers.CharField(source='client.email')
    client_phone = serializers.CharField(source='client.phone')
    
    def get_title(self, obj):
        return f"{obj.job_type} - {obj.building_type} ({obj.client.name})"

    class Meta:
        model = Project
        fields = [
            'project_id',
            'title',
            'start',
            'end',
            'client_name',
            'client_email',
            'client_phone',
            'address',
            'job_type',
            'building_type',
            'status',
            'description'
        ]