from django.db import models
from django.contrib.auth.models import User
# Default Python Models for Auto API

class RouteExclusion(models.Model):
    """Model for URL Routes"""
    required_token = models.BooleanField(default = False)
    route = models.CharField(unique=True, max_length=255)
    is_enabled = models.BooleanField(default = False)

    def __str__(self):
        remarks = ""
        if self.is_enabled == True:
            remarks = "Enabled"
        else:
            remarks = "Disabled"

        return remarks + " : " + self.route

class AppLogs(models.Model):
    """Model for application logs, whether API Level or Function Level"""
    time_stamp = models.TextField(default=None, null=True, blank=True)
    log_type = models.TextField(default=None, null=True, blank=True)
    level = models.TextField(default=None, null=True, blank=True)
    source = models.TextField(default=None, null=True, blank=True)
    message = models.TextField(default=None, null=True, blank=True)
    user_id = models.TextField(default=None, null=True, blank=True)
    session_id = models.TextField(default=None, null=True, blank=True)
    ip_address = models.TextField(default=None, null=True, blank=True)
    request_method = models.TextField(default=None, null=True, blank=True)
    request_path = models.TextField(default=None, null=True, blank=True)
    response_status = models.TextField(default=None, null=True, blank=True)
    data = models.TextField(default=None, null=True, blank=True)
    error_type = models.TextField(default=None, null=True, blank=True)
    error_message = models.TextField(default=None, null=True, blank=True)
    execution_time = models.TextField(default=0.00, null=True, blank=True)

    def __str__(self):
        return f"{self.time_stamp}"
    
class StackTrace(models.Model):
    app_log = models.ForeignKey(AppLogs, on_delete=models.CASCADE)
    description = models.TextField()

class JsonDataset(models.Model):
    sequential_ecg = models.TextField(default = None, null = True)
    remarks = models.TextField(default = 'No Disease', null = False)

    def __str__(self):
        return  str(self.pk) + "-" + self.remarks
    
class TestingJsonDataset(models.Model):

    sequential_ecg = models.TextField(default = None, null = True)
    correct_remarks = models.TextField(default = 'No Disease', null = False)
    answered_remarks = models.TextField(default = 'No Disease', null = False)

    def __str__(self):
        return  str(self.pk) + "-" + self.correct_remarks
    

class Patient(models.Model):

    first_name = models.CharField(max_length=255, null = False)
    middle_name = models.CharField(max_length=255, null = True, default = None)
    last_name = models.CharField(max_length=255, null = False)
    birth = models.DateField(default = None)

    def __str__(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'

class Cardiologist(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    suffixes = models.TextField(default = None, null = True)
    e_signature = models.FileField(upload_to='cardiologist_signature', null = True, default = None)

    def __str__(self):
        return f'{self.user}'
    
class Prediction(models.Model):

    attending_physician = models.ForeignKey(Cardiologist, on_delete=models.CASCADE, null = True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null = True)
    sequential_ecg = models.TextField(default = None, null = False)
    remarks = models.TextField(default = None, null = False)
    recommendations = models.TextField(default = None, null = True)

class ModelInfo(models.Model):

    last_trained_state = models.DateField(default = None)
    accuracy = models.TextField(default = None)
    precision = models.TextField(default = None)
    recall = models.TextField(default = None)
    f1_score = models.TextField(default = None)
    json_info = models.TextField(default = None, null = True)


    def __str__(self):
        return f'{self.last_trained_state}'

