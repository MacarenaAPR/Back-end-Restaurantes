from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UsuarioRestaurante, Categoria, Restaurante,Producto
from django.db.models import Count, Q
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Sesión cerrada correctamente"},
                status=status.HTTP_205_RESET_CONTENT
            )

        except TokenError:
            return Response(
                {"error": "Token inválido o expirado"},
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomLoginView(TokenObtainPairView):
        serializer_class = CustomTokenObtainPairSerializer
class MiRestauranteView(APIView):
        
        permission_classes = [IsAuthenticated]

        def get(self, request):
            try:
                perfil = request.user.perfil_restaurante
            except UsuarioRestaurante.DoesNotExist:
                return Response(
                    {"error": "Usuario sin restaurante"},
                    status=status.HTTP_404_NOT_FOUND
                )

            restaurante = perfil.restaurante
            
            resumen = restaurante.productos.aggregate(
                        disponibles=Count("id", filter=Q(disponible=True)),
                        no_disponibles=Count("id", filter=Q(disponible=False)),
                        total=Count("id")
                    )
            categorias = Categoria.objects.filter(
                restaurante=restaurante,
                activa=True
            ).order_by("orden")

            data_categorias = []

            for categoria in categorias:
                productos = Producto.objects.filter(
                    categoria=categoria,
                    restaurante=restaurante,
                    disponible=True
                ).order_by("orden")

                data_categorias.append({
                    "id": categoria.id,
                    "nombre": categoria.nombre,
                    "productos": [
                        {
                            "id": p.id,
                            "nombre": p.nombre,
                            "descripcion": p.descripcion,
                            "precio": str(p.precio),
                            "imagen": p.imagen.url if p.imagen else None,
                            "disponible": p.disponible,
                        }
                        for p in productos
                    ]
                })
                ultimos_productos = Producto.objects.filter(
                    restaurante=restaurante
                ).order_by("-fecha_creacion")[:10]
                data_ultimos = [
                    {
                        "id": p.id,
                        "nombre": p.nombre,
                        "fecha": p.fecha_creacion,
                        "disponible": p.disponible,
                    }
                    for p in ultimos_productos
                ]

            return Response({
                "usuario": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "rol": perfil.rol,
                },
                "restaurante": {
                    "id": restaurante.id,
                    "nombre_empresa": restaurante.nombre_empresa,
                    "logo": request.build_absolute_uri(restaurante.logo.url) if restaurante.logo else None,
                    "direccion": restaurante.direccion,
                    "telefono": restaurante.telefono,
                    "slug": restaurante.slug
                },
                "resumen": {
                    "productos_disponibles": resumen["disponibles"],
                    "productos_no_disponibles": resumen["no_disponibles"],
                    "total_productos": resumen["total"]
                },
                "categorias": data_categorias,
                "ultimos_productos":data_ultimos
            })
def menu_api(request, slug):

    restaurante = Restaurante.objects.get(slug=slug)

    categorias = Categoria.objects.filter(restaurante=restaurante, activa=True)

    data = []

    for categoria in categorias:
        productos = categoria.producto_set.filter(disponible=True)

        data.append({
            "categoria": categoria.nombre,
            "productos": [
                {
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "precio": str(p.precio),
                    "imagen": p.imagen.url if p.imagen else None
                }
                for p in productos
            ]
        })

    return JsonResponse(data, safe=False)