from django.urls import path,include 
from . import views 
from rest_framework.routers import DefaultRouter 
from .views import TaskViewSet

router = DefaultRouter() 
router.register(r'tasks',TaskViewSet)

urlpatterns = [
    path('list/', views.index, name='index'), 
    path('update_task/<str:pk>/', views.updateTask, name='update_task'),
    path('delete/<str:pk>/', views.deleteTask, name='delete'),
    path('login/', views.login_view, name='login'), 
    path('register/', views.register, name='register'), 
    path('__debug__', include('debug_toolbar.urls')),
    path('', include(router.urls)),
]        