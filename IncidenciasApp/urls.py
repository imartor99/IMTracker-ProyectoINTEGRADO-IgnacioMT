"""
URL configuration for IncidenciasApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import logout_then_login
from incidencias.views import  login_view
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # URL para el admin
    path('admin/', admin.site.urls),

    path('', include(('incidencias.urls', 'incidencias'), namespace='incidencias')),

    # URL para login
    path('login/', login_view, name='login'),

    # Rutas para las vistas de autenticación predeterminadas de Django
    path('accounts/', include('django.contrib.auth.urls')),

    #Logout después del login
    path('logout/', logout_then_login, name='logout'),

    # Internacionalización
    # He añadido esta ruta de Django para habilitar la vista 'set_language', que recibe la petición del selector de idiomas
    path('i18n/', include('django.conf.urls.i18n')),

]

#para mostrar imagenes
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)