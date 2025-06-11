import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("CHATPDF_API_KEY")
UPLOAD_URL = "https://api.chatpdf.com/v1/sources/add-file"
CHAT_URL = "https://api.chatpdf.com/v1/chats/message"

def listar_transcricoes(diretorio="pdfs"):
    """Lista todos os PDFs disponíveis no diretório de transcrições."""
    if not os.path.exists(diretorio):
        return []
    return [f for f in os.listdir(diretorio) if f.endswith(".pdf")]

def upload_pdf_ao_chatpdf(caminho_pdf):
    """
    Faz upload do PDF para a API do ChatPDF e retorna o sourceId.
    Retorna None se ocorrer erro.
    """
    if API_KEY is None:
        print("Chave da API não configurada.")
        return None
    try:
        headers = {"x-api-key": API_KEY}
        with open(caminho_pdf, "rb") as f:
            files = {"file": (os.path.basename(caminho_pdf), f, "application/pdf")}
            response = requests.post(UPLOAD_URL, headers=headers, files=files)

        print("Código de status do upload:", response.status_code)
        print("Resposta da API:", response.text)

        if response.status_code == 200:
            return response.json().get("sourceId")
        else:
            print("Erro ao enviar PDF:", response.status_code, "-", response.text)
            return None
    except Exception as e:
        print("Exceção no upload do PDF:", str(e))
        return None

def conversar_com_ia(pergunta, source_id):
    """
    Envia pergunta para o ChatPDF usando o source_id.
    Retorna a resposta da IA ou mensagem de erro.
    """
    if not source_id:
        return "Erro: source_id inválido."

    try:
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "sourceId": source_id,
            "messages": [{"role": "user", "content": pergunta}]
        }

        response = requests.post(CHAT_URL, headers=headers, json=body)

        if response.status_code == 200:
            return response.json().get("content", "Sem resposta da IA.")
        else:
            return f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return f"Exceção: {str(e)}"

if __name__ == "__main__":
    caminho_pdf = "transcricao_exemplo.pdf"
    source_id = upload_pdf_ao_chatpdf(caminho_pdf)
    if source_id:
        print("Upload realizado com sucesso. Source ID:", source_id)
        pergunta = "Qual o tema do documento?"
        resposta = conversar_com_ia(pergunta, source_id)
        print("Resposta da IA:", resposta)
    else:
        print("Falha no upload, não foi possível conversar com IA.")