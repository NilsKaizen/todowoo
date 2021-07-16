from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate as django_auth
from django.contrib.auth import logout as django_logout
from .forms import TodoForm
from .models import Todo
from django.utils import timezone

def home(request):
    return render(request, 'todos/home.html')


def signup_user(request):
    form = UserCreationForm()
    if request.method == "GET":
        return render(request,'todos/signup_user.html', {'form': form})
    else: 
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], '',request.POST['password1'])
                user.save()
                django_login(request, user)
                return redirect('current_todos')

            except IntegrityError:
                return render(request, 'todos/signup_user.html', {'form': form, 'error': 'User already taken, please choose another username'})

        else: 
            print('pass didnt match')
            return render(request, 'todos/signup_user.html', {'form': form, 'error': 'Passwords didn\'t match'})

def logout(request):
    if request.method == "POST":
        django_logout(request)

        return redirect('home')


def login(request):

    form = AuthenticationForm()

    if request.method == "GET":
        return render(request, 'todos/login.html', {'form': form})
    else:
        user = django_auth(
               request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todos/login.html', {'form': form, 'error': "Username or password incorrect"})
        else:
            django_login(request, user)
            return redirect('current_todos')

def create_todo(request):

    if request.method == "GET":
        return render(request, 'todos/create_todo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todos/create_todo.html', {'form': TodoForm(), 'error': "Wrong data inserted in the fields. Try again"})


def view_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method =="GET":
        
        form = TodoForm(instance=todo)
        return render(request, 'todos/view_todo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todos/create_todo.html', {'form': TodoForm(), 'error': "Wrong data inserted in the fields. Try again"})


def complete_todo(request, todo_pk):

    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == "POST":
        todo.date_todo = timezone.now()
        todo.save()

        return redirect('current_todos')


def delete_todo(request, todo_pk):

    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == "POST":
        todo.delete()

        return redirect('current_todos')


def current_todos(request):

    todos = Todo.objects.filter(
        user=request.user, date_todo=None).order_by('-important','date_created')

    return render(request, 'todos/current_todos.html', {'todos': todos})


def completed_todos(request):

    todos = Todo.objects.filter(
        user=request.user,).exclude(date_todo=None).order_by('-important', '-date_created')

    return render(request, 'todos/completed_todos.html', {'todos': todos})


def created_todos(request):

    todos = Todo.objects.all(user=request.user).order_by('-date_created')

    return render(request, 'todos/created_todos.html', {'todos': todos})
