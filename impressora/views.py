# views.py (Django REST Framework)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Setor
import os, tempfile

class ImprimirPedidoView(APIView):
    def post(self, request):
        try:
            setor_nome = request.data.get('setor')
            numero = request.data.get('numero')
            cliente = request.data.get('cliente')
            produtos = request.data.get('produtos', [])

            print(f"[DEBUG] Setor recebido: {setor_nome}")

            setor = Setor.objects.select_related('impressora').filter(nome__iexact=setor_nome).first()
            if not setor or not setor.impressora or not setor.impressora.ativa:
                return Response({'erro': 'Setor ou impressora inválidos'}, status=status.HTTP_400_BAD_REQUEST)

            nome_impressora = setor.impressora.nome_sistema.strip()
            print(f"[DEBUG] Nome da impressora: {repr(nome_impressora)}")

            texto = f"Pedido #{numero}\nSetor: {setor.nome}\nCliente: {cliente}\n\n"
            for p in produtos:
                texto += f"- {p['nome']} x{p['quantidade']} - R${p['preco']:.2f}\n"
            texto += "\n-----------------------------\n"

            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
                temp_file.write(texto)
                temp_file_path = temp_file.name

            comando = f"lpr -P {nome_impressora} {temp_file_path}"
            print(f"[DEBUG] Comando executado: {comando}")
            resultado = os.system(comando)
            print(f"[DEBUG] Resultado do comando: {resultado}")

            return Response({'status': f'Pedido enviado para a impressora do setor {setor.nome}'})

        except Exception as e:
            print(f"[ERRO] Exceção: {e}")
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
