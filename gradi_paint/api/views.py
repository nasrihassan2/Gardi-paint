from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.db.models import Count, Sum, Avg
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from .models import Client, Project, AdditionalService, Employee, ProjectEmployee, Cost, PDFDocument
from .serializers import (
    ClientSerializer, ProjectSerializer, AdditionalServiceSerializer,
    EmployeeSerializer, ProjectEmployeeSerializer, CostSerializer,
    PDFDocumentSerializer, CalendarEventSerializer
)
import pdfplumber
import pandas as pd
from datetime import datetime


# --------------------------
#  PROJECT VIEWSET
# --------------------------
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['client__name', 'client__email', 'address', 'job_type', 'description', 'building_type']
    ordering_fields = ['start_date', 'end_date', 'area_size_sqft', 'total_gain']
    ordering = ['-start_date']

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        """Fetch project summary data for the dashboard."""
        current_year = now().year

        # Total number of projects
        total_projects = Project.objects.count()

        # Projects completed this year
        completed_projects_this_year = Project.objects.filter(
            status='completed', end_date__year=current_year
        ).count()

        # Total earnings per year
        total_earnings_by_year = (
            Project.objects.filter(status='completed')
            .values('end_date__year')
            .annotate(total_earnings=Sum('total_gain'))
        )

        # Get the earnings for the current year
        current_year_earnings = (
            total_earnings_by_year.filter(end_date__year=current_year)
            .aggregate(total=Sum('total_earnings'))['total'] or 0
        )

        # Average earnings per project
        average_earnings = Project.objects.filter(status='completed').aggregate(
            avg_earnings=Avg('total_gain')
        )['avg_earnings'] or 0

        # Total number of unique clients
        total_clients = Client.objects.count()

        # Project completion rate
        completed_projects = Project.objects.filter(status='completed').count()
        completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0

        data = {
            "total_projects": total_projects,
            "completed_projects_this_year": completed_projects_this_year,
            "current_year_earnings": current_year_earnings,
            "total_earnings_by_year": list(total_earnings_by_year),
            "average_earnings_per_project": round(average_earnings, 2),
            "total_clients": total_clients,
            "project_completion_rate": f"{completion_rate:.2f}%"
        }

        return Response(data)

    @action(detail=False, methods=['GET'])
    def calendar_events(self, request):
        """Fetch calendar events for projects."""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        queryset = self.get_queryset()

        if start:
            queryset = queryset.filter(start_date__gte=start)
        if end:
            queryset = queryset.filter(end_date__lte=end)

        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        serializer = CalendarEventSerializer(queryset, many=True)
        return Response(serializer.data)


# --------------------------
#  OTHER VIEWSETS
# --------------------------
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
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            pdf_instance = serializer.save()
            
            # Initialize lists for tracking processing results
            processed_records = []
            errors = []
            
            # Clean numeric values function
            def clean_numeric(value):
                if pd.isna(value):
                    return 0.0
                cleaned = ''.join(char for char in str(value) if char.isdigit() or char == '.')
                try:
                    return float(cleaned)
                except ValueError:
                    return 0.0
            
            try:
                # Process PDF file to extract data
                if file.name.endswith('.pdf'):
                    try:
                        with pdfplumber.open(pdf_instance.file.path) as pdf:
                            tables = []
                            for page in pdf.pages:
                                extracted_tables = page.extract_tables()
                                if extracted_tables:
                                    tables.extend(extracted_tables)
                            
                            if tables:
                                headers = tables[0][0]
                                data = tables[0][1:]
                                df = pd.DataFrame(data, columns=headers)
                            else:
                                return Response({
                                    'error': 'No tables found in PDF'
                                }, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as pdf_error:
                        return Response({
                            'error': f'Error extracting data from PDF: {str(pdf_error)}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                elif file.name.endswith('.csv'):
                    # Process CSV
                    df = pd.read_csv(pdf_instance.file.path)
                else:
                    return Response({
                        'error': 'File must be a PDF or CSV'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Process DataFrame
                if df is not None:
                    # Clean column names
                    df.columns = df.columns.str.strip()
                    
                    # Process each row
                    for index, row in df.iterrows():
                        try:
                            # Clean phone number
                            phone_number = str(row.get('Client Phone', '')).strip()
                            phone_number = ' '.join(phone_number.split())
                            
                            # Create or get Client
                            client, created = Client.objects.get_or_create(
                                email=row.get('Email', ''),
                                defaults={
                                    'name': row.get('Email', '').split('@')[0],
                                    'phone': phone_number
                                }
                            )
                            
                            # Create or get Employee
                            employee_name = str(row.get('Employee Name', ''))
                            employee_name_parts = employee_name.split()
                            if len(employee_name_parts) >= 2:
                                first_name = employee_name_parts[0]
                                last_name = ' '.join(employee_name_parts[1:])
                            else:
                                first_name = employee_name
                                last_name = ""
                                
                            employee, created = Employee.objects.get_or_create(
                                first_name=first_name,
                                last_name=last_name,
                                defaults={
                                    'wage': clean_numeric(row.get('Employee Wage', 0)),
                                    'hours_worked': int(clean_numeric(row.get('Hours Worked', 0)))
                                }
                            )
                            
                            # Create Project
                            project = Project.objects.create(
                                client=client,
                                building_type=row.get('Building Type', ''),
                                address=row.get('Address', ''),
                                job_type=row.get('Job Type', ''),
                                description=f"Supplies Used: {row.get('Supplies Used', '')}",
                                area_size_sqft=clean_numeric(row.get('Painting Area Size (sq ft)', 0)),
                                start_date=datetime.strptime(str(row.get('Start Date', '')), '%Y-%m-%d').date(),
                                end_date=datetime.strptime(str(row.get('End Date', '')), '%Y-%m-%d').date(),
                                total_gain=clean_numeric(row.get('Total Gain', 0)),
                                status='pending'
                            )
                            
                            # Create Cost
                            cost = Cost.objects.create(
                                project=project,
                                body_paint_cost=clean_numeric(row.get('Total Paint Cost (Body)', 0)),
                                trim_paint_cost=clean_numeric(row.get('Total Paint Cost (Trim)', 0)),
                                other_paint_cost=clean_numeric(row.get('Other Paint Cost', 0)),
                                supplies_cost=clean_numeric(row.get('Cost of Supplies', 0)),
                                additional_service_cost=clean_numeric(row.get('Additional Service Cost', 0))
                            )
                            
                            # Create Additional Service
                            service_name = row.get('Additional Services', '')
                            if pd.notna(service_name) and service_name:
                                service = AdditionalService.objects.create(
                                    project=project,
                                    service_name=str(service_name),
                                    service_cost=clean_numeric(row.get('Additional Service Cost', 0))
                                )
                                
                            # Create Project Employee Relationship
                            project_employee = ProjectEmployee.objects.create(
                                project=project,
                                employee=employee,
                                hours_worked=int(clean_numeric(row.get('Hours Worked', 0)))
                            )
                            
                            processed_records.append({
                                'project_id': project.project_id,
                                'client_email': client.email,
                                'date_created': row.get('Date Created', '')
                            })
                            
                        except Exception as row_error:
                            errors.append({
                                'row': index + 1,
                                'error': str(row_error)
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
                
            except Exception as processing_error:
                return Response({
                    'error': f'Error processing file: {str(processing_error)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --------------------------
#  DATA MANAGEMENT VIEWSET
# --------------------------
class DataManagementViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['DELETE'])
    def clear_all_data(self, request):
        """Delete all data in the database."""
        try:
            with transaction.atomic():
                PDFDocument.objects.all().delete()
                ProjectEmployee.objects.all().delete()
                AdditionalService.objects.all().delete()
                Cost.objects.all().delete()
                Project.objects.all().delete()
                Employee.objects.all().delete()
                Client.objects.all().delete()

                return Response({"message": "All data has been successfully deleted"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
