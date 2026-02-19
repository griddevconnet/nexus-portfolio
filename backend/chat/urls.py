from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationViewSet, MessageViewSet, 
    QuickReplyTemplateViewSet, ChatViewSet, SettingsViewSet,
    DeveloperAuthViewSet
)

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'templates', QuickReplyTemplateViewSet, basename='template')
router.register(r'', ChatViewSet, basename='chat')

settings_router = DefaultRouter()
settings_router.register(r'settings', SettingsViewSet, basename='settings')

auth_router = DefaultRouter()
auth_router.register(r'auth', DeveloperAuthViewSet, basename='developer-auth')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(settings_router.urls)),
    path('', include(auth_router.urls)),
]
