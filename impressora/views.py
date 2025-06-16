from .models import Setor
import os, tempfile, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def imprimir_pedido_por_setor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            setor_nome = data.get('setor')
            numero = data.get('numero')
            cliente = data.get('cliente')
            produtos = data.get('produtos', [])

            print(f"[DEBUG] Setor recebido: {setor_nome}")

            setor = Setor.objects.select_related('impressora').filter(nome__iexact=setor_nome).first()

            if not setor:
                print("[ERRO] Setor não encontrado")
                return JsonResponse({'erro': 'Setor não encontrado'}, status=400)
            if not setor.impressora:
                print("[ERRO] Setor não tem impressora associada")
                return JsonResponse({'erro': 'Impressora não configurada para o setor'}, status=400)
            if not setor.impressora.ativa:
                print("[ERRO] Impressora desativada")
                return JsonResponse({'erro': 'Impressora inativa'}, status=400)

            nome_impressora = setor.impressora.nome_sistema.strip()
            print(f"[DEBUG] Nome da impressora (limpo): {repr(nome_impressora)}")

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

            return JsonResponse({'status': f'Pedido enviado para a impressora do setor {setor.nome}'})
        except Exception as e:
            print(f"[ERRO] Exceção: {e}")
            return JsonResponse({'erro': str(e)}, status=500)

    return JsonResponse({'erro': 'Método não permitido'}, status=405)
