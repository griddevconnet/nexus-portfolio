import time
from celery import shared_task
from django.utils import timezone
from .models import Conversation, Message, DeveloperSettings


@shared_task
def send_auto_reply(conversation_id, delay_seconds=3):
    """Send auto-reply to a conversation after a delay"""
    time.sleep(delay_seconds)
    
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        settings = DeveloperSettings.get_settings()
        
        if not settings.auto_reply_enabled:
            return
        
        # Auto-reply messages
        auto_replies = [
            "Thanks for reaching out! I will get back to you shortly.",
            "Got your message! I usually respond within a few hours.",
            "Appreciate you reaching out. I will review this and respond soon!",
            "Message received! Looking forward to chatting with you.",
            "Hey, thanks for connecting! I will reply as soon as I am available."
        ]
        
        import random
        reply_content = random.choice(auto_replies)
        
        # Create auto-reply message
        Message.objects.create(
            conversation=conversation,
            sender='dev',
            content=reply_content
        )
        
        conversation.updated_at = timezone.now()
        conversation.save()
        
    except Conversation.DoesNotExist:
        pass  # Conversation might have been deleted
