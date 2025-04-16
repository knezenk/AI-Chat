from groq import Groq
import os

# API key da Groq e modelo a ser usado
chave_groq = "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"
model = "llama3-70b-8192"

# Variável global que armazenará o conhecimento resumido
conhecimento_contabil = ""

# 📖 Função: Divide um arquivo em blocos de texto
def dividir_arquivo_em_blocos(caminho, tamanho_maximo=3000):
    with open(caminho, "r", encoding="utf-8") as f:
        texto = f.read()
    return [texto[i:i + tamanho_maximo] for i in range(0, len(texto), tamanho_maximo)]

# 📚 Função: Resume um bloco de texto usando o modelo da Groq
def resumir_bloco(bloco, client):
    #                {"role": "system", "content": "Resuma esse conteúdo contábil para uso posterior:"},
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Resuma essas notícias para um bate-papo com o cliente:"},
                {"role": "user", "content": bloco}
            ],
            temperature=0.2,
            max_tokens = 500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro no resumo: {e}"

# 🧠 Treinamento do agente baseado no conteúdo do arquivo
def realizar_treinamento():
    global conhecimento_contabil
    print("📚 Iniciando treinamento com base no conteúdo...")
    client = Groq(api_key=chave_groq)

    try:
        blocos = dividir_arquivo_em_blocos("treinamento2.txt", tamanho_maximo=3000)
        resumos = []

        for bloco in blocos[:5]:  # Limita o número de blocos para evitar sobrecarga
            resumo = resumir_bloco(bloco, client)
            resumos.append(resumo)

        conhecimento_contabil = "\n".join(resumos)
        print("✅ Treinamento concluído!")
    except Exception as e:
        print(f"❌ Erro durante o treinamento: {e}")

# 🤖 Função do agente: responde com base no conteúdo treinado
def agent(msg):
    if not conhecimento_contabil:
        return "⚠️ Conhecimento ainda não foi treinado."

    client = Groq(api_key=chave_groq)

#            "content": f"Você é um assistente contábil didático e claro. Use o seguinte conteúdo como base:\n{conhecimento_contabil}"
    
    messages = [
        {
            "role": "system",
            "content": f"Você é um assistente jornalístico didático e claro. Se apresente sempre como um jornalista virtual. Apto pra tirar dúvidas sobre as notícias capturadas. Use o seguinte conteúdo como :\n{conhecimento_contabil}"
        },
        {
            "role": "user",
            "content": msg
        }
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Erro ao consultar a Groq API: {e}"
