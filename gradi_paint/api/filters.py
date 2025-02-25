from django_filters import rest_framework as filters
from .models import Project
from django.db import models

class ProjectFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Project.JOB_STATUS_CHOICES)
    building_type = filters.ChoiceFilter(choices=[
        ('Residential', 'Residential'),
        ('Commercial', 'Commercial'),
        ('Industrial', 'Industrial')
    ])
    job_type = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')
    start_date = filters.DateFilter()
    end_date = filters.DateFilter()
    min_area = filters.NumberFilter(field_name='area_size_sqft', lookup_expr='gte')
    max_area = filters.NumberFilter(field_name='area_size_sqft', lookup_expr='lte')
    client_email = filters.CharFilter(field_name='client__email', lookup_expr='icontains')
    client_name = filters.CharFilter(field_name='client__name', lookup_expr='icontains')
    search = filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(client__name__icontains=value) |
            models.Q(client__email__icontains=value) |
            models.Q(address__icontains=value) |
            models.Q(job_type__icontains=value) |
            models.Q(description__icontains=value)
        )

    class Meta:
        model = Project
        fields = [
            'status', 'building_type', 'job_type', 'address',
            'start_date', 'end_date', 'min_area', 'max_area',
            'client_email', 'client_name', 'search'
        ] 