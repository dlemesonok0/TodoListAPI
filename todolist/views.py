from django.shortcuts import render
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from todolist import serializers
from todolist.models import Task


class TodoListView(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = [permissions.AllowAny]