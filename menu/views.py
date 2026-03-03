from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Restaurante, Categoria

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