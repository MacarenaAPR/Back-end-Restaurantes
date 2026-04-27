"""
URL configuration for core project.

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
#from django.conf import settings
from django.urls import path
from menu.views import menu_api
#from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from menu.views import menu_api,CustomLoginView, MiRestauranteView,ProductoUpdateView, LogoutView,ProductoCreateView, ActualizarDisponibilidadProductoView, EliminarProductoView, HistorialBitacoraView
from menu.views import CrearReservaPublicaView, ReservasDashboardView,UsuariosView, CrearReservaManualView, ActualizarReservaView, ConfiguracionRestauranteView, UploadLogoView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 login custom
    path("api/login/", CustomLoginView.as_view(), name="login"),

    # 🔄 refresh token
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 🏪 dashboard privado
    path("api/mi-restaurante/", MiRestauranteView.as_view(), name="mi-restaurante"),

    # 🌐 menu público
    path("api/menu/<slug:slug>/", menu_api),

    #logoyt
     path("api/logout/", LogoutView.as_view(), name="logout"),
    
    #Productos
    path(
    "api/mi-restaurante/productos/<int:id>/",
    ActualizarDisponibilidadProductoView.as_view(),
    name="actualizar-disponibilidad-producto"
    ),

    #PRODUCTOS ELMINADOS
    path(
    "api/mi-restaurante/productos/<int:id>/eliminar/",
    EliminarProductoView.as_view(),
    name="eliminar-producto"
    ),

    # AGREGAR PRODUCTO
    path(
        "api/mi-restaurante/productos/agregar/",
        ProductoCreateView.as_view(),
        name="agregar-producto"
    ),
    
    # EDITAR PRODUCTO
    path(
        "api/mi-restaurante/productos/<int:id>/actualizar/",
        ProductoUpdateView.as_view(),
        name="actualizar-producto"
    ),

    #BITACORA 
    path("api/historial/", HistorialBitacoraView.as_view()),


    #RESERVAS

    path(
        "api/reservas/<slug:slug>/",
        CrearReservaPublicaView.as_view(),
        name="crear-reserva-publica"
    ),

    path(
        "api/mi-restaurante/reservas/",
        ReservasDashboardView.as_view(),
        name="reservas-dashboard"
    ),

    path(
        "api/mi-restaurante/reservas/crear/",
        CrearReservaManualView.as_view(),
        name="crear-reserva-manual"
    ),

    path(
        "api/mi-restaurante/reservas/<int:reserva_id>/",
        ActualizarReservaView.as_view(),
        name="actualizar-reserva"
    ),

    #SUBIR FOTO
    path("api/mi-restaurante/upload-logo/", UploadLogoView.as_view()),

    #CONFIGURACION DEL RESTAURANTE 
    path("api/mi-restaurante/configuracion/", ConfiguracionRestauranteView.as_view()),


    #USUARIOS CONFIGURACION SEGUN PERMISOS
    path("api/mi-restaurante/usuarios/<int:user_id>/", UsuariosView.as_view()),
    path("api/mi-restaurante/usuarios/", UsuariosView.as_view()),

] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
