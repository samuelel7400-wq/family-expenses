from django.urls import path
from .views import home, delete_expense

urlpatterns = [
    path('', home, name='home'),
    path('delete/<int:id>/', delete_expense, name='delete_expense'),
]