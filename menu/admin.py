from django.contrib import admin
from .models import Restaurante, Categoria, Producto, UsuarioRestaurante, BitacoraProducto

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

@admin.register(BitacoraProducto)
class BitacoraProductoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "accion",
        "producto_nombre",
        "restaurante",
        "usuario",
        "fecha",
    )

    list_filter = (
        "accion",
        "restaurante",
        "fecha",
    )

    search_fields = (
        "producto_nombre",
        "descripcion",
        "usuario__username",
        "restaurante__nombre_empresa",
    )

    readonly_fields = (
        "restaurante",
        "producto_id",
        "producto_nombre",
        "usuario",
        "accion",
        "descripcion",
        "valor_anterior",
        "valor_nuevo",
        "fecha",
    )

    ordering = ("-fecha",)

    date_hierarchy = "fecha"