# Nexus Chat Backend

Django REST API backend for the Nexus chat system with PostgreSQL database.

## Setup Instructions

### 1. Start PostgreSQL with Docker
```bash
cd ..
docker-compose up -d
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Load Initial Data
```bash
python manage.py loaddata initial_data.json  # Optional
```

### 7. Start Development Server
```bash
python manage.py runserver
```

## API Endpoints

### Developer Dashboard (Requires Authentication)
- `GET /api/chat/conversations/` - List all conversations
- `GET /api/chat/conversations/{id}/` - Get conversation details
- `POST /api/chat/conversations/{id}/mark_read/` - Mark conversation as read
- `POST /api/chat/conversations/{id}/archive/` - Archive conversation
- `POST /api/chat/conversations/{id}/send_message/` - Send message
- `GET /api/chat/templates/` - List quick reply templates
- `POST /api/chat/templates/` - Create quick reply template
- `GET /api/chat/settings/auto_reply/` - Get auto-reply settings
- `POST /api/chat/settings/auto_reply/` - Update auto-reply settings

### Client Chat (Public)
- `POST /api/chat/start_conversation/` - Start new conversation
- `POST /api/chat/send_message/` - Send message to existing conversation
- `GET /api/chat/conversation/?id={conversation_id}` - Get conversation details

## Features

- ✅ PostgreSQL database with Docker
- ✅ Django REST Framework API
- ✅ CORS support for frontend integration
- ✅ Auto-reply functionality
- ✅ Quick reply templates
- ✅ Message read/unread status
- ✅ Conversation archiving
- ✅ Admin panel for management
- ✅ Celery ready for async tasks

## Development

### Admin Panel
Access at: `http://localhost:8000/admin/`

### API Documentation
Use Django REST Framework's built-in browsable API at `http://localhost:8000/api/chat/`

### Database Models
- **Conversation**: Chat sessions with clients
- **Message**: Individual messages in conversations
- **QuickReplyTemplate**: Reusable message templates
- **DeveloperSettings**: Configuration for auto-reply and password

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS` in settings
3. Use PostgreSQL with proper credentials
4. Set up Celery for async tasks
5. Configure static files serving
6. Set up proper CORS origins
