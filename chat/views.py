from django.shortcuts import render, redirect, get_object_or_404
from .models import Conversation
import uuid

def index(request):
    return redirect('chat', conversation_id=uuid.uuid4())

def chat_view(request, conversation_id):
    # Ensure conversation exists or create it?
    # For a smoother UX, we might create it on the first message in consumer, 
    # but to render the page, we might just pass the ID.
    # However, to show history, the object should exist.
    
    conversation, created = Conversation.objects.get_or_create(id=conversation_id)
    
    # Get recent conversations for sidebar
    recent_chats = Conversation.objects.all()[:20] 
    
    return render(request, 'chat/index.html', {
        'conversation': conversation,
        'recent_chats': recent_chats
    })
