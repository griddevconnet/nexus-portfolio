from django.contrib import admin
from .models import Conversation, Message, QuickReplyTemplate, DeveloperSettings


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_email', 'status', 'tag', 'unread', 'created_at', 'updated_at']
    list_filter = ['status', 'tag', 'unread', 'created_at']
    search_fields = ['client_name', 'client_email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'content_preview', 'created_at', 'read_at']
    list_filter = ['sender', 'created_at', 'read_at']
    search_fields = ['content', 'conversation__client_name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + ('...' if len(obj.content) > 100 else '')
    content_preview.short_description = 'Content'


@admin.register(QuickReplyTemplate)
class QuickReplyTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + ('...' if len(obj.content) > 100 else '')
    content_preview.short_description = 'Content'


@admin.register(DeveloperSettings)
class DeveloperSettingsAdmin(admin.ModelAdmin):
    list_display = ['password_display', 'auto_reply_enabled', 'auto_reply_delay']
    readonly_fields = ['id']
    
    def password_display(self, obj):
        return '••••••••' if obj.password else 'Not set'
    password_display.short_description = 'Password'
