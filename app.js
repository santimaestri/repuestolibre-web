(async function () {
  const ORDEN = ['Samsung', 'iPhone', 'Motorola', 'Xiaomi', 'Consolas', 'Herramientas e insumos', 'Otros'];
  const $ = (id) => document.getElementById(id);
  const pesos = (n) => '$' + Math.round(n).toLocaleString('es-AR');
  const norm = (s) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  let datos;
  try {
    datos = await (await fetch('productos.json', { cache: 'no-cache' })).json();
  } catch (e) {
    $('cuenta').textContent = 'No pudimos cargar los productos. Mirá la tienda en Mercado Libre.';
    return;
  }
  const prods = datos.productos.map((p) => ({ ...p, _q: norm(p.titulo) }));
  if (datos.actualizado) $('actualizado').textContent = 'Precios actualizados el ' + datos.actualizado.split('-').reverse().join('/');

  const grupos = ORDEN.filter((g) => prods.some((p) => p.grupo === g));
  let grupo = 'Todos';
  $('grupos').innerHTML = ['Todos', ...grupos]
    .map((g) => `<button class="chip" role="tab" data-g="${esc(g)}" aria-selected="${g === 'Todos'}">${esc(g)}</button>`)
    .join('');
  $('grupos').addEventListener('click', (e) => {
    const b = e.target.closest('.chip');
    if (!b) return;
    grupo = b.dataset.g;
    document.querySelectorAll('.chip').forEach((c) => c.setAttribute('aria-selected', c === b));
    pintar();
  });

  const card = (p) => `
    <a class="card" href="${esc(p.url)}" target="_blank" rel="noopener">
      <img src="${esc(p.foto)}" alt="${esc(p.titulo)}" loading="lazy">
      <div class="card-body">
        <h3>${esc(p.titulo)}</h3>
        <div class="precio">${p.precio_antes && p.precio_antes > p.precio ? `<span class="antes">${pesos(p.precio_antes)}</span>` : ''}${pesos(p.precio)}</div>
        <div class="tags">${p.envio_gratis ? '<span class="tag">Envío gratis</span>' : ''}${p.full ? '<span class="tag">⚡ Full</span>' : ''}</div>
        <span class="btn btn-ml">Comprar en Mercado Libre</span>
      </div>
    </a>`;

  function pintar() {
    const palabras = norm($('buscar').value).split(/\s+/).filter(Boolean);
    const lista = prods.filter(
      (p) => (grupo === 'Todos' || p.grupo === grupo) && palabras.every((w) => p._q.includes(w))
    );
    lista.sort((a, b) => ORDEN.indexOf(a.grupo) - ORDEN.indexOf(b.grupo) || a.titulo.localeCompare(b.titulo, 'es'));
    $('grilla').innerHTML = lista.map(card).join('');
    $('cuenta').textContent = `${lista.length} producto${lista.length === 1 ? '' : 's'}`;
    $('vacio').hidden = lista.length > 0;
  }
  $('buscar').addEventListener('input', pintar);
  pintar();
})();
