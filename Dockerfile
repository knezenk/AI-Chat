# Use uma imagem Python leve
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o Flask usa
EXPOSE 5010

# Comando para rodar a aplicação
CMD ["python", "app.py"]
