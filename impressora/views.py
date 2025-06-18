# views.py (Django REST Framework com WeasyPrint e QR Code)

import os, tempfile, base64
from io import BytesIO
from datetime import datetime
from PIL import Image
import qrcode

from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from weasyprint import HTML
from .models import Setor

# -------------------------
# Serializers
# -------------------------

class ProdutoSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=300)
    sku = serializers.CharField(max_length=50)
    quantidade = serializers.IntegerField(min_value=1)
    unidade = serializers.CharField(max_length=10)
    preco = serializers.FloatField(min_value=0)

class PedidoSerializer(serializers.Serializer):
    setor = serializers.CharField(max_length=100)
    marketplace = serializers.CharField(max_length=100)
    numero = serializers.CharField(max_length=30)
    cliente = serializers.CharField(max_length=100)
    data_faturamento = serializers.DateField()
    produtos = ProdutoSerializer(many=True)
    volumes = serializers.IntegerField(min_value=1)
    soma_quantidades = serializers.IntegerField(min_value=1)
    observacao = serializers.CharField(max_length=255, allow_blank=True)

# -------------------------
# Geração de PDF com QR Code
# -------------------------

def gerar_fatura_pdf_weasy(dados):
    # Gera QR Code com número do pedido
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(str(dados['numero']))
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img_qr = img_qr.resize((120, 120), Image.Resampling.LANCZOS)

    buffer_qr = BytesIO()
    img_qr.save(buffer_qr, format="PNG")
    qr_base64 = base64.b64encode(buffer_qr.getvalue()).decode("utf-8")

    # Define caminho da imagem do marketplace
    nome_mkt = dados['marketplace'].lower().replace(' ', '_')
    caminho_logo = os.path.join("impressora", "static", "impressora", "marketplaces", f"{nome_mkt}.png")

    if os.path.exists(caminho_logo):
        with open(caminho_logo, "rb") as logo_file:
            logo_base64 = base64.b64encode(logo_file.read()).decode("utf-8")
        logo_src = f"data:image/png;base64,{logo_base64}"
    else:
        logo_src = ""  # opcional: imagem padrão se quiser

    # Renderiza HTML com dados + QR code + logo
    html_string = render_to_string('impressora/fatura.html', {
        **dados,
        'qr_code': qr_base64,
        'marketplace_logo': logo_src
    })

    # Gera o PDF
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=html_string).write_pdf(pdf_file.name)
    return pdf_file.name

# -------------------------
# View principal da API
# -------------------------

class ImprimirPedidoView(APIView):
    def post(self, request):
        # Validação dos dados
        serializer = PedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = serializer.validated_data
            setor_nome = data['setor']
            print(f"[DEBUG] Setor recebido: {setor_nome}")

            # Busca o setor e impressora correspondente
            setor = Setor.objects.select_related('impressora').filter(nome__iexact=setor_nome).first()
            if not setor or not setor.impressora or not setor.impressora.ativa:
                return Response({'erro': 'Setor ou impressora inválidos'}, status=status.HTTP_400_BAD_REQUEST)

            nome_impressora = setor.impressora.nome_sistema.strip()
            print(f"[DEBUG] Nome da impressora: {repr(nome_impressora)}")

            # Geração do PDF
            pdf_path = gerar_fatura_pdf_weasy(data)

            # Envia o PDF para impressão
            comando = f"lp -d {nome_impressora} {pdf_path}"
            print(f"[DEBUG] Comando executado: {comando}")
            resultado = os.system(comando)
            print(f"[DEBUG] Resultado do comando: {resultado}")

            return Response({'status': f'Pedido enviado para a impressora do setor {setor.nome}'})

        except Exception as e:
            print(f"[ERRO] Exceção: {e}")
            return Response({'erro': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)