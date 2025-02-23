from django.db import models
from django.core.validators import RegexValidator, EmailValidator, FileExtensionValidator

#  Clients Table
class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=50, validators=[RegexValidator(regex=r'^\+?[\d\-x\.()]+$', message="Invalid phone number")])

#  Projects Table (with auto-incrementing Job ID)
class Project(models.Model):
    JOB_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]

    project_id = models.AutoField(primary_key=True)  # Auto-incrementing Job ID
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="projects")
    building_type = models.CharField(max_length=50, choices=[('Residential', 'Residential'), ('Commercial', 'Commercial'), ('Industrial', 'Industrial')])
    address = models.CharField(max_length=255)
    job_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    area_size_sqft = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_gain = models.FloatField()
    status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES, default='pending')

# Cost tables
class Cost(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True)
    body_paint_cost = models.FloatField(default=0.0)
    trim_paint_cost = models.FloatField(default=0.0)
    other_paint_cost = models.FloatField(default=0.0)
    supplies_cost = models.FloatField(default=0.0)
    additional_service_cost = models.FloatField(default=0.0)

    def total_cost(self):
       return self.body_paint_cost + self.trim_paint_cost + self.other_paint_cost + self.supplies_cost + self.additional_service_cos
    

#  Additional Services Table
class AdditionalService(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="services")
    service_name = models.CharField(max_length=100)
    service_cost = models.FloatField()

# Employees Table (with first & last name)
class Employee(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    wage = models.FloatField()
    hours_worked = models.IntegerField()

# Employee table
class ProjectEmployee(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    hours_worked = models.IntegerField()

class PDFDocument(models.Model):
    file = models.FileField(upload_to='pdfs/', validators=[
        FileExtensionValidator(allowed_extensions=['pdf', 'csv'])
    ])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"File uploaded at {self.uploaded_at}"

    class Meta:
        ordering = ['-uploaded_at']
    