from django.contrib import admin
from .models import Restaurante, Categoria, Producto, UsuarioRestaurante

@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ("nombre_empresa", "ciudad", "activo", "fecha_creacion")
    prepopulated_fields = {"slug": ("nombre_empresa",)}
    search_fields = ("nombre_empresa", "ciudad")
    list_filter = ("activo", "ciudad")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "restaurante", "orden", "activa")
    list_filter = ("restaurante", "activa")
    ordering = ("restaurante", "orden")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "restaurante", "categoria", "precio", "disponible")
    list_filter = ("restaurante", "categoria", "disponible")
    search_fields = ("nombre",)
    ordering = ("restaurante", "orden")


@admin.register(UsuarioRestaurante)
class UsuarioRestauranteAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurante", "rol", "activo")
    list_filter = ("rol", "restaurante", "activo")