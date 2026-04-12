from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UsuarioRestaurante

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