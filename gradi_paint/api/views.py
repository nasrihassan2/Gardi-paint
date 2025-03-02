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
