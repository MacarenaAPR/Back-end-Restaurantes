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
            )
        ]

    def clean(self):
        if self.categoria and self.restaurante:
            if self.categoria.restaurante_id != self.restaurante_id:
                raise ValidationError({
                    "categoria": "La categoría seleccionada no pertenece al restaurante elegido."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
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
