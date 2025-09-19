from django.db import router
from django.urls import path
from rest_framework.routers import DefaultRouter

from todolist import views
from todolist.serializers import TaskSerializer
from todolist.views import TodoListView

router = DefaultRouter()
router.register('tasks', TodoListView, basename="task")

urlpatterns = router.urls
