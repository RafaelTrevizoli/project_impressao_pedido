from django.urls import path
from .views import ImprimirPedidoView

urlpatterns = [
    path('api/imprimir/', ImprimirPedidoView.as_view()),
]
