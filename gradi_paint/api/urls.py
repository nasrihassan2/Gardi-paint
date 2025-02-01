from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ProjectViewSet, CostViewSet, AdditionalServiceViewSet, EmployeeViewSet, ProjectEmployeeViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'costs', CostViewSet) 
router.register(r'services', AdditionalServiceViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'project-employees', ProjectEmployeeViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
