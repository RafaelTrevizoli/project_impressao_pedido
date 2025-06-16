from django.db import models

class Impressora(models.Model):
    nome = models.CharField(max_length=100)  # Ex: Epson_L3250
    descricao = models.TextField(blank=True)
    nome_sistema = models.CharField(max_length=100)  # nome real usado no sistema (lpstat -p)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Setor(models.Model):
    nome = models.CharField(max_length=100)
    impressora = models.ForeignKey(Impressora, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome
