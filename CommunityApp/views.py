from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import *
from .forms import *


def loginpage(request):

    page = 'loginpage'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        
        else:
            messages.error(request, 'Username does not exist')

    context = {'page': page} 

    return render(request, 'CommunityApp/login_reg.html', context)


def logoutpage(request):
    logout(request)
    return redirect('home')


def registerpage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occured during registration.")
    context = {'form': form}
    return render(request, "CommunityApp/login_reg.html", context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) | 
        Q(description__icontains=q) 
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__name__icontains = q))

    context = {"rooms": rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'CommunityApp/home.html', context=context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room, 
            body = request.POST.get( 'body' )
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {"room": room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'CommunityApp/room.html', context=context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'CommunityApp/profile.html', context)


@login_required(login_url="loginpage")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('home')
    context = {'form': form, 'topics':topics}
    return render(request, 'CommunityApp/room_form.html', context)


@login_required(login_url='loginpage')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    form  = RoomForm(instance=room)

    if request.user !=  room.host:
        return HttpResponse('Your are not allowed  to edit this')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get( 'name' )
        room.topic = topic
        room.description = request.POST.get( 'description' )
        room.save()
        return redirect('home')
    context = {'form': form, 'topics':topics, 'room': room}
    return render(request, 'CommunityApp/room_form.html', context)


@login_required(login_url="loginpage")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user !=  room.host:
        return HttpResponse('Your are not allowed  to edit this')
    
    if request.method=='POST':
        room.delete()
        return redirect('home')
    
    context = {'obj': room}
    return render(request, 'CommunityApp/delete.html', context)


@login_required(login_url="loginpage")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user !=  message.user:
        return HttpResponse('Your are not allowed  to edit this')
    
    if request.method=='POST':
        message.delete()
        return redirect('home')
    
    context = {'obj': message}
    return render(request, 'CommunityApp/delete.html', context)


@login_required(login_url="loginpage")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'CommunityApp/update_user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q)

    context = {'topics':  topics}
    return render(request, 'CommunityApp/topics.html', context)


def activityPage(request):

    room_messages = Message.objects.all()

    context = {'room_messages': room_messages}
    return render(request, 'CommunityApp/activity.html', context)