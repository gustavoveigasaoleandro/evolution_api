from flask import Flask, request, jsonify
import requests
import subprocess
import os
from pyngrok import ngrok
from langchain_ollama import OllamaLLM
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente a partir do arquivo .env
load_dotenv()

app = Flask(__name__)

# CONFIGURAÇÕES
EVOLUTION_TOKEN = os.getenv("EVOLUTION_TOKEN")
GRUPO_ID_DESEJADO = os.getenv("GRUPO_ID_DESEJADO")
INSTANCE = os.getenv("INSTANCE")
URL_ENVIO = os.getenv("URL_ENVIO")
PROMPT = os.getenv("PROMPT")

def enviar_resposta(mensagem, numero_destinatario, mensagem_respondida=None, mencionar_todos=False, participantes_mencionados=None):
    # Estrutura do payload para envio de mensagem
    print('teste: ', mensagem)
    payload = {
        "number": numero_destinatario,  # Agora, o número do destinatário será o 'chat_id'
        "options": {
            "delay": 123,  # Tempo de atraso, se necessário (opcional)
            "presence": "composing",  # Indica que está digitando (opcional)
            "linkPreview": True,  # Se deve mostrar o preview do link (opcional)
            "quoted": mensagem_respondida,  # Mensagem que está sendo citada (se necessário)
            "mentions": {
                "everyOne": mencionar_todos,  # Caso queira mencionar todos no grupo
                "mentioned": participantes_mencionados if participantes_mencionados else []  # Participantes específicos a serem mencionados
            }
        },
        "text": mensagem  # A mensagem que você deseja enviar
    }

    # Cabeçalhos da requisição
    headers = {
        "apikey": EVOLUTION_TOKEN,  # Token de autenticação
        "Content-Type": "application/json"  # Tipo de conteúdo
    }

    # URL do serviço para envio da mensagem
    url = f"http://localhost:8081/message/sendText/Gustavo VSL"  # URL com a instância dinâmica

    # Enviar a requisição POST
    response = requests.post(url, json=payload, headers=headers)

    # Verificar a resposta e imprimir o resultado
    if response.status_code == 200:
        print("Resposta enviada com sucesso:", response.text)
    else:
        print("Erro ao enviar resposta:", response.text)


def buscar_historico_conversa(chat_id, quantidade=5):
    url = f"http://localhost:8081/chat/findMessages/Gustavo%20VSL"
    headers = {
        "apikey": EVOLUTION_TOKEN,
        "Content-Type": "application/json"
    }   
    payload = {
        "where": {
            "key": {
                "remoteJid": chat_id
            }
        },
        "limit": quantidade,
        "orderBy": {
            "messageTimestamp": "desc"
        }
    }

    try:
        print(f"Buscando histórico de {chat_id} com URL: {url}")
        print(f"Headers usados: {headers}")
        print(f"Payload enviado: {payload}")
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            mensagens = response.json().get("messages", {}).get("records", [])
            print(f"mensagens: {mensagens}")
            return mensagens[::-1]  # inverte para ordem cronológica
        else:
            print("Erro ao buscar histórico:", response.text)
            return []
    except Exception as e:
        print("Erro ao buscar histórico:", str(e))
        return [] 


def gerar_resposta_com_modelo(texto, historico=None):
    try:
        llm = OllamaLLM(model="mistral:latest", device="gpu")

        contexto = ""
        if historico:
            partes = []
            for m in historico:
                autor = m.get("senderName", "Você") if m.get("key", {}).get("fromMe") else m.get("senderName", "Contato")
                msg_type = m.get("messageType", "")
                msg_data = m.get("message", {})
                conteudo = ""
                
                # Converter o timestamp
                timestamp = m.get("messageTimestamp", 0)
                dt_str = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")

                if msg_type == "conversation":
                    conteudo = msg_data.get("conversation", "")
                elif msg_type == "extendedTextMessage":
                    conteudo = msg_data.get("extendedTextMessage", {}).get("text", "")
                elif msg_type == "imageMessage":
                    conteudo = f"[Imagem: {msg_data.get('imageMessage', {}).get('caption', '')}]"
                elif msg_type == "audioMessage":
                    conteudo = "[Mensagem de áudio]"
                elif msg_type == "videoMessage":
                    conteudo = "[Vídeo enviado]"
                else:
                    conteudo = "[Tipo de mensagem não tratado]"

                partes.append(f"{dt_str} - {autor}: {conteudo}")
            contexto = "\n".join(partes)
        print(f'Contexto: {contexto}')
        prompt = f"{PROMPT} HISTÓRICO: {contexto} MENSAGEM RECEBIDA: {texto} SUA RESPOSTA:"  
        result = llm.invoke(prompt)
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] O comando retornou código de erro {e.returncode}")
        print(f"[STDERR] {e.stderr}")
        return "Erro ao gerar resposta com o modelo."
    except FileNotFoundError:
        print("[ERRO] Caminho para o executável ./llama/main não encontrado.")
        return "Modelo indisponível."
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao chamar o modelo: {str(e)}")
        return "Erro inesperado na geração da resposta."
    
@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    data = request.json
    print("Recebido:", data)

    # Obter o ID do grupo e a mensagem
    chat_id = data["data"]["key"]["remoteJid"]  # Usando 'remoteJid' para obter o ID do grupo
    texto = data["data"]["message"]["conversation"]
    
    # Verificar se a mensagem não foi enviada por você (Gustavo)
    if data["data"]["key"]["fromMe"]:
        print("Mensagem enviada por mim, ignorando...")
        return jsonify({"status": "ok"}), 200
    
    # Verifica se o chat_id corresponde ao ID do grupo desejado
    if chat_id == GRUPO_ID_DESEJADO or chat_id == '5515991289083@s.whatsapp.net':
        print('TEXTO: ', texto)
        historico = buscar_historico_conversa(chat_id, quantidade=5)
        resposta = gerar_resposta_com_modelo(texto, historico)
        print(f"Resposta: {resposta}")
        
        # Aqui você passa 'chat_id' diretamente para o envio da resposta
        enviar_resposta(mensagem=resposta, numero_destinatario=chat_id)  # Usando 'chat_id' como número

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)