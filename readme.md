# Listar impressoras locais 

lpstat -p -d

# Dar post pra teste 

curl -X POST http://127.0.0.1:8001/impressora/api/imprimir/ \
  -H "Content-Type: application/json" \
  -d '{
    "setor": "Pvc",
    "numero": 101,
    "cliente": "Maria Clara Cavichia",
    "produtos": [
      { "nome": "Pastel de carne", "quantidade": 2, "preco": 6.50 },
      { "nome": "Coca-Cola lata", "quantidade": 1, "preco": 5.00 }
    ]
  }'

curl -X POST http://127.0.0.1:8001/impressora/api/imprimir/ \
  -H "Content-Type: application/json" \
  -d '{
    "setor": "Isopor",
    "numero": 101,
    "cliente": "Maria Clara Cavichia",
    "produtos": [
      { "nome": "Pastel de carne", "quantidade": 2, "preco": 6.50 },
      { "nome": "Coca-Cola lata", "quantidade": 1, "preco": 5.00 }
    ]
  }'

curl -X POST http://127.0.0.1:8001/impressora/api/imprimir/ \
  -H "Content-Type: application/json" \
  -d '{
    "setor": "Escritorio",
    "numero": 101,
    "cliente": "Maria Clara Cavichia",
    "produtos": [
      { "nome": "Pastel de carne", "quantidade": 2, "preco": 6.50 },
      { "nome": "Coca-Cola lata", "quantidade": 1, "preco": 5.00 }
    ]
  }'
