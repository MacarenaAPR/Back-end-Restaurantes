from django.db import models
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
class Restaurante(models.Model):
    
    nombre_empresa = models.CharField(max_length=150)
    rut = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20)
    email_contacto = models.EmailField()
    
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    
    logo = CloudinaryField("logo", blank=True, null=True)
    
    slug = models.SlugField(unique=True)
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_empresa
    
class Categoria(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurante", "nombre"],
                name="unique_categoria_por_restaurante"
            )
        ]

    def __str__(self):
        return f"{self.nombre} - {self.restaurante.nombre_empresa}"

class Producto(models.Model):
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name="productos"
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="productos"
    )

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    condiciones = models.TextField(blank=True)

    precio = models.DecimalField(max_digits=8, decimal_places=0)

    imagen = CloudinaryField("imagen", blank=True, null=True)

    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)

    orden = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurante", "nombre"],
                name="unique_producto_por_restaurante"
            ),
            models.UniqueConstraint(
                fields=["restaurante", "categoria", "orden"],
                name="unique_orden_por_categoria"
            )
        ]

    def clean(self):
        if self.categoria and self.restaurante:
            if self.categoria.restaurante_id != self.restaurante_id:
                raise ValidationError({
                    "categoria": "La categoría seleccionada no pertenece al restaurante elegido."
                })

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.restaurante.nombre_empresa}"

class UsuarioRestaurante(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil_restaurante"
    )

    restaurante = models.ForeignKey(
        "Restaurante",
        on_delete=models.CASCADE,
        related_name="usuarios"
    )

    ROL_CHOICES = [
        ("dueno", "Dueño"),
        ("admin", "Administrador"),
        ("empleado", "Empleado"),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default="empleado"
    )

    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "restaurante")

    def __str__(self):
        return f"{self.user.email} - {self.restaurante.nombre_empresa} ({self.rol})"

class BitacoraProducto(models.Model):
    ACCIONES = [
        ("CREADO", "Creado"),
        ("EDITADO", "Editado"),
        ("ELIMINADO", "Eliminado"),
        ("DISPONIBLE", "Cambio de disponibilidad"),
        ("PRECIO", "Cambio de precio"),
        ("ORDEN", "Cambio de orden"),
    ]

    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    producto_id = models.IntegerField(null=True, blank=True)
    producto_nombre = models.CharField(max_length=150)
    usuario = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)

    accion = models.CharField(max_length=20, choices=ACCIONES)
    descripcion = models.TextField()

    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.accion} - {self.producto_nombre}"

class Reserva(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("rechazada", "Rechazada"),
        ("cancelada", "Cancelada"),
    ]

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name="reservas"
    )

    creada_por = models.ForeignKey(
        UsuarioRestaurante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservas_creadas"
    )

    gestionada_por = models.ForeignKey(
        UsuarioRestaurante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservas_gestionadas"
    )

    nombre_cliente = models.CharField(max_length=120)
    telefono = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)

    fecha = models.DateField()
    hora = models.TimeField()
    cantidad_personas = models.PositiveIntegerField()

    mensaje = models.TextField(blank=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="pendiente"
    )

    mesa_asignada = models.CharField(max_length=50, blank=True, null=True)
    observacion_admin = models.TextField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.nombre_cliente} - {self.fecha} {self.hora}"