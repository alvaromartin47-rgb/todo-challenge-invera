from .models import Task
from .serializer import TaskSerializer
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.db import models

class TaskFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
    
    class Meta:
        model = Task
        fields = ['done', 'created_at']

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
