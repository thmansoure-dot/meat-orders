// ============================================================
// API CLIENT — يربط البرنامج بـ FastAPI Backend
// ============================================================
const API_BASE = '';  // same origin — Railway serves both

function getToken() {
  return localStorage.getItem('token') || '';
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + getToken()
  };
}

async function apiCall(method, path, body = null) {
  const opts = {
    method,
    headers: authHeaders(),
  };
  if (body !== null) opts.body = JSON.stringify(body);

  const res = await fetch(API_BASE + path, opts);

  if (res.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/';
    return null;
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'خطأ في الخادم');
  }

  return res.json();
}

const API = {
  // Auth
  me:             ()           => apiCall('GET',  '/api/auth/me'),
  getUsers:       ()           => apiCall('GET',  '/api/auth/users'),
  createUser:     (data)       => apiCall('POST', '/api/auth/users', data),
  deleteUser:     (id)         => apiCall('DELETE',`/api/auth/users/${id}`),
  changePassword: (data)       => apiCall('POST', '/api/auth/change-password', data),

  // Orders
  getOrders:      ()           => apiCall('GET',  '/api/orders/'),
  createOrder:    (data)       => apiCall('POST', '/api/orders/', data),
  updateOrder:    (id, data)   => apiCall('PUT',  `/api/orders/${id}`, data),
  deleteOrder:    (id)         => apiCall('DELETE',`/api/orders/${id}`),

  // Suppliers
  getSuppliers:   ()           => apiCall('GET',  '/api/suppliers/'),
  createSupplier: (data)       => apiCall('POST', '/api/suppliers/', data),
  updateSupplier: (id, data)   => apiCall('PUT',  `/api/suppliers/${id}`, data),
  deleteSupplier: (id)         => apiCall('DELETE',`/api/suppliers/${id}`),

  // Companies
  getCompanies:   ()           => apiCall('GET',  '/api/companies/'),
  createCompany:  (data)       => apiCall('POST', '/api/companies/', data),
  updateCompany:  (id, data)   => apiCall('PUT',  `/api/companies/${id}`, data),
  deleteCompany:  (id)         => apiCall('DELETE',`/api/companies/${id}`),
};

// ============================================================
// DATA LAYER — replaces localStorage with API calls
// In-memory cache for speed, synced to server on every change
// ============================================================
let orders    = [];
let suppliers = [];
let companies = [];
let products  = [];
let orderCounter = 0;

async function loadAllData() {
  try {
    showLoadingOverlay(true);
    const [ords, sups, comps] = await Promise.all([
      API.getOrders(),
      API.getSuppliers(),
      API.getCompanies(),
    ]);
    orders    = mapOrders(ords);
    suppliers = mapSuppliers(sups);
    companies = mapCompanies(comps);
    products  = extractProducts(sups);
    orderCounter = orders.length;
    showLoadingOverlay(false);
  } catch(e) {
    showLoadingOverlay(false);
    showToast('⚠️ تعذر تحميل البيانات: ' + e.message, 'error');
  }
}

// Map server format → frontend format
function mapOrders(serverOrders) {
  return (serverOrders || []).map(o => ({
    id:            o.id,
    number:        o.number,
    supplierId:    o.supplier_id,
    companyId:     o.company_id,
    week:          o.week,
    weekYear:      o.week_year,
    date:          o.date,
    deliveryDate:  o.delivery_date,
    deliveryPlace: o.delivery_place,
    payment:       o.payment,
    status:        o.status,
    total:         o.total,
    notes:         o.notes,
    reminderDays:  o.reminder_days,
    reminderNote:  o.reminder_note,
    docsStatus:    o.docs_status,
    docs:          o.docs || [],
    issues:        o.issues || [],
    confirmData:   o.confirm_data,
    confirmDate:   o.confirm_date,
    originalItems: o.original_items,
    originalTotal: o.original_total,
    items:         (o.items || []).map(i => ({
      id:           i.id,
      productName:  i.product_name,
      meatType:     i.meat_type,
      cartons:      i.cartons,
      cartonWeight: i.carton_weight,
      qty:          i.qty,
      price:        i.price,
      note:         i.note,
      cut:          i.cut,
      total:        i.total,
    })),
  }));
}

function mapSuppliers(serverSuppliers) {
  return (serverSuppliers || []).map(s => ({
    id:          s.id,
    name:        s.name,
    country:     s.country,
    address:     s.address,
    contact:     s.contact,
    email:       s.email,
    phone:       s.phone,
    iban:        s.iban,
    swift:       s.swift,
    bank:        s.bank,
    euReg:       s.eu_reg,
    notes:       s.notes,
    certHalal:   s.cert_halal,
    certHealth:  s.cert_health,
    certISO:     s.cert_iso,
    certBRC:     s.cert_brc,
    certOrganic: s.cert_organic,
    lastPriceUpdate: s.last_price_update,
    items:       (s.items || []).map(p => ({
      id:      p.id,
      artno:   p.artno,
      name:    p.name,
      type:    p.type,
      price:   p.price,
      history: p.history || [],
    })),
  }));
}

function mapCompanies(serverCompanies) {
  return (serverCompanies || []).map(c => ({
    id:      c.id,
    name:    c.name,
    nameEn:  c.name_en,
    address: c.address,
    phone:   c.phone,
    email:   c.email,
    reg:     c.reg,
    code:    c.code,
    notes:   c.notes,
    logo:    c.logo,
    color:   c.color,
  }));
}

function extractProducts(serverSuppliers) {
  const prods = [];
  (serverSuppliers || []).forEach(s => {
    (s.items || []).forEach(p => {
      prods.push({ id: p.id, name: p.name, type: p.type, supplierId: s.id, price: p.price, unit: 'كغ', notes: '' });
    });
  });
  return prods;
}

// ── Convert frontend format → server format ──────────────────
function orderToServer(o) {
  return {
    number:         o.number,
    supplier_id:    o.supplierId || null,
    company_id:     o.companyId || null,
    week:           o.week || null,
    week_year:      o.weekYear || null,
    date:           o.date || '',
    delivery_date:  o.deliveryDate || '',
    delivery_place: o.deliveryPlace || '',
    payment:        o.payment || '',
    status:         o.status || 'pending',
    total:          parseFloat(o.total) || 0,
    notes:          o.notes || '',
    reminder_days:  o.reminderDays ? parseInt(o.reminderDays) : null,
    reminder_note:  o.reminderNote || '',
    docs_status:    o.docsStatus || 'ok',
    docs:           o.docs || [],
    issues:         o.issues || [],
    confirm_data:   o.confirmData || null,
    confirm_date:   o.confirmDate || '',
    original_items: o.originalItems || null,
    original_total: o.originalTotal || null,
    items:          (o.items || []).map((i, idx) => ({
      product_name:  i.productName || '',
      meat_type:     i.meatType || '',
      cartons:       parseFloat(i.cartons) || 0,
      carton_weight: parseFloat(i.cartonWeight) || 20,
      qty:           parseFloat(i.qty) || 0,
      price:         parseFloat(i.price) || 0,
      note:          i.note || '',
      cut:           i.cut || '',
      total:         parseFloat(i.total) || 0,
      sort_order:    idx,
    })),
  };
}

function supplierToServer(s) {
  return {
    name:         s.name,
    country:      s.country || 'ألمانيا',
    address:      s.address || '',
    contact:      s.contact || '',
    email:        s.email || '',
    phone:        s.phone || '',
    iban:         s.iban || '',
    swift:        s.swift || '',
    bank:         s.bank || '',
    eu_reg:       s.euReg || '',
    notes:        s.notes || '',
    cert_halal:   !!s.certHalal,
    cert_health:  !!s.certHealth,
    cert_iso:     !!s.certISO,
    cert_brc:     !!s.certBRC,
    cert_organic: !!s.certOrganic,
    last_price_update: s.lastPriceUpdate || '',
    items:        (s.items || []).map(p => ({
      artno:   p.artno || '',
      name:    p.name,
      type:    p.type || 'other',
      price:   parseFloat(p.price) || 0,
      history: p.history || [],
    })),
  };
}

function companyToServer(c) {
  return {
    name:    c.name,
    name_en: c.nameEn || '',
    address: c.address || '',
    phone:   c.phone || '',
    email:   c.email || '',
    reg:     c.reg || '',
    code:    c.code || '',
    notes:   c.notes || '',
    logo:    c.logo || '',
    color:   c.color || '#1a2235',
  };
}

// ── SAVE FUNCTIONS — replace the old localStorage save() ─────
async function saveOrder(order) {
  try {
    let result;
    if (order.id && orders.find(o => o.id === order.id)) {
      result = await API.updateOrder(order.id, orderToServer(order));
      const mapped = mapOrders([result])[0];
      const idx = orders.findIndex(o => o.id === order.id);
      if (idx !== -1) orders[idx] = mapped;
    } else {
      result = await API.createOrder(orderToServer(order));
      const mapped = mapOrders([result])[0];
      orders.unshift(mapped);
      orderCounter++;
    }
    return true;
  } catch(e) {
    showToast('❌ خطأ في الحفظ: ' + e.message, 'error');
    return false;
  }
}

async function saveSupplierToServer(supplier) {
  try {
    let result;
    if (supplier.id && suppliers.find(s => s.id === supplier.id)) {
      result = await API.updateSupplier(supplier.id, supplierToServer(supplier));
      const mapped = mapSuppliers([result])[0];
      const idx = suppliers.findIndex(s => s.id === supplier.id);
      if (idx !== -1) suppliers[idx] = mapped;
    } else {
      result = await API.createSupplier(supplierToServer(supplier));
      const mapped = mapSuppliers([result])[0];
      suppliers.push(mapped);
    }
    products = extractProducts(suppliers.map(s => ({ ...s, items: s.items })));
    return result;
  } catch(e) {
    showToast('❌ خطأ في الحفظ: ' + e.message, 'error');
    return null;
  }
}

async function saveCompanyToServer(company) {
  try {
    let result;
    if (company.id && companies.find(c => c.id === company.id)) {
      result = await API.updateCompany(company.id, companyToServer(company));
      const mapped = mapCompanies([result])[0];
      const idx = companies.findIndex(c => c.id === company.id);
      if (idx !== -1) companies[idx] = mapped;
    } else {
      result = await API.createCompany(companyToServer(company));
      const mapped = mapCompanies([result])[0];
      companies.push(mapped);
    }
    return result;
  } catch(e) {
    showToast('❌ خطأ في الحفظ: ' + e.message, 'error');
    return null;
  }
}

// Loading overlay
function showLoadingOverlay(show) {
  let el = document.getElementById('loading-overlay');
  if (!el) {
    el = document.createElement('div');
    el.id = 'loading-overlay';
    el.style.cssText = 'position:fixed;inset:0;background:rgba(10,14,23,0.85);z-index:9999;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:1rem';
    el.innerHTML = `<div style="font-size:3rem">🥩</div><div style="color:#e8b460;font-family:Cairo,sans-serif;font-size:1.1rem;font-weight:700">جاري تحميل البيانات...</div>`;
    document.body.appendChild(el);
  }
  el.style.display = show ? 'flex' : 'none';
}
