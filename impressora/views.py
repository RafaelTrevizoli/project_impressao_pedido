import qrcode
from PIL import Image

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .models import Setor
import os, tempfile, base64
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO


# Serializer para validar o produto
class ProdutoSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=300)
    sku = serializers.CharField(max_length=50)
    quantidade = serializers.IntegerField(min_value=1)
    unidade = serializers.CharField(max_length=10)
    preco = serializers.FloatField(min_value=0)


# Serializer para validar o pedido
class PedidoSerializer(serializers.Serializer):
    setor = serializers.CharField(max_length=100)
    marketplace = serializers.CharField(max_length=100)
    numero = serializers.IntegerField()
    cliente = serializers.CharField(max_length=100)
    data_faturamento = serializers.DateField()
    produtos = ProdutoSerializer(many=True)
    volumes = serializers.IntegerField(min_value=1)
    soma_quantidades = serializers.IntegerField(min_value=1)
    observacao = serializers.CharField(max_length=255, allow_blank=True)

# Função para gerar fatura
def gerar_fatura_pdf_weasy(dados):
    # Gera QR Code com tamanho fixo (120x120 px)
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(str(dados['numero']))
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Redimensiona para quadrado fixo
    img_qr = img_qr.resize((120, 120), Image.Resampling.LANCZOS)

    buffer_qr = BytesIO()
    img_qr.save(buffer_qr, format="PNG")
    qr_base64 = base64.b64encode(buffer_qr.getvalue()).decode("utf-8")

    # Renderiza o HTML
    html_string = render_to_string('impressora/fatura.html', {
        **dados,
        'qr_code': qr_base64
    })

    # Gera PDF
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=html_string).write_pdf(pdf_file.name)
    return pdf_file.name


class ImprimirPedidoView(APIView):
    def post(self, request):
        serializer = PedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = serializer.validated_data
            setor_nome = data['setor']

            print(f"[DEBUG] Setor recebido: {setor_nome}")

            setor = Setor.objects.select_related('impressora').filter(nome__iexact=setor_nome).first()
            if not setor or not setor.impressora or not setor.impressora.ativa:
                return Response({'erro': 'Setor ou impressora inválidos'}, status=status.HTTP_400_BAD_REQUEST)

            nome_impressora = setor.impressora.nome_sistema.strip()
            print(f"[DEBUG] Nome da impressora: {repr(nome_impressora)}")

            # Gera o PDF com WeasyPrint
            pdf_path = gerar_fatura_pdf_weasy(data)

            # Envia para a impressora
            comando = f"lp -d {nome_impressora} {pdf_path}"
            print(f"[DEBUG] Comando executado: {comando}")
            resultado = os.system(comando)
            print(f"[DEBUG] Resultado do comando: {resultado}")

            return Response({'status': f'Pedido enviado para a impressora do setor {setor.nome}'})

        except Exception as e:
            print(f"[ERRO] Exceção: {e}")
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
