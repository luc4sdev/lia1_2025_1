import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def gerar_alerta(analise: dict) -> str:
    try:
        total = int(analise.get("total", 0))
        duracao = float(analise.get("duracao_s", 1.0))  # evitar divisão por zero
        veic_por_s = round(float(analise.get("veiculos_por_segundo", 0.0)), 2)
        vel_media = round(float(analise.get("media_velocidade_px", 0.0)), 2)
    except Exception as e:
        return f"Erro ao processar os dados de análise: {str(e)}"

    # Configurar chave da API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Erro: API key do Google Gemini não encontrada no .env"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-2.0-flash")

    prompt = f"""
    Você é um assistente de tráfego especializado. Analise a situação abaixo com base em um vídeo processado automaticamente:

    - Veículos detectados: {total}
    - Duração do vídeo: {duracao:.1f} segundos
    - Média de veículos por segundo: {veic_por_s}
    - Velocidade média dos veículos (em pixels por frame): {vel_media}

    Com base nesses dados, classifique o nível de tráfego usando esta escala:
    - 0-10 veículos: "Trânsito livre"
    - 11-30 veículos: "Trânsito moderado"
    - 31-50 veículos: "Trânsito intenso"
    - +50 veículos: "Congestionamento"

    Se a velocidade média for muito baixa (menor que 2), considere um possível engarrafamento mesmo com quantidade menor.

    Escreva uma frase curta, clara e objetiva indicando a situação atual e adicione uma dica de segurança relevante.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Erro ao gerar alerta com IA: {str(e)}"
