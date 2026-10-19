from fastapi import FastAPI, HTTPException
from curl_cffi import requests
from bs4 import BeautifulSoup

app = FastAPI(title="ML Scraper Microservice")

@app.get("/search")
def search_products(q: str):
    url = f"https://lista.mercadolivre.com.br/{q}"
    
    try:
        response = requests.get(url, impersonate="chrome120", timeout=15)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Erro ao acessar o Mercado Livre")
        
        soup = BeautifulSoup(response.text, "html.parser")
        products = []
        
        cards = soup.select(".poly-card, .ui-search-layout__item")
        
        for card in cards:
            title_elem = card.select_one(".poly-component__title, .ui-search-item__title")
            price_elem = card.select_one(".poly-price__current .andes-money-amount__fraction, .ui-search-price__second-line .andes-money-amount__fraction")
            
            if title_elem and price_elem:
                title = title_elem.get_text(strip=True)
                link = title_elem.get("href")
                
                price_text = price_elem.get_text(strip=True).replace(".", "")
                
                products.append({
                    "title": title,
                    "price": float(price_text),
                    "link": link
                })
        
        return {
            "query": q,
            "total_found": len(products),
            "products": products
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))