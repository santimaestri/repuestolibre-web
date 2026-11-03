# Repuestolibre — web

Catálogo público de Repuestolibre. Cada producto lleva a su publicación de Mercado Libre: la venta es sólo por ML.

- `index.html`, `style.css`, `app.js`: la página (sin build, GitHub Pages).
- `productos.json`: lo escribe la Action `Actualizar productos` todos los días a las 08:00 (ARG), con los datos que devuelve el flujo de n8n `WEB - Catálogo Repuestolibre (solo lectura)` (`gBoL620J1EUInt48`).
- Si n8n devuelve menos de 50 productos, la Action falla y la web queda como estaba.
