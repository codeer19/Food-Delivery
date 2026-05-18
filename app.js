// ── STATE ─────────────────────────────────────────────────────────────────────

let APP_LOCATION = 'your area';
let userLat = null, userLng = null;
let allRestaurants = [...CHANDIGARH_RESTAURANTS, ...PATIALA_RESTAURANTS, ...RAJPURA_RESTAURANTS];
let cityRestaurants = [];
const data = { featured: [], restaurants: [] };

// ── LOCATION DETECTION ───────────────────────────────────────────────────────

async function detectLocation() {
  try {
    const pos = await new Promise((ok, fail) =>
      navigator.geolocation.getCurrentPosition(ok, fail, { timeout: 8000 })
    );
    userLat = pos.coords.latitude;
    userLng = pos.coords.longitude;
  } catch {
    try {
      const r = await fetch('https://ipapi.co/json/');
      const d = await r.json();
      userLat = d.latitude; userLng = d.longitude;
      APP_LOCATION = d.city || 'your area';
    } catch { userLat = 30.7333; userLng = 76.7794; APP_LOCATION = 'Chandigarh'; }
    return;
  }
  // Reverse geocode
  try {
    const r = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${userLat}&lon=${userLng}&format=json`);
    const d = await r.json();
    APP_LOCATION = d.address?.city || d.address?.town || d.address?.state_district || d.address?.village || d.address?.suburb || 'your area';
  } catch {}
}

function matchCity(detectedCity) {
  const c = detectedCity.toLowerCase().trim();
  const cityMap = {
    'chandigarh': 'Chandigarh',
    'patiala': 'Patiala',
    'rajpura': 'Rajpura',
    'mohali': 'Chandigarh',
    'zirakpur': 'Chandigarh',
    'panchkula': 'Chandigarh',
    'kharar': 'Chandigarh',
    'nabha': 'Patiala',
    'samana': 'Patiala',
  };
  for (const [key, val] of Object.entries(cityMap)) {
    if (c.includes(key)) return val;
  }
  return null;
}

function getRestaurantsForCity(city) {
  if (!city) return allRestaurants;
  return allRestaurants.filter(r => r.city.toLowerCase() === city.toLowerCase());
}

// ── INIT ──────────────────────────────────────────────────────────────────────

let cart = [];
let orderHistory = [];
let activeFilter = 'all';

async function init() {
  renderCart();
  setupFilters();
  setupCartToggle();
  setupSearch();
  setupCitySelector();
  showPage('browse');

  // Loading state
  document.getElementById('restaurantGrid').innerHTML =
    '<div style="grid-column:1/-1;padding:3rem 0;text-align:center;color:var(--ink3)">Detecting your location...</div>';
  document.getElementById('featuredStrip').innerHTML =
    '<div style="padding:1rem;color:var(--ink3);font-size:0.85rem">Loading trending dishes…</div>';

  await detectLocation();
  const matched = matchCity(APP_LOCATION);
  if (matched) APP_LOCATION = matched;

  // Set city selector
  const sel = document.getElementById('citySelector');
  if (sel) {
    const opts = sel.options;
    for (let i = 0; i < opts.length; i++) {
      if (opts[i].value.toLowerCase() === (matched || '').toLowerCase()) {
        sel.selectedIndex = i; break;
      }
    }
  }

  loadCity(matched || 'Chandigarh');
  updateLocationUI();
  console.log(`Location: ${APP_LOCATION} (${userLat}, ${userLng})`);
}

function loadCity(city) {
  APP_LOCATION = city;
  cityRestaurants = getRestaurantsForCity(city);
  data.restaurants = cityRestaurants;
  data.featured = cityRestaurants.slice(0, 6).map(r => ({
    image: r.menu[0]?.items[0]?.image || r.image,
    name: r.menu[0]?.items[0]?.name || 'Special',
    restaurant: r.name,
    price: r.menu[0]?.items[0]?.price || 200,
  }));
  activeFilter = 'all';
  document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
  const allPill = document.querySelector('.filter-pill[data-filter="all"]');
  if (allPill) allPill.classList.add('active');
  renderFeatured();
  renderRestaurants();
  updateLocationUI();
}

function setupCitySelector() {
  const sel = document.getElementById('citySelector');
  if (!sel) return;
  sel.addEventListener('change', () => {
    loadCity(sel.value);
  });
}

function updateLocationUI() {
  const title = document.querySelector('.section-title');
  if (title) title.textContent = `Restaurants in ${APP_LOCATION}`;
}

// ── PAGE SWITCHING ────────────────────────────────────────────────────────────

function showPage(page) {
  document.getElementById('page-browse').style.display = page === 'browse' ? 'block' : 'none';
  document.getElementById('page-orders').style.display = page === 'orders' ? 'block' : 'none';
  document.getElementById('navBrowse').classList.toggle('active', page === 'browse');
  document.getElementById('navOrders').classList.toggle('active', page === 'orders');
  if (page === 'orders') renderOrders();
  if (page === 'browse') window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── FEATURED STRIP ────────────────────────────────────────────────────────────

function renderFeatured() {
  document.getElementById('featuredStrip').innerHTML = data.featured
    .map(f => `
      <div class="featured-item" onclick="quickAdd('${esc(f.name)}','${esc(f.restaurant)}',${f.price},'${esc(f.image)}')">
        <div class="featured-img"><img src="${f.image}" alt="${f.name}" loading="lazy"></div>
        <div class="featured-name">${f.name}</div>
        <div class="featured-rest">${f.restaurant}</div>
        <div class="featured-price">₹${f.price}</div>
      </div>
    `)
    .join('');
}

// ── RESTAURANT GRID ───────────────────────────────────────────────────────────

function renderRestaurants() {
  const list = activeFilter === 'all'
    ? data.restaurants
    : data.restaurants.filter(r => r.tag === activeFilter);

  if (list.length === 0) {
    document.getElementById('restaurantGrid').innerHTML = `
      <div style="grid-column:1/-1;padding:2rem 0;text-align:center;color:var(--ink3);font-size:0.875rem;">
        No restaurants found for this filter.
      </div>`;
    return;
  }

  document.getElementById('restaurantGrid').innerHTML = list.map(r => `
    <div class="restaurant-card" onclick="openModal('${esc(String(r.id))}')">
      <div class="card-img">
        <img src="${r.image}" alt="${r.name}" loading="lazy">
        ${r.badge ? `<span class="card-badge">${r.badge}</span>` : ''}
      </div>
      <div class="card-body">
        <div class="card-name">${r.name}</div>
        ${r.address ? `<div style="font-size:0.72rem;color:var(--ink3);margin-bottom:0.3rem;">${r.address}</div>` : ''}
        <div class="card-meta">
          <span>${r.rating}</span>
          <span class="dot"></span>
          <span>${r.time} min</span>
          <span class="dot"></span>
          <span>${r.fee === 0 ? 'Free delivery' : '₹' + r.fee + ' delivery'}</span>
        </div>
      </div>
    </div>
  `).join('');
}

// ── FILTERS ───────────────────────────────────────────────────────────────────

function setupFilters() {
  document.getElementById('filters').addEventListener('click', e => {
    const pill = e.target.closest('.filter-pill');
    if (!pill) return;
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    activeFilter = pill.dataset.filter;
    renderRestaurants();
  });
}

// ── RESTAURANT MODAL ──────────────────────────────────────────────────────────

function openModal(id) {
  const r = data.restaurants.find(x => String(x.id) === String(id));
  if (!r) return;

  document.getElementById('modalContent').innerHTML = `
    <div class="modal-header">
      <div>
        <div class="modal-title">${r.name}</div>
        <div class="modal-meta">
          ${r.rating} · ${r.time} min ·
          ${r.fee === 0 ? 'Free delivery' : '₹' + r.fee + ' delivery'}
          ${r.address ? ' · ' + r.address : ''}
        </div>
      </div>
      <button class="close-btn" onclick="closeModal(null, true)">✕</button>
    </div>
    <div class="modal-hero-img"><img src="${r.image}" alt="${r.name}"></div>
    ${r.menu.map(sec => `
      <div class="menu-section-title">${sec.section}</div>
      ${sec.items.map(item => `
        <div class="menu-item">
          <div class="menu-img"><img src="${item.image}" alt="${item.name}" loading="lazy"></div>
          <div class="menu-info">
            <div class="menu-name">${item.name}</div>
            <div class="menu-desc">${item.desc}</div>
          </div>
          <div class="menu-right">
            <span class="menu-price">₹${item.price}</span>
            <button class="add-btn" onclick="addToCart('${esc(item.name)}','${esc(r.name)}',${item.price},'${esc(item.image)}')">Add</button>
          </div>
        </div>
      `).join('')}
    `).join('')}
  `;

  document.getElementById('modalOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(e, force) {
  if (!force && e && e.target !== document.getElementById('modalOverlay')) return;
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.style.overflow = '';
}

// ── CART ──────────────────────────────────────────────────────────────────────

function addToCart(name, restaurant, price, image) {
  const existing = cart.find(i => i.name === name && i.restaurant === restaurant);
  if (existing) { existing.qty++; }
  else { cart.push({ name, restaurant, price, image, qty: 1 }); }
  renderCart();
  showToast(`Added ${name} to cart`);
}

function quickAdd(name, restaurant, price, image) {
  addToCart(name, restaurant, price, image);
}

function changeQty(name, restaurant, delta) {
  const item = cart.find(i => i.name === name && i.restaurant === restaurant);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) cart = cart.filter(i => !(i.name === name && i.restaurant === restaurant));
  renderCart();
}

function renderCart() {
  const count = cart.reduce((s, i) => s + i.qty, 0);
  const subtotal = cart.reduce((s, i) => s + i.price * i.qty, 0);
  document.getElementById('cartCount').textContent = count;

  const body = document.getElementById('cartBody');
  const foot = document.getElementById('cartFoot');

  if (cart.length === 0) {
    body.innerHTML = `<div class="cart-empty"><span class="cart-empty-icon"></span>Your cart is empty</div>`;
    foot.innerHTML = `<button class="checkout-btn" disabled>Checkout</button>`;
    return;
  }

  body.innerHTML = cart.map(item => `
    <div class="cart-item">
      <div class="cart-item-img"><img src="${item.image}" alt="${item.name}"></div>
      <div class="cart-item-info">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-rest">${item.restaurant}</div>
      </div>
      <div>
        <div class="qty-control">
          <button class="qty-btn" onclick="changeQty('${esc(item.name)}','${esc(item.restaurant)}',-1)">−</button>
          <span class="qty-num">${item.qty}</span>
          <button class="qty-btn" onclick="changeQty('${esc(item.name)}','${esc(item.restaurant)}',1)">+</button>
        </div>
        <div class="cart-item-price" style="margin-top:4px;text-align:center">₹${item.price * item.qty}</div>
      </div>
    </div>
  `).join('');

  const delivery = 29;
  foot.innerHTML = `
    <div class="total-row"><span style="color:var(--ink2)">Subtotal</span><span>₹${subtotal}</span></div>
    <div class="total-row"><span style="color:var(--ink2)">Delivery</span><span>₹${delivery}</span></div>
    <div class="total-row big"><span>Total</span><span>₹${subtotal + delivery}</span></div>
    <button class="checkout-btn" onclick="checkout()">Place order →</button>
  `;
}

function openCart() {
  document.getElementById('cartDrawer').classList.add('open');
  document.getElementById('overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeCart() {
  document.getElementById('cartDrawer').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
  document.body.style.overflow = '';
}

function setupCartToggle() {
  document.getElementById('cartToggle').addEventListener('click', () => {
    const isOpen = document.getElementById('cartDrawer').classList.contains('open');
    isOpen ? closeCart() : openCart();
  });
}

// ── CHECKOUT ──────────────────────────────────────────────────────────────────

function checkout() {
  const subtotal = cart.reduce((s, i) => s + i.price * i.qty, 0);
  const delivery = 29;
  const total = subtotal + delivery;
  const restaurants = [...new Set(cart.map(i => i.restaurant))].join(', ');
  const now = new Date();

  orderHistory.push({
    restaurant: restaurants,
    date: now.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }),
    items: cart.map(i => ({ ...i })),
    subtotal,
    delivery,
    total,
  });

  cart = [];
  renderCart();
  closeCart();
  showToast('Successfully ordered! Total: Rs.' + total);
  showPage('orders');
}

// ── ORDERS PAGE ───────────────────────────────────────────────────────────────

function renderOrders() {
  const el = document.getElementById('ordersContent');

  if (orderHistory.length === 0) {
    el.innerHTML = `
      <div class="orders-empty">
        <p>No orders yet</p>
        <small>Your order history will appear here.</small><br>
        <button class="browse-btn" onclick="showPage('browse')">Browse restaurants</button>
      </div>`;
    return;
  }

  el.innerHTML = orderHistory.slice().reverse().map((order, i) => `
    <div class="order-card">
      <div class="order-card-head">
        <div>
          <div class="order-restaurant">${order.restaurant}</div>
          <div class="order-date">${order.date}</div>
        </div>
        <span class="order-status delivered">Successfully Ordered</span>
      </div>
      <div class="order-items-list">
        ${order.items.map(it => `<div style="display:flex;justify-content:space-between;padding:2px 0"><span>${it.name} x${it.qty}</span><span>Rs.${it.price * it.qty}</span></div>`).join('')}
      </div>
      <div class="order-billing">
        <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:var(--ink3)"><span>Subtotal</span><span>Rs.${order.subtotal || order.total - 29}</span></div>
        <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:var(--ink3)"><span>Delivery</span><span>Rs.${order.delivery || 29}</span></div>
      </div>
      <div class="order-footer">
        <span class="order-total">Total: Rs.${order.total}</span>
        <button class="reorder-btn" onclick="reorder(${orderHistory.length - 1 - i})">Reorder</button>
      </div>
    </div>
  `).join('');
}

function reorder(idx) {
  const order = orderHistory[idx];
  order.items.forEach(item => addToCart(item.name, item.restaurant, item.price, item.image));
  showPage('browse');
  setTimeout(openCart, 200);
}

// ── SEARCH (Food-based) ──────────────────────────────────────────────────────

function setupSearch() {
  document.getElementById('searchInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') handleSearch();
  });
}

function handleSearch() {
  const q = document.getElementById('searchInput').value.trim();
  if (!q) { loadCity(APP_LOCATION); return; }
  const ql = q.toLowerCase();

  // Search menu items across all restaurants in current city
  const matches = [];
  data.restaurants.forEach(r => {
    const hasMatch = r.menu.some(s => s.items.some(i =>
      i.name.toLowerCase().includes(ql) || i.desc.toLowerCase().includes(ql)
    ));
    const nameMatch = r.name.toLowerCase().includes(ql);
    if (hasMatch || nameMatch) matches.push(r);
  });

  if (matches.length === 0) {
    document.getElementById('restaurantGrid').innerHTML = `
      <div style="grid-column:1/-1;padding:3rem 0;text-align:center;color:var(--ink3)">
        <div style="font-size:2.5rem;margin-bottom:0.8rem"></div>
        <div style="font-size:0.95rem;margin-bottom:0.3rem">No results for "${q}"</div>
        <div style="font-size:0.8rem">Try searching for a dish like "butter chicken" or "pizza"</div>
      </div>`;
    showToast(`No results for "${q}" in ${APP_LOCATION}`);
    return;
  }

  // Temporarily override restaurant list for rendering
  const orig = data.restaurants;
  data.restaurants = matches;
  renderRestaurants();
  data.restaurants = orig;

  const title = document.querySelector('.section-title');
  if (title) title.textContent = `${matches.length} result(s) for "${q}" in ${APP_LOCATION}`;
  showToast(`Found ${matches.length} restaurant(s) with "${q}"`);
}

// ── TOAST ─────────────────────────────────────────────────────────────────────

let toastTimer;

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2500);
}

// ── UTILS ─────────────────────────────────────────────────────────────────────

function esc(str) {
  return String(str).replace(/'/g, "\\'");
}

// ── START ─────────────────────────────────────────────────────────────────────

init();