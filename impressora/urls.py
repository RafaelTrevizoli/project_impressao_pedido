from django.urls import path
from .views import imprimir_pedido_por_setor

urlpatterns = [
    path('imprimir/', imprimir_pedido_por_setor),
]
