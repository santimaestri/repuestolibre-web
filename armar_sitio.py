#!/usr/bin/env python3
"""Arma las páginas por producto (p/<id>.html), el feed de Google Merchant Center
(feed.xml) y el sitemap.xml a partir de productos.json.

Lo corre la Action `Actualizar productos` después de bajar productos.json.
Sin dependencias: sólo la biblioteca estándar.
"""
import html
import json
import pathlib
import shutil
from xml.sax.saxutils import escape as xesc

BASE = "https://www.repuestolibre.com.ar/"
TIENDA = "https://www.mercadolibre.com.ar/tienda/repuestolibre"
RAIZ = pathlib.Path(__file__).resolve().parent

GRUPO_TEXTO = {
    "Samsung": "celulares Samsung",
    "iPhone": "iPhone",
    "Motorola": "celulares Motorola",
    "Xiaomi": "celulares Xiaomi",
    "Consolas": "joysticks y consolas",
    "Herramientas e insumos": "reparación de celulares",
    "Otros": "reparación",
}


def pesos(n):
    return "$" + f"{round(n):,}".replace(",", ".")


def descripcion(p):
    g = GRUPO_TEXTO.get(p["grupo"], "reparación")
    extra = []
    if p.get("envio_gratis"):
        extra.append("Envío gratis.")
    if p.get("full"):
        extra.append("Llega rápido con Mercado Envíos Full.")
    return (
        f"{p['titulo']}. Repuesto nuevo para {g}. "
        "Se compra por Mercado Libre, con garantía y Compra Protegida. "
        + " ".join(extra)
    ).strip()


def pagina(p):
    t = html.escape(p["titulo"])
    d = html.escape(descripcion(p))
    url_pag = f"{BASE}p/{p['id']}.html"
    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["titulo"],
        "image": p["foto"],
        "description": descripcion(p),
        "sku": p["id"],
        "brand": {"@type": "Brand", "name": "RepuestoLibre"},
        "offers": {
            "@type": "Offer",
            "url": url_pag,
            "price": f"{p['precio']:.2f}",
            "priceCurrency": "ARS",
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition",
        },
    }
    antes = (
        f'<span class="antes">{pesos(p["precio_antes"])}</span>'
        if p.get("precio_antes") and p["precio_antes"] > p["precio"]
        else ""
    )
    tags = ("<span class=\"tag\">Envío gratis</span>" if p.get("envio_gratis") else "") + (
        "<span class=\"tag\">⚡ Full</span>" if p.get("full") else ""
    )
    return f"""<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} — Repuestolibre</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url_pag}">
<meta property="og:title" content="{t}">
<meta property="og:image" content="{html.escape(p['foto'])}">
<meta property="og:type" content="product">
<link rel="icon" href="../logo.svg" type="image/svg+xml">
<meta name="theme-color" content="#0d0d0d">
<link rel="stylesheet" href="../style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="top">
  <div class="wrap top-in">
    <a class="logo" href="../"><img src="../logo.svg" alt="RL" width="62" height="23"><span>Repuestolibre</span></a>
    <a class="btn btn-ml" href="{TIENDA}" target="_blank" rel="noopener">Seguí la tienda en Mercado Libre</a>
  </div>
</header>
<main class="wrap producto">
  <img class="producto-foto" src="{html.escape(p['foto'])}" alt="{t}">
  <div class="producto-info">
    <h1>{t}</h1>
    <div class="precio">{antes}{pesos(p['precio'])}</div>
    <div class="tags">{tags}</div>
    <p>{d}</p>
    <a class="btn btn-ml btn-grande" href="{html.escape(p['url'])}" rel="noopener">Comprar en Mercado Libre</a>
    <p class="nota">Vendemos sólo por Mercado Libre. Las preguntas se hacen en la publicación.</p>
    <p><a href="../">← Ver todos los repuestos</a></p>
  </div>
</main>
<footer class="pie"><div class="wrap"><span>© Repuestolibre · Olivos, Buenos Aires</span><a href="../devoluciones.html">Cambios y devoluciones</a></div></footer>
</body>
</html>
"""


def item_feed(p):
    campos = [
        ("g:id", p["id"]),
        ("title", p["titulo"][:150]),
        ("description", descripcion(p)),
        ("link", f"{BASE}p/{p['id']}.html"),
        ("g:image_link", p["foto"]),
        ("g:availability", "in_stock"),
        ("g:condition", "new"),
        ("g:price", f"{p['precio']:.2f} ARS"),
        ("g:brand", "RepuestoLibre"),
        ("g:identifier_exists", "no"),
        ("g:product_type", p["grupo"]),
    ]
    if p.get("precio_antes") and p["precio_antes"] > p["precio"]:
        campos[7] = ("g:price", f"{p['precio_antes']:.2f} ARS")
        campos.append(("g:sale_price", f"{p['precio']:.2f} ARS"))
    cuerpo = "".join(f"<{k}>{xesc(str(v))}</{k}>" for k, v in campos)
    return f"<item>{cuerpo}</item>"


def main():
    datos = json.loads((RAIZ / "productos.json").read_text())
    prods = datos["productos"]
    assert len(prods) >= 50, f"muy pocos productos: {len(prods)}"

    carpeta = RAIZ / "p"
    if carpeta.exists():
        shutil.rmtree(carpeta)
    carpeta.mkdir()
    for p in prods:
        (carpeta / f"{p['id']}.html").write_text(pagina(p))

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0"><channel>'
        f"<title>Repuestolibre</title><link>{BASE}</link>"
        "<description>Repuestos para celulares y joysticks</description>\n"
        + "\n".join(item_feed(p) for p in prods)
        + "\n</channel></rss>\n"
    )
    (RAIZ / "feed.xml").write_text(feed)

    urls = [BASE, f"{BASE}devoluciones.html"] + [f"{BASE}p/{p['id']}.html" for p in prods]
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"<url><loc>{u}</loc></url>" for u in urls)
        + "\n</urlset>\n"
    )
    (RAIZ / "sitemap.xml").write_text(sitemap)
    print(f"páginas: {len(prods)} · feed: {len(prods)} items · sitemap: {len(urls)} urls")


if __name__ == "__main__":
    main()
