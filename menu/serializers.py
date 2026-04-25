from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UsuarioRestaurante
from rest_framework import serializers
from .models import Producto, Categoria, Reserva


class ReservaPublicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = [
            "id",
            "nombre_cliente",
            "telefono",
            "email",
            "fecha",
            "hora",
            "cantidad_personas",
            "mensaje",
        ]


class ReservaDashboardSerializer(serializers.ModelSerializer):
    creada_por_email = serializers.SerializerMethodField()
    gestionada_por_email = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            "id",
            "nombre_cliente",
            "telefono",
            "email",
            "fecha",
            "hora",
            "cantidad_personas",
            "mensaje",
            "estado",
            "mesa_asignada",
            "observacion_admin",
            "fecha_creacion",
            "fecha_actualizacion",
            "creada_por_email",
            "gestionada_por_email",
        ]

    def get_creada_por_email(self, obj):
        return obj.creada_por.user.email if obj.creada_por else None

    def get_gestionada_por_email(self, obj):
        return obj.gestionada_por.user.email if obj.gestionada_por else None

class ProductoCreateSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all()
    )

    class Meta:
        model = Producto
        fields = [
            "id",
            "categoria",
            "nombre",
            "descripcion",
            "condiciones",
            "precio",
            "imagen",
            "disponible",
            "destacado",
            "orden",
            "fecha_creacion"
        ]

    def validate_categoria(self, categoria):
        request = self.context["request"]

        perfil = request.user.perfil_restaurante
        restaurante = perfil.restaurante

        if categoria.restaurante != restaurante:
            raise serializers.ValidationError(
                "La categoría no pertenece a tu restaurante."
            )

        return categoria

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        try:
            perfil = user.perfil_restaurante
            restaurante = perfil.restaurante

            data["user"] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }

            data["restaurante"] = {
                "id": restaurante.id,
                "nombre_empresa": restaurante.nombre_empresa,
                "slug": restaurante.slug,
                "rol": perfil.rol,
            }

        except UsuarioRestaurante.DoesNotExist:
            data["user"] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            data["restaurante"] = None

        return data