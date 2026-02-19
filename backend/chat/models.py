from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Conversation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    TAG_CHOICES = [
        ('project', 'Project'),
        ('hire', 'Hire'),
        ('collab', 'Collaboration'),
        ('greeting', 'Greeting'),
        ('other', 'Other'),
    ]

    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default='greeting')
    unread = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.client_name} - {self.created_at.strftime('%Y-%m-%d')}"
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()
    
    @property
    def message_count(self):
        return self.messages.count()


class Message(models.Model):
    SENDER_CHOICES = [
        ('client', 'Client'),
        ('dev', 'Developer'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.conversation.client_name} - {self.sender}: {self.content[:50]}..."
    
    def mark_as_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save()


class QuickReplyTemplate(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DeveloperSettings(models.Model):
    password = models.CharField(max_length=255, help_text="Password for developer dashboard")
    auto_reply_enabled = models.BooleanField(default=True)
    auto_reply_delay = models.IntegerField(default=3, help_text="Delay in seconds before auto-reply")
    
    def __str__(self):
        return "Developer Settings"
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={'password': 'nexus2025'}
        )
        return settings
