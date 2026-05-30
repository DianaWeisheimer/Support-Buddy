# Usa uma imagem oficial do Python enxuta (slim = menor tamanho)
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala dependências primeiro (aproveita o cache do Docker)
# Se só o código mudar, essa camada não é reexecutada
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta que a API vai usar
EXPOSE 8000

# Comando para iniciar o servidor
# --host 0.0.0.0 faz a API aceitar conexões de fora do container
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]