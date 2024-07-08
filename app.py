from flask import Flask, request, render_template, flash, redirect, url_for
import os
from PIL import Image, UnidentifiedImageError
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar flash messages

# Configuração do GemAI
genai.configure(api_key="AIzaSyAUjnJX5IetZFKMss7J6PuXfQQapKZuKB0")

# Função para análise de imagem
def analyze_image(image_path):
    try:
        img = Image.open(image_path)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(["Analise esta imagem e descreva as roupas e suas cores.", img])
        
        if not response or not hasattr(response, 'text'):
            return "Erro ao analisar a imagem: Nenhuma resposta válida recebida."
        
        return response.text
    except UnidentifiedImageError:
        return "Erro ao analisar a imagem: Arquivo de imagem não identificado."
    except Exception as e:
        return f"Erro ao analisar a imagem: {str(e)}"

# Função para adicionar links de compras e sugestões de roupas com base na ocasião
def add_shopping_suggestions(description, occasion):
    suggestions = {
        "casual": {
            "description": "Para um visual casual, você pode considerar adicionar estas peças ao seu guarda-roupa:",
            "items": [
                {"name": "camisa casual", "link": "https://www.cea.com.br/camisas-casual", "reason": "Uma camisa casual é confortável e versátil para diversas situações do dia a dia."},
                {"name": "jeans", "link": "https://www.lojasrenner.com.br/calcas-casual", "reason": "Jeans são peças chave em qualquer guarda-roupa casual devido à sua durabilidade e estilo."},
                {"name": "tênis", "link": "https://www.nike.com.br/tenis-casual", "reason": "Tênis confortáveis são ideais para um visual casual e para longas caminhadas."}
            ]
        },
        "formal": {
            "description": "Para um visual formal, considere as seguintes peças:",
            "items": [
                {"name": "camisa formal", "link": "https://www.cea.com.br/camisas-formal", "reason": "Uma camisa formal é essencial para eventos profissionais e sociais."},
                {"name": "calça social", "link": "https://www.lojasrenner.com.br/calcas-formal", "reason": "Calças sociais proporcionam um visual elegante e sofisticado."},
                {"name": "sapato social", "link": "https://www.nike.com.br/sapatos-formal", "reason": "Sapatos sociais completam o traje formal com classe e conforto."}
            ]
        },
        "esporte": {
            "description": "Para um visual esportivo, estas peças são recomendadas:",
            "items": [
                {"name": "camisa esportiva", "link": "https://www.cea.com.br/camisas-esporte", "reason": "Camisas esportivas são feitas de materiais que ajudam a manter o corpo seco durante atividades físicas."},
                {"name": "calça esportiva", "link": "https://www.lojasrenner.com.br/calcas-esporte", "reason": "Calças esportivas oferecem conforto e flexibilidade para exercícios."},
                {"name": "tênis esportivo", "link": "https://www.nike.com.br/tenis-esporte", "reason": "Tênis esportivos proporcionam o suporte necessário para diferentes tipos de atividades físicas."}
            ]
        }
    }

    filtered_items = [item for item in suggestions[occasion]["items"] if item["name"].split()[0] not in description]

    suggestion_text = suggestions[occasion]["description"]
    for item in filtered_items:
        suggestion_text += f'<br><a href="{item["link"]}" target="_blank">{item["name"]}</a>: {item["reason"]}'
    return description + "<br><br>" + suggestion_text

# Rota para a página inicial com o formulário de upload
@app.route("/")
def index():
    return render_template("index.html")

# Rota para perguntar sobre a ocasião
@app.route("/occasion", methods=["POST"])
def occasion():
    if 'file' not in request.files:
        flash("Nenhum arquivo enviado!")
        return redirect("/")

    file = request.files['file']
    if file.filename == '':
        flash("Nenhum arquivo selecionado!")
        return redirect("/")

    upload_folder = os.path.join(app.root_path, "uploads")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_path = os.path.join(upload_folder, file.filename)
    try:
        file.save(file_path)
        Image.open(file_path).verify()  # Verifica se o arquivo é uma imagem válida
    except UnidentifiedImageError:
        flash("Erro ao analisar a imagem: Arquivo de imagem não identificado.")
        return redirect("/")
    except Exception as e:
        flash(f"Erro ao salvar a imagem: {str(e)}")
        return redirect("/")

    return render_template("occasion.html", file_path=file_path)

# Rota para processar a análise da imagem e mostrar resultados
@app.route("/analyze", methods=["POST"])
def analyze():
    occasion = request.form.get("occasion")
    file_path = request.form.get("file_path")

    analysis_result = analyze_image(file_path)
    if "Erro" in analysis_result:
        flash(analysis_result)
        return redirect("/")

    analysis_result_with_links = add_shopping_suggestions(analysis_result, occasion)
    return render_template("result.html", analysis_result=analysis_result_with_links)

if __name__ == "__main__":
    app.run(debug=True)
