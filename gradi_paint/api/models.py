from django.db import models

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50)


class Project(models.Model):
    BUILDING_TYPES = [
        ('Residential', 'Residential'),
        ('Commercial', 'Commercial'),
        ('Industrial', 'Industrial'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="projects")
    building_type = models.CharField(max_length=50, choices=BUILDING_TYPES)
    address = models.CharField(max_length=255)
    job_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    area_size_sqft = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_gain = models

class Cost(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    body_paint_cost = models.FloatField()
    trim_paint_cost = models.FloatField()
    other_paint_cost = models.FloatField()
    supplies_cost = models.FloatField()
    additional_service_cost = models.FloatField()


class Supply(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="supplies")
    supply_name = models.CharField(max_length=100)
    supply_cost = models.FloatField()

class Supply(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="supplies")
    supply_name = models.CharField(max_length=100)
    supply_cost = models.FloatField()


class AdditionalService(models.Model):  # Make sure this is correct!
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="services")
    service_name = models.CharField(max_length=100)
    service_cost = models.FloatField()


class Employee(models.Model):
    name = models.CharField(max_length=255)
    wage = models.FloatField()
    hours_worked = models.IntegerField()


class ProjectEmployee(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    hours_worked = models.IntegerField()


    