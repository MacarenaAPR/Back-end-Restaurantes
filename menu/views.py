from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .serializers import CustomTokenObtainPairSerializer, ProductoCreateSerializer, ReservaPublicaSerializer, ReservaDashboardSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import UsuarioRestaurante, Categoria, Restaurante,Producto, BitacoraProducto, Reserva
from django.db.models import Count, Q, F
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.generics import CreateAPIView, UpdateAPIView
from django.db import transaction
from django.utils.timezone import now




class CrearReservaPublicaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, slug):
        restaurante = get_object_or_404(Restaurante, slug=slug, activo=True)

        serializer = ReservaPublicaSerializer(data=request.data)

        if serializer.is_valid():
            reserva = serializer.save(
                restaurante=restaurante,
                estado="pendiente"
            )

            return Response(
                {
                    "message": "Solicitud de reserva enviada correctamente.",
                    "reserva": ReservaDashboardSerializer(reserva).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReservasDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario_restaurante = get_object_or_404(
            UsuarioRestaurante,
            user=request.user,
            activo=True
        )

        reservas = Reserva.objects.filter(
            restaurante=usuario_restaurante.restaurante
        )

        serializer = ReservaDashboardSerializer(reservas, many=True)

        return Response(serializer.data)

class CrearReservaManualView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario_restaurante = get_object_or_404(
            UsuarioRestaurante,
            user=request.user,
            activo=True
        )

        serializer = ReservaPublicaSerializer(data=request.data)

        if serializer.is_valid():
            reserva = serializer.save(
                restaurante=usuario_restaurante.restaurante,
                creada_por=usuario_restaurante,
                estado="confirmada"
            )

            return Response(
                {
                    "message": "Reserva creada manualmente.",
                    "reserva": ReservaDashboardSerializer(reserva).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActualizarReservaView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, reserva_id):
        usuario_restaurante = get_object_or_404(
            UsuarioRestaurante,
            user=request.user,
            activo=True
        )

        reserva = get_object_or_404(
            Reserva,
            id=reserva_id,
            restaurante=usuario_restaurante.restaurante
        )

        estado = request.data.get("estado")
        mesa_asignada = request.data.get("mesa_asignada")
        observacion_admin = request.data.get("observacion_admin")

        if estado:
            reserva.estado = estado
            reserva.gestionada_por = usuario_restaurante

        if mesa_asignada is not None:
            reserva.mesa_asignada = mesa_asignada

        if observacion_admin is not None:
            reserva.observacion_admin = observacion_admin

        reserva.save()

        return Response({
            "message": "Reserva actualizada correctamente.",
            "reserva": ReservaDashboardSerializer(reserva).data
        })



class HistorialBitacoraView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        perfil = request.user.perfil_restaurante
        restaurante = perfil.restaurante

        historial = BitacoraProducto.objects.filter(
            restaurante=restaurante
        ).order_by("-fecha")

        data = [
            {
                "id": b.id,
                "accion": b.accion,
                "producto": b.producto_nombre,
                "descripcion": b.descripcion,
                "fecha": b.fecha,
                "usuario": b.usuario.username if b.usuario else "Sistema"
            }
            for b in historial
        ]

        return Response(data)

class ProductoUpdateView(UpdateAPIView):
    serializer_class = ProductoCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        perfil = self.request.user.perfil_restaurante
        return Producto.objects.filter(restaurante=perfil.restaurante)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        producto = self.get_object()

        nombre_anterior = producto.nombre
        precio_anterior = producto.precio
        descripcion_anterior = producto.descripcion
        condiciones_anterior = producto.condiciones
        disponible_anterior = producto.disponible
        destacado_anterior = producto.destacado
        orden_anterior = producto.orden
        categoria_anterior = producto.categoria.nombre
        imagen_anterior = producto.imagen.url if producto.imagen else None

        nuevo_orden = int(request.data.get("orden", producto.orden))
        nueva_categoria_id = int(request.data.get("categoria", producto.categoria_id))

        # actualizar datos normales
        producto.nombre = request.data.get("nombre", producto.nombre)
        producto.precio = request.data.get("precio", producto.precio)
        producto.descripcion = request.data.get("descripcion", producto.descripcion)
        producto.condiciones = request.data.get("condiciones", producto.condiciones)
        producto.disponible = request.data.get("disponible") == "true"
        producto.destacado = request.data.get("destacado") == "true"

        if "imagen" in request.FILES:
            producto.imagen = request.FILES["imagen"]

        # productos de la categoría
        productos = list(
            Producto.objects.filter(
                restaurante=producto.restaurante,
                categoria_id=nueva_categoria_id
            )
            .exclude(id=producto.id)
            .order_by("orden", "id")
        )

        # limitar orden
        if nuevo_orden < 1:
            nuevo_orden = 1
        if nuevo_orden > len(productos) + 1:
            nuevo_orden = len(productos) + 1

        # insertar en nueva posición
        producto.categoria_id = nueva_categoria_id
        productos.insert(nuevo_orden - 1, producto)

        # 🔥 fase 1: evitar choque (orden temporal)
        for p in productos:
            if p.id:
                p.orden = -100000 - p.id
                p.save(update_fields=["orden"])

        # 🔥 fase 2: orden real
        for i, p in enumerate(productos, start=1):
            p.orden = i
            p.save()
        
        cambios = []

        if nombre_anterior != producto.nombre:
            cambios.append(f"Nombre: {nombre_anterior} → {producto.nombre}")

        if str(precio_anterior) != str(producto.precio):
            cambios.append(f"Precio: {precio_anterior} → {producto.precio}")

        if descripcion_anterior != producto.descripcion:
            cambios.append("Descripción actualizada")

        if condiciones_anterior != producto.condiciones:
            cambios.append("Condiciones actualizadas")

        if disponible_anterior != producto.disponible:
            estado_anterior = "Disponible" if disponible_anterior else "No disponible"
            estado_nuevo = "Disponible" if producto.disponible else "No disponible"
            cambios.append(f"Disponibilidad: {estado_anterior} → {estado_nuevo}")

        if destacado_anterior != producto.destacado:
            destacado_ant = "Destacado" if destacado_anterior else "No destacado"
            destacado_nuevo = "Destacado" if producto.destacado else "No destacado"
            cambios.append(f"Destacado: {destacado_ant} → {destacado_nuevo}")

        if orden_anterior != producto.orden:
            cambios.append(f"Orden: {orden_anterior} → {producto.orden}")

        if categoria_anterior != producto.categoria.nombre:
            cambios.append(f"Categoría: {categoria_anterior} → {producto.categoria.nombre}")

        imagen_nueva = producto.imagen.url if producto.imagen else None
        if imagen_anterior != imagen_nueva:
            cambios.append("Imagen actualizada")

        if cambios:
            BitacoraProducto.objects.create(
                restaurante=producto.restaurante,
                producto_id=producto.id,
                producto_nombre=producto.nombre,
                usuario=request.user,
                accion="EDITADO",
                descripcion="; ".join(cambios),
                valor_anterior="Edición de producto",
                valor_nuevo="; ".join(cambios)
            )
        serializer = self.get_serializer(producto)
        return Response(serializer.data)

class ProductoCreateView(CreateAPIView):
    serializer_class = ProductoCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        perfil = self.request.user.perfil_restaurante
        restaurante = perfil.restaurante

        producto = serializer.save(restaurante=restaurante)

        BitacoraProducto.objects.create(
            restaurante=restaurante,
            producto_id=producto.id,
            producto_nombre=producto.nombre,
            usuario=self.request.user,
            accion="CREADO",
            descripcion=f"Se creó el producto {producto.nombre}",
            valor_nuevo=f"Precio: {producto.precio}, Orden: {producto.orden}"
        )

        
class EliminarProductoView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            producto = Producto.objects.get(id=id)
        except Producto.DoesNotExist:
            return Response(
                {"error": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Aquí después debes dejar la validación real según tu relación usuario-restaurante
        # Por ahora elimina directo
        BitacoraProducto.objects.create(
            restaurante=producto.restaurante,
            producto_id=producto.id,
            producto_nombre=producto.nombre,
            usuario=request.user,
            accion="ELIMINADO",
            descripcion=f"Se eliminó el producto {producto.nombre}",
            valor_anterior=f"Precio: {producto.precio}, Categoría: {producto.categoria.nombre}",
            valor_nuevo="Producto eliminado"
        )
        producto.delete()

        return Response(
            {"message": "Producto eliminado correctamente"},
            status=status.HTTP_200_OK
        )
class ActualizarDisponibilidadProductoView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            producto = Producto.objects.get(id=id)
        except Producto.DoesNotExist:
            return Response(
                {"error": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        disponible = request.data.get("disponible")

        if disponible is None:
            return Response(
                {"error": "El campo 'disponible' es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )

        producto.disponible = disponible
        producto.save()

        return Response(
            {
                "message": "Disponibilidad actualizada correctamente",
                "id": producto.id,
                "disponible": producto.disponible,
            },
            status=status.HTTP_200_OK
        )

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
                todos_productos = Producto.objects.filter(
                    restaurante=restaurante
                )
                data_productos=[
                    {
                        "id": p.id,
                        "nombre": p.nombre,
                        "descripcion": p.descripcion,
                        "precio": str(p.precio),
                        "imagen": p.imagen.url if p.imagen else None,
                        "disponible": p.disponible,
                        "categoria":p.categoria.nombre,
                        "fecha_creacion":p.fecha_creacion,
                        "destacado":p.destacado,
                        "orden":p.orden
                    }
                    for p in todos_productos
                ]
                ultimas_actualizaciones = BitacoraProducto.objects.filter(
                    restaurante=restaurante
                ).order_by("-fecha")[:10]
                hoy = now().date()

                reservas_hoy = Reserva.objects.filter(
                    restaurante=restaurante,
                    fecha=hoy
                ).count()

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
                    "total_productos": resumen["total"],
                    "reservas_hoy": reservas_hoy,

                },
                "categorias": data_categorias,
                "productos":data_productos,
                "ultimas_actualizaciones": [
                    {
                        "id": b.id,
                        "accion": b.accion,
                        "producto": b.producto_nombre,
                        "descripcion": b.descripcion,
                        "fecha": b.fecha,
                    }
                    for b in ultimas_actualizaciones
                ]
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