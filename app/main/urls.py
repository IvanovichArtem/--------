from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserCreateView, EmployeeListView, TaskListCreateView, TaskCompleteView, TaskUpdateView, TaskAssignView

urlpatterns = [
    path('create_user/', UserCreateView.as_view(), name='user_create'),
    path('employees/', EmployeeListView.as_view(), name='employee_list'),

    path('tasks/', TaskListCreateView.as_view()),
    path('tasks/<int:pk>', TaskUpdateView.as_view()),
    path('tasks/<int:pk>/complete/', TaskCompleteView.as_view()),
    path('tasks/<int:pk>/assign/', TaskAssignView.as_view()),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]