import speech_recognition as sr
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

def transcrever_audio(caminho_arquivo):
    """
    Recebe o caminho de um arquivo de áudio, transcreve o conteúdo para texto em português.
    Retorna o texto transcrito ou mensagem de erro.
    """
    r = sr.Recognizer()
    try:
        with sr.AudioFile(caminho_arquivo) as source:
            audio = r.record(source)
        texto = r.recognize_google(audio, language='pt-BR')
        return texto
    except Exception as e:
        return f"Erro: {str(e)}"

def criar_pdf(texto, caminho_pdf):
    """
    Cria um arquivo PDF no caminho especificado a partir do texto recebido.
    Tenta usar Arial, se não disponível, usa Helvetica.
    """
    c = canvas.Canvas(caminho_pdf, pagesize=letter)
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        fonte = "Arial"
    except:
        fonte = "Helvetica"
    c.setFont(fonte, 12)
    width, height = letter
    margin = 72
    y = height - margin

    linhas = texto.split('\n')
    for linha in linhas:
        if y < margin:
            c.showPage()
            c.setFont(fonte, 12)
            y = height - margin
        c.drawString(margin, y, linha)
        y -= 14
    c.save()

def salvar_transcricao_txt(texto, caminho_txt):
    """
    Salva o texto transcrito em um arquivo .txt para facilitar consultas futuras.
    """
    with open(caminho_txt, 'w', encoding='utf-8') as f:
        f.write(texto)

if __name__ == "__main__":
    audio_path = "exemplo_audio.wav"
    pdf_path = "transcricao_exemplo.pdf"
    txt_path = "transcricao_exemplo.txt"

    texto = transcrever_audio(audio_path)
    if texto.startswith("Erro:"):
        print(texto)
    else:
        print("Transcrição concluída:")
        print(texto)

        criar_pdf(texto, pdf_path)
        print(f"PDF criado em: {pdf_path}")

        salvar_transcricao_txt(texto, txt_path)
        print(f"Transcrição salva em arquivo txt: {txt_path}")