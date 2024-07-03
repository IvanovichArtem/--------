from rest_framework import generics, permissions, views
from .models import User, Task
from .serializers import UserSerializer, TaskSerializer, EmployeeSerializer
from .permissions import IsCustomerAndAuthenticated, IsEmployeeAndAuthenticated
from django.db.models import Q
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework import status

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsEmployeeAndAuthenticated] 
    
class EmployeeListView(generics.ListAPIView):
    queryset = User.objects.filter(role='employee')
    serializer_class = EmployeeSerializer
    permission_classes = [IsCustomerAndAuthenticated]

class TaskListCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'employee':
            queryset = Task.objects.filter(Q(assigned_to=user) | Q(assigned_to=None))
        elif user.role == 'customer':
            queryset = Task.objects.filter(customer=user)
        else:
            queryset = Task.objects.none()

        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated or request.user.role != 'customer':
            return Response({'detail': "Can't create tasks."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCompleteView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'pk'
    permission_classes = [IsEmployeeAndAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if obj.assigned_to != user:
            raise PermissionDenied('You do not have permission to complete this task.')
        return obj

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.status == "completed":
            return Response({"error": "Task already completed"}, status=status.HTTP_400_BAD_REQUEST)
        
        report_in_request = request.data.get('report', None)
        if not instance.report and not report_in_request:
            return Response({'error': 'Report field cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            'report': report_in_request,
            'status': "completed"
        }

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
    
class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == 'customer' and obj.customer != user:
            raise PermissionDenied('You do not have permission to update this task.')
        if user.role == 'employee' and obj.assigned_to != user:
            raise PermissionDenied('You do not have permission to update this task.')
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        
        if instance.status == "completed":
            return Response({'error': 'Cannot update completed task'}, status=status.HTTP_400_BAD_REQUEST)
        
        data.pop('customer', None)
        data.pop('assigned_to', None)

        serializer = self.get_serializer(instance, data=data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    
class TaskAssignView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'pk'
    permission_classes = [IsEmployeeAndAuthenticated]

    def get_object(self):
        obj = super().get_object()
        return obj

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.status == "completed":
            return Response({'error': 'Cannot update completed task'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = self.request.user

        if instance.assigned_to is not None and instance.assigned_to != user:
            return Response({"error": "Task is already assigned to another user"}, status=status.HTTP_400_BAD_REQUEST)
        if instance.status == "completed":
            return Response({"error": "Task is already completed"}, status=status.HTTP_400_BAD_REQUEST)

        data = {'assigned_to': user.id, "status": "in_progress"}
        
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)