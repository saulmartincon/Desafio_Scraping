"""
PARTE 1: Web scraping de https://scrapeme.live/shop/ (tienda falsa de Pokémon)
con BeautifulSoup. Guarda los datos limpios en pokemons.csv usando Pandas.

Flujo:  página del listado -> cada Pokémon -> su ficha -> DataFrame -> CSV
"""

import time
from datetime import date
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL_INICIAL = "https://scrapeme.live/shop/"

# Nos identificamos con un User-Agent (buena práctica ética)
CABECERAS = {"User-Agent": "Mozilla/5.0 (practica-scraping-2DAM; uso educativo)"}

# Pausa entre peticiones para no saturar el servidor (rate limiting)
PAUSA_SEGUNDOS = 0.5

# Para probar rápido pon 1 (solo la primera página). None = todas las páginas
MAX_PAGINAS = None


def obtener_soup(url):
    """Descarga una página y devuelve el HTML analizado por BeautifulSoup."""
    time.sleep(PAUSA_SEGUNDOS)
    respuesta = requests.get(url, headers=CABECERAS, timeout=10)
    respuesta.raise_for_status()   # si hay error (404, 500...) lanza excepción
    respuesta.encoding = "utf-8"   # evita problemas con el símbolo £
    return BeautifulSoup(respuesta.text, "html.parser")


def texto(soup, selector):
    """Devuelve el texto del primer elemento que cumple el selector ('' si no existe)."""
    elemento = soup.select_one(selector)
    return elemento.text.strip() if elemento else ""


def scrapear_ficha(url):
    """Entra en la ficha de un Pokémon y saca stock, peso, categorías, SKU y descripción."""
    soup = obtener_soup(url)

    # Stock: el texto es algo como "179 in stock" -> nos quedamos con el número
    stock_texto = texto(soup, "p.stock")
    primera_palabra = stock_texto.split()[0] if stock_texto else ""
    stock = int(primera_palabra) if primera_palabra.isdigit() else 0

    # Peso: el texto es algo como "6.9 kg" -> lo pasamos a número
    peso_texto = texto(soup, "td.product_weight") or texto(
        soup, "tr.woocommerce-product-attributes-item--weight td"
    )
    try:
        peso = float(peso_texto.replace("kg", "").strip())
    except ValueError:
        peso = None  # si no hay peso, queda vacío (NaN en Pandas)

    # Categorías: un Pokémon puede tener varias (ej: "Pokemon, Seed")
    categorias = ", ".join(a.text.strip() for a in soup.select("span.posted_in a"))

    return {
        "stock": stock,
        "peso_kg": peso,
        "categorias": categorias,
        "sku": texto(soup, "span.sku"),
        "descripcion": texto(soup, "div.woocommerce-product-details__short-description"),
    }


def main():
    pokemons = []
    url = URL_INICIAL
    pagina = 1

    while url:  # mientras exista una página que visitar
        print(f"Scrapeando página {pagina} ...")
        soup = obtener_soup(url)

        # Cada Pokémon del listado es un <li class="product">
        for producto in soup.select("li.product"):
            # El enlace de la web es relativo ("Bulbasaur/index.html"), lo completamos con urljoin
            enlace = urljoin(url, producto.select_one("a.woocommerce-LoopProduct-link")["href"])
            nombre = producto.select_one("h2.woocommerce-loop-product__title").text.strip()

            # Limpieza: "£63.00" -> 63.0 (de texto a número)
            precio_texto = producto.select_one("span.woocommerce-Price-amount").text
            precio = float(precio_texto.replace("£", "").strip())

            datos = {
                "nombre": nombre,
                "precio": precio,
                "imagen": urljoin(url, producto.img["src"]),
                "enlace": enlace,
            }
            datos.update(scrapear_ficha(enlace))  # añadimos los datos de la ficha
            datos["fecha_extraccion"] = date.today().isoformat()
            pokemons.append(datos)

        # Paginación: si hay botón "siguiente" vamos a esa página
        siguiente = soup.select_one("a.next")
        url = urljoin(url, siguiente["href"]) if siguiente else None
        pagina += 1

        if MAX_PAGINAS and pagina > MAX_PAGINAS:
            break

    # Pasamos la lista de diccionarios a un DataFrame de Pandas
    df = pd.DataFrame(pokemons)

    # Convertimos la fecha de texto a tipo fecha
    df["fecha_extraccion"] = pd.to_datetime(df["fecha_extraccion"])

    df.to_csv("pokemons.csv", index=False, encoding="utf-8")
    print(f"\nListo: {len(df)} Pokémon guardados en pokemons.csv")


if __name__ == "__main__":
    main()
