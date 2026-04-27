from django.contrib import admin
from menu.models import Restaurante, Categoria, Producto, UsuarioRestaurante, BitacoraProducto,Reserva,HorarioAtencion,MetodoPago,Mesa


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre_empresa", "slug", "telefono", "ciudad", "activo", "fecha_creacion")
    list_filter = ("activo", "ciudad")
    search_fields = ("nombre_empresa", "rut", "telefono", "email_contacto", "slug")
    prepopulated_fields = {"slug": ("nombre_empresa",)}
    ordering = ("nombre_empresa",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "restaurante", "orden", "activa")
    list_filter = ("activa", "restaurante")
    search_fields = ("nombre", "restaurante__nombre_empresa")
    ordering = ("restaurante", "orden")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "restaurante",
        "categoria",
        "precio",
        "disponible",
        "destacado",
        "orden",
        "fecha_creacion",
    )
    list_filter = ("disponible", "destacado", "restaurante", "categoria")
    search_fields = ("nombre", "descripcion", "restaurante__nombre_empresa", "categoria__nombre")
    ordering = ("restaurante", "categoria", "orden")
    readonly_fields = ("fecha_creacion",)


@admin.register(UsuarioRestaurante)
class UsuarioRestauranteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "restaurante", "rol", "activo", "creado_por", "fecha_creacion")
    list_filter = ("rol", "activo", "restaurante")
    search_fields = ("user__username", "user__email", "restaurante__nombre_empresa")
    ordering = ("restaurante", "rol")
    readonly_fields = ("fecha_creacion",)


@admin.register(BitacoraProducto)
class BitacoraProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurante", "producto_nombre", "accion", "usuario", "fecha")
    list_filter = ("accion", "restaurante", "fecha")
    search_fields = ("producto_nombre", "descripcion", "usuario__username", "usuario__email")
    ordering = ("-fecha",)
    readonly_fields = ("fecha",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "restaurante",
        "nombre_cliente",
        "telefono",
        "fecha",
        "hora",
        "cantidad_personas",
        "estado",
        "mesa_asignada",
        "creada_por",
        "gestionada_por",
        "fecha_creacion",
    )
    list_filter = ("estado", "fecha", "restaurante")
    search_fields = (
        "nombre_cliente",
        "telefono",
        "email",
        "mesa_asignada",
        "restaurante__nombre_empresa",
    )
    ordering = ("fecha", "hora")
    readonly_fields = ("fecha_creacion", "fecha_actualizacion")


@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "restaurante",
        "dia",
        "hora_apertura",
        "hora_cierre",
        "cerrado",
        "activo",
    )
    list_filter = ("restaurante", "dia", "cerrado", "activo")
    search_fields = ("restaurante__nombre_empresa",)
    ordering = ("restaurante", "dia")


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurante", "nombre", "activo")
    list_filter = ("restaurante", "activo")
    search_fields = ("nombre", "restaurante__nombre_empresa")
    ordering = ("restaurante", "nombre")


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurante", "numero", "nombre", "activa")
    list_filter = ("restaurante", "activa")
    search_fields = ("nombre", "restaurante__nombre_empresa")
    ordering = ("restaurante", "numero")