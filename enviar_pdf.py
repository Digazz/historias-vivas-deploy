import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CHATPDF_API_KEY")

def enviar_pdf_e_obter_source_id(caminho_pdf):
    url = "https://api.chatpdf.com/v1/sources/add-file"
    headers = {
        "x-api-key": API_KEY
    }

    with open(caminho_pdf, "rb") as f:
        files = {
            "file": (os.path.basename(caminho_pdf), f, "application/pdf")
        }
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        dados = response.json()
        print("✅ sourceId:", dados["sourceId"])
        return dados["sourceId"]
    else:
        print("❌ Erro ao enviar PDF:", response.status_code, response.text)
        return None

if __name__ == "__main__":
    caminho = input("Digite o caminho do PDF (ex: pdfs/transcricao_20250527.pdf): ")
    enviar_pdf_e_obter_source_id(caminho)