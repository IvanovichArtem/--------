from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee', 'Сотрудник'),
        ('customer', 'Заказчик'),
    )
    phone_regex = RegexValidator(r'^\+375(25|29|33|44)\d{7}$')

    phone = models.CharField(max_length=20, blank=False, unique=True, validators=[phone_regex], help_text="Введите номер телефона в формате +375XXXXXXXXX")
    role = models.CharField(max_length=10, blank=False, choices=ROLE_CHOICES)
    
    def __str__(self) -> str:
        return self.username
    
class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает исполнителя'),
        ('in_progress', 'В процессе'),
        ('completed', 'Выполнена'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer = models.ForeignKey(User, on_delete=models.CASCADE,                related_name='created_tasks', limit_choices_to={'role': 'customer'})
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True, limit_choices_to={'role': 'employee'})
    report = models.TextField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.title} - {self.customer} - {self.assigned_to}"