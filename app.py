from typing import List
from pydantic import BaseModel
from flask import Flask, request, jsonify
import openai
import os
from youtube_transcript_api import YouTubeTranscriptApi

import nltk
nltk.download('punkt')

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# Configure a chave da API do OpenAI
openai.api_key = os.environ['OPENAI_API_KEY']

# Configurações da API do ChatGPT em português
model = "gpt-3.5-turbo"
engine = "text-davinci-003"
temperature = 0.2
max_tokens = 100

app = Flask(__name__)

def word_count(text):
    # Remover espaços em branco extras e dividir o texto em palavras
    word = text.strip().split()

    # Retornar o número redondo de palavras
    return round(len(word)/600*1000)

def summarize(text):
    # Criar um parser para o texto
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("portuguese"))
    except:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))

    # Criar o resumidor LexRank
    summarizer = LexRankSummarizer()

    # Definir o número de sentenças no resumo
    numero_sentencas = 3

    # Resumir o texto
    resumo = summarizer(parser.document, numero_sentencas)

    # Juntar as sentenças em uma única string
    resumo_texto = ' '.join([str(sentenca) for sentenca in resumo])

    # Retorna o resumo
    return resumo[0]._text

# Função para extrair o ID do vídeo do link do YouTube
def extract_video_id(youtube_link: str) -> str:
    video_id = youtube_link.split("v=")[1]
    return video_id

# Função para obter a transcrição do vídeo do YouTube
def get_video_transcription(video_id: str, language:str) -> str:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        text = ' '.join([t['text'] for t in transcript])
        count_tokens = word_count(text)
        if count_tokens <= 4000:
            return text
        else:
            text = summarize(text)   
            return text
    except:
        return ""

# Função para fazer perguntas usando a API do ChatGPT
def chatgpt_responder(query: str, transcription: str) -> str:
    prompt = f"Responda a seguinte questão: {query} dentro do contexto do texto: {transcription}"
    response = openai.Completion.create(
        engine=engine,
        # model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        n=1,
        stop=None,
    )
    return response.choices[0].text.strip()


# Rota para fazer perguntas sobre o vídeo
@app.route('/query', methods=['POST'])
def fazer_perguntas():
    # Obtém o link do YouTube e a transcrição do corpo da requisição
    youtube_link = request.get_json()
    video_id = extract_video_id(youtube_link['link'])
    language = youtube_link['language']
    querys = youtube_link['query']
    transcription = get_video_transcription(video_id, language)
    
    # Obtém as respostas às perguntas usando a API do ChatGPT
    respostas = []
    
    for query in querys:
        pergunta_com_video = f"{query}"
        resposta = chatgpt_responder(pergunta_com_video, transcription)
        respostas.append(resposta)
    
    return jsonify(respostas)


if __name__ == '__main__':
    app.run()
