import streamlit as st  
from database import (
    criar_tabelas, verificar_usuario, login_existe, adicionar_usuario,
    adicionar_transcricao, listar_transcricoes, excluir_transcricao, atualizar_source_id
)
from auth import hash_password, verify_password
from transcricao import transcrever_audio, criar_pdf
from chat import conversar_com_ia, upload_pdf_ao_chatpdf
from datetime import datetime
import os
import uuid
from st_audiorec import st_audiorec

st.set_page_config(page_title="Histórias Vivas", layout="centered")
criar_tabelas()

os.makedirs("audios", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None
    st.session_state.uuid = None

if "latest_wavfile" not in st.session_state:
    st.session_state.latest_wavfile = None

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.stop()

def login():
    st.title("Login")
    login = st.text_input("Login").lower()
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = verificar_usuario(login, senha, verify_password)
        if user:
            st.session_state.usuario_id = user[0]
            st.session_state.uuid = str(uuid.uuid4())
            st.success("Login bem-sucedido!")
            safe_rerun()
        else:
            st.error("Login ou senha incorretos.")

def cadastro():
    st.title("Cadastro")
    login = st.text_input("Novo login").lower()
    senha = st.text_input("Nova senha", type="password")
    if st.button("Cadastrar"):
        if login_existe(login):
            st.error("Este login já está cadastrado.")
        else:
            senha_hash = hash_password(senha)
            adicionar_usuario(login, senha_hash)
            st.success("Usuário cadastrado com sucesso.")

def menu_principal():
    st.sidebar.title("Menu")
    opcao = st.sidebar.selectbox("Escolha uma opção", [
        "Gravar e Transcrever", "Minhas Transcrições", "Conversar com IA", "Logout"
    ])

    if opcao == "Gravar e Transcrever":
        st.header("🎙️ Gravar novo áudio (via navegador)")
        st.info("Clique em 'Gravar' para começar e depois 'Parar' para finalizar. Máx. 60 segundos.")

        audio_bytes = st_audiorec()

        if audio_bytes is not None:
            nome_audio = f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
            temp_wav_path = os.path.join("audios", nome_audio)
            with open(temp_wav_path, "wb") as f:
                f.write(audio_bytes)
            st.session_state.latest_wavfile = temp_wav_path
            st.success(f"Áudio salvo em: {temp_wav_path}")

        if st.session_state.latest_wavfile:
            st.audio(st.session_state.latest_wavfile)
            texto = transcrever_audio(st.session_state.latest_wavfile)
            st.text_area("Transcrição:", texto, height=300)

            nome_pdf = os.path.join("pdfs", f"transcricao_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
            criar_pdf(texto, nome_pdf)
            
            transcricao_id = adicionar_transcricao(st.session_state.usuario_id, nome_pdf, texto)
            st.success(f"Transcrição salva em PDF: {nome_pdf}")

            source_id = upload_pdf_ao_chatpdf(nome_pdf)
            if source_id:
                atualizar_source_id(transcricao_id, source_id)
            else:
                st.warning("Não foi possível obter o ID do documento na API ChatPDF.")

            with open(nome_pdf, "rb") as f_pdf:
                pdf_bytes = f_pdf.read()
            st.download_button("Download do PDF", pdf_bytes, file_name=os.path.basename(nome_pdf))

            st.session_state.latest_wavfile = None

    elif opcao == "Minhas Transcrições":
        st.header("Lista de Transcrições")
        transcricoes = listar_transcricoes(st.session_state.usuario_id)
        for t in transcricoes:
            col1, col2 = st.columns([8, 1])
            with col1:
                st.write(t[2])
            with col2:
                if st.button(f"Excluir {t[2]}", key=f"excluir_{t[0]}"):
                    excluir_transcricao(t[0])
                    st.success("Transcrição excluída.")
                    safe_rerun()

    elif opcao == "Conversar com IA":
        st.header("Chat com IA")
        pergunta = st.text_input("Faça uma pergunta sobre suas transcrições:")
        if st.button("Enviar"):
            transcricoes = listar_transcricoes(st.session_state.usuario_id)
            if not transcricoes:
                st.warning("Você ainda não possui transcrições salvas.")
            else:
                ultima_transcricao = transcricoes[-1]
                transcricao_id = ultima_transcricao[0]
                caminho_pdf = ultima_transcricao[2]
                source_id = ultima_transcricao[4]

                if not source_id:
                    source_id = upload_pdf_ao_chatpdf(caminho_pdf)
                    if source_id:
                        atualizar_source_id(transcricao_id, source_id)
                    else:
                        st.error("Falha ao obter o ID do documento (sourceId).")
                        return

                resposta = conversar_com_ia(pergunta, source_id)
                st.text_area("Resposta da IA:", resposta, height=200)

def main():
    if st.session_state.usuario_id is None:
        st.sidebar.title("Acesso")
        pagina = st.sidebar.selectbox("Escolha", ["Login", "Cadastro"])
        if pagina == "Login":
            login()
        else:
            cadastro()
    else:
        menu_principal()

if __name__ == "__main__":
    main()