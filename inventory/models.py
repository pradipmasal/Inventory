from django.db import models
from django.contrib.auth.models import User

class Component(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='components/', blank=True, null=True)

    def __str__(self):
        return self.name

class IssuedComponent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity_issued = models.PositiveIntegerField()
    issue_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.component.name} issued to {self.user.username}"
