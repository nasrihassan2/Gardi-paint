from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client, Project, AdditionalService, Employee, ProjectEmployee, Cost, PDFDocument
from .serializers import ClientSerializer, ProjectSerializer, AdditionalServiceSerializer, EmployeeSerializer, ProjectEmployeeSerializer, CostSerializer, PDFDocumentSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from datetime import datetime
import io
from .filters import ProjectFilter
from PyPDF2 import PdfReader
import csv
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import pdfplumber
from rest_framework.decorators import action
from django.db import transaction
from django.db import models

#  Project ViewSet with Filtering
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = [
        'client__name',
        'client__email',
        'address',
        'job_type',
        'description',
        'building_type'
    ]
    ordering_fields = [
        'start_date',
        'end_date',
        'area_size_sqft',
        'total_gain'
    ]
    ordering = ['-start_date']  # Default ordering

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

def clean_numeric(value):
    if pd.isna(value):
        return 0.0
    # Remove any non-numeric characters except decimal points
    cleaned = ''.join(char for char in str(value) if char.isdigit() or char == '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

class PDFUploadViewSet(viewsets.ModelViewSet):
    queryset = PDFDocument.objects.all()
    serializer_class = PDFDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        try:
            if 'file' not in request.FILES:
                return Response({
                    'error': 'No file provided'
                }, status=status.HTTP_400_BAD_REQUEST)

            file = request.FILES['file']
            
            # Define column mappings
            column_mappings = {
                'Date Created': 'Date Created',
                'Email': 'Email',
                'Client Phone': 'Client Phone',
                'Building Type': 'Building Type',
                'Address': 'Address',
                'Job Type': 'Job Type',
                'Painting Area Size (sq ft': 'Painting Area Size (sq ft)',
                ')Total Paint Cost (Body)': 'Total Paint Cost (Body)',
                'Total Paint Cost (Trim)': 'Total Paint Cost (Trim)',
                'Other Paint Cost': 'Other Paint Cost',
                'Supplies Used': 'Supplies Used',
                'Cost of Supplies': 'Cost of Supplies',
                'Additional Services': 'Additional Services',
                'Additional Services': 'Additional Service',
                'sAdditional Service Cost': 'Additional Service Cost',
                'Employee Name': 'Employee Name',
                'Employee Wage': 'Employee Wage',
                'Hours Worked (Employee)': 'Hours Worked',
                'Project Length (Hours)': 'Project Length (Hours)',
                'Start Date': 'Start Date',
                'End Date': 'End Date',
                'Total Gain': 'Total Gain',
                'Job Description': 'Job Description'
            }

            # Initialize lists for tracking processing results
            processed_records = []
            errors = []

            # Save the file first
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            pdf_instance = serializer.save()

            if file.name.endswith('.pdf'):
                with pdfplumber.open(file) as pdf:
                    tables = []
                    for page in pdf.pages:
                        tables.extend(page.extract_tables())
                
                if tables:
                    headers = tables[0][0]
                    data = tables[0][1:]
                    df = pd.DataFrame(data, columns=headers)
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                return Response({
                    'error': 'File must be a PDF or CSV'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Process DataFrame
            if df is not None:
                df.columns = df.columns.str.strip()
                
                column_fixes = {
                    'Painting Area Size (sq ft': 'Painting Area Size (sq ft)',
                    ')Total Paint Cost (Body)': 'Total Paint Cost (Body)',
                    'Additional Service': 'Additional Services',
                    'sAdditional Service Cost': 'Additional Service Cost',
                    'Hours Worked (Employee)': 'Hours Worked'
                }
                
                df = df.rename(columns=column_fixes)
                
                for index, row in df.iterrows():
                    try:
                        # Clean phone number before creating client
                        phone_number = str(row['Client Phone']).strip()
                        phone_number = ' '.join(phone_number.split())
                        
                        client, created = Client.objects.get_or_create(
                            email=row['Email'],
                            defaults={
                                'name': row['Email'].split('@')[0],
                                'phone': phone_number
                            }
                        )

                        # Create or get Employee
                        employee_name_parts = str(row['Employee Name']).split()
                        if len(employee_name_parts) >= 2:
                            first_name = employee_name_parts[0]
                            last_name = ' '.join(employee_name_parts[1:])
                        else:
                            first_name = str(row['Employee Name'])
                            last_name = ""

                        employee, created = Employee.objects.get_or_create(
                            first_name=first_name,
                            last_name=last_name,
                            defaults={
                                'wage': clean_numeric(row['Employee Wage']),
                                'hours_worked': int(clean_numeric(row['Hours Worked']))
                            }
                        )

                        # Create Project
                        project = Project.objects.create(
                            client=client,
                            building_type=row['Building Type'],
                            address=row['Address'],
                            job_type=row['Job Type'],
                            description=f"Supplies Used: {row['Supplies Used']}",
                            area_size_sqft=clean_numeric(row['Painting Area Size (sq ft)']),
                            start_date=datetime.strptime(str(row['Start Date']), '%Y-%m-%d').date(),
                            end_date=datetime.strptime(str(row['End Date']), '%Y-%m-%d').date(),
                            total_gain=clean_numeric(row['Total Gain']),
                            status='pending'
                        )

                        # Create Cost
                        cost = Cost.objects.create(
                            project=project,
                            body_paint_cost=clean_numeric(row['Total Paint Cost (Body)']),
                            trim_paint_cost=clean_numeric(row['Total Paint Cost (Trim)']),
                            other_paint_cost=clean_numeric(row['Other Paint Cost']),
                            supplies_cost=clean_numeric(row['Cost of Supplies']),
                            additional_service_cost=clean_numeric(row['Additional Service Cost'])
                        )

                        # Create Additional Service if service name exists
                        if pd.notna(row['Additional Services']):
                            service = AdditionalService.objects.create(
                                project=project,
                                service_name=str(row['Additional Services']),
                                service_cost=clean_numeric(row['Additional Service Cost'])
                            )

                        # Create Project Employee Relationship
                        project_employee = ProjectEmployee.objects.create(
                            project=project,
                            employee=employee,
                            hours_worked=int(clean_numeric(row['Hours Worked']))
                        )

                        processed_records.append({
                            'project_id': project.project_id,
                            'client_email': client.email,
                            'date_created': row['Date Created']
                        })

                    except Exception as row_error:
                        errors.append({
                            'row': index + 1,
                            'error': str(row_error),
                            'data': row.to_dict()  # Add row data for debugging
                        })

                # Mark PDF as processed
                pdf_instance.processed = True
                pdf_instance.save()

                response_data = {
                    'message': 'File processed successfully',
                    'processed_records': processed_records,
                    'total_records': len(df),
                    'successful_records': len(processed_records),
                    'failed_records': len(errors)
                }
                
                if errors:
                    response_data['errors'] = errors
                    return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
                
                return Response(response_data, status=status.HTTP_201_CREATED)

            return Response({
                'error': 'No data found in file'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataManagementViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['DELETE'])
    def clear_all_data(self, request):
        try:
            with transaction.atomic():
                # Delete records from all tables
                PDFDocument.objects.all().delete()
                ProjectEmployee.objects.all().delete()
                AdditionalService.objects.all().delete()
                Cost.objects.all().delete()
                Project.objects.all().delete()
                Employee.objects.all().delete()
                Client.objects.all().delete()

                return Response({
                    'message': 'All data has been successfully deleted',
                    'status': 'success'
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': 'Error deleting data',
                'error': str(e),
                'status': 'failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)