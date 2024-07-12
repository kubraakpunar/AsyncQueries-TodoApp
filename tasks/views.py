import stat
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from h11 import Response
from .models import Task
from .forms import TaskForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets 
from .serializer import TaskSerializer
import aiohttp 
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from asgiref.sync import sync_to_async

@login_required
def index(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            print("Görev başarıyla kaydedildi.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'task': str(task)})
            else:
                return redirect('index')
        else:
            print("Form geçersiz:", form.errors)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            context = {'page_obj': page_obj, 'form': form}
            return render(request, 'tasks/list.html', context)
    
    task_list = Task.objects.filter(user=request.user).order_by('-id')
    paginator = Paginator(task_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tasks = list(page_obj.object_list.values('id', 'title', 'complete'))
        return JsonResponse({
            'tasks': tasks,
            'has_next': page_obj.has_next()
        })

    form = TaskForm()
    context = {'page_obj': page_obj, 'form': form}
    return render(request, 'tasks/list.html', context)


@login_required
def updateTask(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    form = TaskForm(instance=task)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('list')
    context = {'form': form}
    return render(request, 'tasks/update_task.html', context)

@login_required
def deleteTask(request, pk):
    item = get_object_or_404(Task, id=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('list')
    context = {'item': item}
    return render(request, 'tasks/delete.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()  
    serializer_class = TaskSerializer
    chunk_size = 500

    async def batch_create_tasks(self, tasks):
        tasks_data = [self.serializer_class(task).data for task in tasks]
        async with aiohttp.ClientSession() as session: #http istemci oturumu olusturulur 
            for chunk in [tasks[i:i + self.chunk_size] for i in range(0, len(tasks), self.chunk_size)]:  #task listesi parçalara bolunur or.500
                tasks_data = [self.serializer_class(task).data for task in chunk]
                async with session.post('https://http://127.0.0.1:8000/api/tasks/batch/', json=tasks_data) as response:
                    if response.status == 201:
                        created_tasks = await response.json()
                        print(f"{len(created_tasks)} tasks created successfully.")
                    else:
                        print(f"Error creating tasks: {response.status}")

    async def create(self, request, *args, **kwargs):
            tasks = []
            for _ in range(1000000):
                tasks.append(Task())
            
            await self.batch_create_tasks(tasks)

            return Response(status=stat.HTTP_201_CREATED)
    
