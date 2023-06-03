

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Chat
import openai

openai_api_key = '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'
openai.api_key = openai_api_key

# Create your views here.
def ask_chatbot(message):
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {"role": "system", "content": "You are an helpful assistant."},
            {"role": "user", "content": message}
        ]
    )
    answer = response.choices[0].message.content.strip()
    return answer

def chatbot(request):
    chats = Chat.objects.filter(user = request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_chatbot(message)

        chat = Chat(user = request.user, message = message, response = response, created_at = timezone.now())
        chat.save()
        return JsonResponse({ 'message': message, 'response': response})
    return render(request, 'chatbot.html', { 'chats': chats })

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username = username, password = password)

        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Wrong credentials'
            return render(request, 'login.html', { 'error_message': error_message })
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message  = 'Error creating account'
                return render(request, 'register.html', { "error_message": error_message})
        else:
            error_message = "Password don't match"
            return render(request, 'register.html', { "error_message": error_message })
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')