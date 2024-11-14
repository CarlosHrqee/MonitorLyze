from flask import Flask, request, jsonify
import asyncio
import os
from playwright.async_api import async_playwright

app = Flask(__name__)

async def scrape_reclameaqui_data(url):
    async with async_playwright() as p:
        # Iniciar o navegador
        browser = await p.chromium.connect(os.environ['BROWSER_PLAYWRIGHT_ENDPOINT'])

        # Criar um único contexto com ajustes para ignorar HTTPS errors
        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )

        # Adicionar script anti-detecção de webdriver e outras modificações
        await context.add_init_script("""
            const defaultGetter = Object.getOwnPropertyDescriptor(
                Navigator.prototype,
                "webdriver"
            )?.get;
            if (defaultGetter) {
                Object.defineProperty(Navigator.prototype, "webdriver", {
                    get: new Proxy(defaultGetter, {
                        apply: (target, thisArg, args) => {
                            Reflect.apply(target, thisArg, args);
                            return false;
                        },
                    }),
                });
            }
        """)

        # Abrir uma nova página no contexto
        page1 = await context.new_page()
        await page1.goto(url, wait_until="load")

        # Aguardar o carregamento dos elementos
        await page1.wait_for_selector("span.go1306724026")
        await page1.wait_for_selector("span.go2549335548")

        # Extrair o texto do primeiro elemento <span> com a classe "go1306724026"
        span_element_1 = await page1.query_selector("span.go1306724026")
        span_text_1 = await span_element_1.inner_text()

        # Etiquetas para os elementos <span> com a classe "go2549335548"
        labels = [
            "Número de reclamações",
            "Taxa de respostas",
            "Reclamações aguardando respostas",
            "Reclamações avaliadas e nota do consumidor",
            "Taxa de clientes que voltariam a fazer negócios",
            "Taxa de solução das reclamações",
            "Tempo médio de respostas"
        ]

        # Extrair e montar o dicionário com os dados
        span_elements = await page1.query_selector_all("span.go2549335548")
        data = {"Nota geral": span_text_1}

        # Iterar sobre cada elemento <span> e associar com as etiquetas
        for index, element in enumerate(span_elements):
            span_text = await element.inner_text()
            label = labels[index] if index < len(labels) else f"Elemento {index + 1}"
            data[label] = span_text

        # Fechar o navegador
        await browser.close()

        return data

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Parâmetro 'url' é obrigatório"}), 400

    # Usar asyncio.run para chamar a função assíncrona
    data = asyncio.run(scrape_reclameaqui_data(url))
    return jsonify(data)

if __name__ == '__main__':
    app.run()
