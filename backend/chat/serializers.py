from rest_framework import serializers
from .models import Conversation, Message, QuickReplyTemplate


class MessageSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'read_at']
    
    def get_timestamp(self, obj):
        return obj.created_at.isoformat()


class ConversationSerializer(serializers.ModelSerializer):
    last_message_preview = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'client_name', 'client_email', 'status', 'tag', 
                 'unread', 'created_at', 'updated_at', 'last_message_preview', 
                 'timestamp', 'unread_count']
    
    def get_last_message_preview(self, obj):
        last_msg = obj.last_message
        if last_msg:
            return last_msg.content[:100] + ('...' if len(last_msg.content) > 100 else '')
        return "No messages yet"
    
    def get_timestamp(self, obj):
        return obj.updated_at.isoformat()
    
    def get_unread_count(self, obj):
        return obj.messages.filter(sender='client', read_at__isnull=True).count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'client_name', 'client_email', 'status', 'tag', 
                 'unread', 'created_at', 'updated_at', 'messages']


class QuickReplyTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickReplyTemplate
        fields = ['id', 'name', 'content', 'created_at', 'is_active']


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=2000)
    conversation_id = serializers.IntegerField(required=False)


class AutoReplySerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    delay = serializers.IntegerField(min_value=1, max_value=60)
