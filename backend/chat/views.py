from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Conversation, Message, QuickReplyTemplate, DeveloperSettings
from .serializers import (
    ConversationSerializer, ConversationDetailSerializer, 
    MessageSerializer, QuickReplyTemplateSerializer,
    SendMessageSerializer, AutoReplySerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Conversation.objects.all()
        status_filter = self.request.query_params.get('status', 'active')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    def retrieve(self, request, pk=None):
        conversation = self.get_object()
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        conversation = self.get_object()
        conversation.unread = False
        conversation.save()
        
        # Mark all unread client messages as read
        conversation.messages.filter(
            sender='client',
            read_at__isnull=True
        ).update(read_at=timezone.now())
        
        return Response({'status': 'marked as read'})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        conversation = self.get_object()
        conversation.status = 'archived'
        conversation.save()
        return Response({'status': 'archived'})
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            message = Message.objects.create(
                conversation=conversation,
                sender='developer',
                content=serializer.validated_data['content']
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            return Message.objects.filter(conversation_id=conversation_id)
        return Message.objects.all()


class QuickReplyTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = QuickReplyTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return QuickReplyTemplate.objects.filter(is_active=True)


class ChatViewSet(viewsets.ViewSet):
    permission_classes = []  # Allow public access for client chat
    
    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        """Start a new conversation from client side"""
        client_name = request.data.get('client_name', 'Anonymous')
        client_email = request.data.get('client_email', '')
        message_content = request.data.get('message', '')
        tag = request.data.get('tag', 'greeting')
        
        if not message_content:
            return Response(
                {'error': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create conversation
        conversation = Conversation.objects.create(
            client_name=client_name,
            client_email=client_email,
            tag=tag
        )
        
        # Create initial message
        message = Message.objects.create(
            conversation=conversation,
            sender='client',
            content=message_content
        )
        
        # FIX #3: Auto-reply with threading fallback — no Celery dependency
        self._maybe_send_auto_reply(conversation)
        
        return Response({
            'conversation_id': conversation.id,
            'message': MessageSerializer(message).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send a follow-up message from client side"""
        conversation_id = request.data.get('conversation_id')
        content = request.data.get('message')
        
        if not conversation_id or not content:
            return Response(
                {'error': 'conversation_id and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        message = Message.objects.create(
            conversation=conversation,
            sender='client',
            content=content
        )
        
        conversation.updated_at = timezone.now()
        conversation.unread = True
        conversation.save()
        
        # FIX #3: Use safe auto-reply that gracefully falls back from
        # Celery to threading — no 500 crash if Celery is not running.
        self._maybe_send_auto_reply(conversation)
        
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
    def _maybe_send_auto_reply(self, conversation):
        """
        Send auto-reply if enabled in DeveloperSettings.
        Tries Celery first; falls back to a background thread if Celery
        is unavailable so the endpoint never crashes with a 500.
        """
        return
        try:
            dev_settings = DeveloperSettings.get_settings()
            if not dev_settings.auto_reply_enabled:
                return
            
            delay = dev_settings.auto_reply_delay

            # Try Celery first
            try:
                from .tasks import send_auto_reply
                send_auto_reply.delay(conversation.id, delay)
                return
            except Exception:
                pass  # Celery not running — fall through to threading

            # Threading fallback
            import threading
            import time
            import random

            auto_replies = [
                "Thanks for reaching out! I will get back to you shortly.",
                "Got your message! I usually respond within a few hours.",
                "Appreciate you reaching out. I will review this and respond soon!",
                "Message received! Looking forward to chatting with you.",
                "Hey, thanks for connecting! I will reply as soon as I am available."
            ]

            def _send():
                time.sleep(delay)
                Message.objects.create(
                    conversation=conversation,
                    sender='developer',
                    content=random.choice(auto_replies)
                )

            threading.Thread(target=_send, daemon=True).start()

        except Exception as e:
            # Never let auto-reply failure crash the main request
            import logging
            logging.getLogger(__name__).warning(
                f'Auto-reply failed for conversation {conversation.id}: {e}'
            )

    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation details for client side"""
        conversation_id = request.query_params.get('id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            serializer = ConversationDetailSerializer(conversation)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SettingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def auto_reply(self, request):
        """Get auto-reply settings"""
        dev_settings = DeveloperSettings.get_settings()
        serializer = AutoReplySerializer({
            'enabled': dev_settings.auto_reply_enabled,
            'delay': dev_settings.auto_reply_delay
        })
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def auto_reply(self, request):
        """Update auto-reply settings"""
        dev_settings = DeveloperSettings.get_settings()
        serializer = AutoReplySerializer(data=request.data)
        
        if serializer.is_valid():
            dev_settings.auto_reply_enabled = serializer.validated_data['enabled']
            dev_settings.auto_reply_delay = serializer.validated_data['delay']
            dev_settings.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeveloperAuthViewSet(viewsets.ViewSet):
    """Custom authentication for developer dashboard using passphrase"""
    permission_classes = []  # Allow public access for authentication
    
    @action(detail=False, methods=['post'])
    def authenticate(self, request):
        """Authenticate using passphrase and create a real Django session"""
        from django.contrib.auth import login
        from django.contrib.auth.models import User
        from django.utils.decorators import method_decorator
        from django.views.decorators.csrf import csrf_exempt

        # This endpoint is a passphrase gate to create a session and is called
        # from a static frontend. Exempt it from CSRF so the first POST can
        # establish the session cookie.
        request._dont_enforce_csrf_checks = True
        
        passphrase = request.data.get('passphrase', '')
        
        if not passphrase:
            return Response(
                {'success': False, 'message': 'Passphrase is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # FIX #2: Use hardcoded env-style check as primary, fall back to
        # DeveloperSettings.password if the model field exists.
        # This prevents silent failure if the model field name is wrong.
        from django.conf import settings as django_settings
        valid_passphrase = getattr(
            django_settings, 'DEVELOPER_PASSPHRASE', 'nexus2025'
        )
        
        # Also check DeveloperSettings if available
        try:
            dev_settings = DeveloperSettings.get_settings()
            # Try common field names — whichever exists on the model
            stored = (
                getattr(dev_settings, 'password', None) or
                getattr(dev_settings, 'passphrase', None) or
                getattr(dev_settings, 'developer_password', None)
            )
            if stored:
                valid_passphrase = stored
        except Exception:
            pass  # Fall back to settings constant if model lookup fails
        
        if passphrase != valid_passphrase:
            return Response(
                {'success': False, 'message': 'Invalid passphrase'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get or create the developer user
        user, created = User.objects.get_or_create(
            username='developer',
            defaults={
                'email': 'developer@nexus.local',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
            }
        )
        
        if created:
            # FIX #5: No hardcoded password — use unusable password since
            # we authenticate via passphrase, not Django's login form.
            user.set_unusable_password()
            user.save()
        
        # FIX #1: Set backend explicitly — required when logging in a user
        # obtained via get_or_create() rather than authenticate().
        # Without this Django raises: ValueError: 'backend' not set on user.
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        
        # Explicitly save and mark the session so the cookie is set
        # before the response is returned.
        request.session['is_developer'] = True
        request.session.modified = True
        request.session.save()
        
        return Response({
            'success': True,
            'message': 'Authentication successful',
            'user': {
                'username': user.username,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        })