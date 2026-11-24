# Práctica PrDesafio01: Web Scraping + Streamlit

Scraping de [ScrapeMe](https://scrapeme.live/shop/) (tienda de Pokémon creada para practicar scraping) con BeautifulSoup, almacenamiento en CSV con Pandas y dashboard interactivo con Streamlit.

## Archivos
- `scraper.py`: extrae los Pokémon (nombre, precio, stock, peso, categorías, SKU, descripción, enlace, imagen, fecha) y genera `pokemons.csv`.
- `app.py`: dashboard Streamlit con filtros, tabla y gráficos.
- `requirements.txt`: librerías necesarias.

## Cómo ejecutarlo
```
pip install -r requirements.txt
python scraper.py
streamlit run app.py
```

## Buenas prácticas aplicadas
- User-Agent propio en cada petición.
- Pausa entre peticiones (`time.sleep`).
- Datos limpios en Python (precio, stock y peso a número, fecha a tipo fecha).
