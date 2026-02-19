from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
import os

def developer_dashboard(request):
    # Read the original dev_chat.html file and serve it directly
    file_path = os.path.join(settings.BASE_DIR, '..', 'dev_chat.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("=== HTML CONTENT ANALYSIS ===")
            print("Has router.js script:", 'router.js' in content)
            print("Has api-client.js script:", 'api-client.js' in content)
            print("Has script tags:", '<script' in content)
            print("Script count:", content.count('<script'))
            print("=====================================")
            
            # Serve the HTML as-is without modifications
            return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponseNotFound("Developer dashboard not found")

def serve_static_files(request, path):
    # Serve static files from the parent directory
    file_system_path = os.path.join(settings.BASE_DIR, '..', path)
    
    # Debug logging
    print("=== STATIC FILE REQUEST ===")
    print("Path requested:", path)
    print("Full path:", file_system_path)
    print("Exists:", os.path.exists(file_system_path))
    print("Is file:", os.path.isfile(file_system_path) if os.path.exists(file_system_path) else "N/A")
    print("==========================")
    
    if os.path.exists(file_system_path) and os.path.isfile(file_system_path):
        # Determine content type based on file extension
        if path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.png'):
            content_type = 'image/png'
        elif path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.html'):
            content_type = 'text/html'
        else:
            content_type = 'application/octet-stream'
        
        try:
            with open(file_system_path, 'rb') as f:
                content = f.read()
                print("File served successfully!")
                return HttpResponse(content, content_type=content_type)
        except Exception as e:
            print("Error reading file:", e)
            return HttpResponseNotFound("Error reading file: " + str(e))
    else:
        # Try alternative paths for common files
        if path == 'nexus-logo.png':
            # Try public directory
            public_path = os.path.join(settings.BASE_DIR, '..', 'public', 'nexus-logo.png')
            print("Trying public path:", public_path)
            print("Public exists:", os.path.exists(public_path))
            if os.path.exists(public_path):
                with open(public_path, 'rb') as f:
                    return HttpResponse(f.read(), content_type='image/png')
        
        print("File not found!")
        return HttpResponseNotFound("File not found: " + path)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', include('chat.urls')),
    path('developer/', developer_dashboard, name='developer_dashboard'),
    # Serve root-level static files
    path('router.js', serve_static_files, {'path': 'router.js'}),
    path('api-client.js', serve_static_files, {'path': 'api-client.js'}),
    path('public/nexus-logo.png', serve_static_files, {'path': 'public/nexus-logo.png'}),
    # Put static handler first to ensure it's caught
    path('static/<path:path>', serve_static_files),
    # Test route to see if URL patterns are working
    path('test/', lambda request: HttpResponse("URL patterns working!")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
