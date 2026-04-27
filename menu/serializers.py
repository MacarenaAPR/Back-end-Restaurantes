from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UsuarioRestaurante, HorarioAtencion, MetodoPago, Mesa
from rest_framework import serializers
from .models import Producto, Categoria, Reserva, Restaurante
from django.contrib.auth.models import User

class UsuarioRestauranteCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    nombre = serializers.CharField(max_length=150, required=False, allow_blank=True)
    rol = serializers.ChoiceField(choices=["admin", "empleado"])

    def validate(self, data):
        request = self.context["request"]
        restaurante = request.user.perfil_restaurante.restaurante
        rol = data["rol"]

        usuarios_activos = UsuarioRestaurante.objects.filter(
            restaurante=restaurante,
            activo=True
        )

        if usuarios_activos.count() >= 4:
            raise serializers.ValidationError(
                "Este restaurante ya alcanzó el máximo de usuarios permitidos."
            )

        if rol == "admin" and usuarios_activos.filter(rol="admin").count() >= 1:
            raise serializers.ValidationError(
                "Este restaurante ya tiene un administrador."
            )

        if rol == "empleado" and usuarios_activos.filter(rol="empleado").count() >= 2:
            raise serializers.ValidationError(
                "Este restaurante ya tiene el máximo de empleados permitidos."
            )

        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError(
                "Este nombre de usuario ya existe."
            )

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                "Este correo ya está registrado."
            )

        return data

    def create(self, validated_data):
        request = self.context["request"]
        dueno_perfil = request.user.perfil_restaurante
        restaurante = dueno_perfil.restaurante

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("nombre", "")
        )

        usuario_restaurante = UsuarioRestaurante.objects.create(
            user=user,
            restaurante=restaurante,
            rol=validated_data["rol"],
            activo=True,
            creado_por=dueno_perfil
        )

        return usuario_restaurante

class UsuarioRestauranteListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    nombre = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = UsuarioRestaurante
        fields = [
            "id",
            "email",
            "username",
            "nombre",
            "rol",
            "activo",
            "fecha_creacion",
        ]

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = "__all__"

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = "__all__"

class HorarioSerializer(serializers.ModelSerializer):
    dia_nombre = serializers.CharField(source="get_dia_display", read_only=True)

    class Meta:
        model = HorarioAtencion
        fields = "__all__"

class RestauranteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurante
        fields = [
            "id",
            "nombre_empresa",
            "telefono",
            "email_contacto",
            "direccion",
            "ciudad",
            "sitio_web",
            "descripcion",
            "logo",
        ]

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