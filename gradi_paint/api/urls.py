from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ProjectViewSet, CostViewSet, AdditionalServiceViewSet, EmployeeViewSet, ProjectEmployeeViewSet, PDFUploadViewSet, DataManagementViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

#  Swagger schema setup
schema_view = get_schema_view(
    openapi.Info(
        title="Gardi Paint API",
        default_version="v1",
        description="API documentation for Gardi paint backend",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

#  Register ViewSets
router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'costs', CostViewSet)
router.register(r'services', AdditionalServiceViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'project-employees', ProjectEmployeeViewSet)
router.register(r'pdf-upload', PDFUploadViewSet)
router.register(r'data-management', DataManagementViewSet, basename='data-management')

# Define API URL patterns
urlpatterns = [
    path('api/', include(router.urls)),

    #  Swagger UI and Redoc documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]