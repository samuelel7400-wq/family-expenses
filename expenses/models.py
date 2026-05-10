from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Expense(models.Model):
    PERSON_CHOICES = [
        ('Dad', 'Dad'),
        ('Mom', 'Mom'),
    ]

    person = models.CharField(max_length=10, choices=PERSON_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=100, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.person} - {self.category} - ₹{self.amount}"