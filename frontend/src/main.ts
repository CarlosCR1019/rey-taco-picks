import './style.css'
import { createClient } from '@supabase/supabase-js'

// Inicializar Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
let supabase: any = null;

if (supabaseUrl && supabaseAnonKey) {
  supabase = createClient(supabaseUrl, supabaseAnonKey);
}

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div class="app-container">
    <header class="header">
      <div class="logo-container">
        <img src="/logo.jpg" alt="Rey Taco Picks Logo" class="brand-logo" />
        <h1>Rey Taco <span class="logo-accent">Picks</span></h1>
      </div>
      <div class="header-actions">
        <button id="login-btn" class="login-btn">Iniciar Sesión</button>
        <button class="premium-badge">Acceso Premium</button>
      </div>
    </header>

    <main>
      <section class="stats-bar">
        <div class="stat-card">
          <span class="stat-label">ROI % del mes</span>
          <span class="stat-value text-green">+18.4%</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Racha actual</span>
          <span class="stat-value text-gold">4 Victorias</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">% Acierto global</span>
          <span class="stat-value">67.2%</span>
        </div>
      </section>

      <section class="picks-section">
        <h3 class="section-title">
          <span class="live-indicator"></span> 
          Análisis del Día
        </h3>
        
        <div id="picks-container" class="loading">Desencriptando líneas de mercado...</div>
      </section>

      <section class="chart-section">
        <h3 class="section-title">📊 Rendimiento</h3>
        <div class="chart-grid">
          <div class="chart-card">
            <h4>Bankroll Simulado ($MXN)</h4>
            <canvas id="bankroll-chart"></canvas>
          </div>
          <div class="chart-card">
            <h4>Aciertos por Deporte</h4>
            <canvas id="sport-chart"></canvas>
          </div>
        </div>
      </section>
      <section class="history-section">
        <h3 class="section-title">Historial de Operaciones</h3>
        <div class="table-container">
          <table class="history-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Partido</th>
                <th>Pick</th>
                <th>Cuota</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody id="history-container">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
      </section>

      <section class="tickets-section">
        <h3 class="section-title">🏆 Muro de Victorias</h3>
        <p class="tickets-subtitle">Nosotros apostamos. Nosotros ganamos. Aquí está la prueba.</p>
        <div id="tickets-grid" class="tickets-grid">
          <!-- Rendered via JS -->
        </div>
      </section>
    </main>

    <!-- Auth & Subscription Modal -->
    <div id="auth-modal" class="modal-overlay hidden">
      <div class="modal-content">
        <button id="close-modal" class="close-btn">&times;</button>
        
        <div class="auth-tabs">
          <button id="tab-login" class="auth-tab active">🔑 Acceso</button>
          <button id="tab-spei" class="auth-tab">💳 Pagar SPEI</button>
          <button id="tab-code" class="auth-tab">🎟️ Código VIP</button>
        </div>

        <!-- Panel 1: Login / Register -->
        <div id="panel-login" class="auth-panel">
          <div class="modal-header">
            <h2 id="modal-title">Iniciar Sesión</h2>
            <p id="modal-subtitle">Accede a tus picks premium y análisis IA</p>
          </div>
          
          <div class="auth-subtabs">
            <button id="subtab-login" class="subtab active">Entrar</button>
            <button id="subtab-register" class="subtab">Crear Cuenta</button>
          </div>

          <form id="auth-form" class="auth-form">
            <div class="form-group">
              <label>Correo Electrónico</label>
              <input type="email" id="auth-email" required placeholder="carlosds1017@gmail.com" />
            </div>
            <div class="form-group">
              <label>Contraseña</label>
              <input type="password" id="auth-password" required placeholder="••••••••" minlength="6" />
            </div>
            <p id="auth-error" class="auth-error hidden"></p>
            <p id="auth-success" class="auth-success hidden"></p>
            <button type="submit" id="auth-submit-btn" class="submit-btn">Entrar al Sistema</button>
          </form>
        </div>

        <!-- Panel 2: SPEI Transfer -->
        <div id="panel-spei" class="auth-panel hidden">
          <div class="modal-header">
            <h2>💳 Pagar por Transferencia SPEI</h2>
            <p>Acceso VIP instantáneo sin comisiones extras</p>
          </div>
          
          <div class="spei-card">
            <div class="spei-row">
              <span class="spei-label">Banco:</span>
              <strong class="spei-val">BBVA México</strong>
            </div>
            <div class="spei-row">
              <span class="spei-label">Titular:</span>
              <strong class="spei-val">Carlos Alberto Gutierrez Ramirez</strong>
            </div>
            <div class="spei-row">
              <span class="spei-label">Cuenta CLABE:</span>
              <div class="clabe-copy-box">
                <code id="clabe-number">012180015228133759</code>
                <button id="copy-clabe-btn" class="copy-btn" title="Copiar CLABE">📋 Copiar</button>
              </div>
            </div>
            <div class="spei-row">
              <span class="spei-label">Cuenta:</span>
              <strong class="spei-val">152 281 3375</strong>
            </div>
            <div class="spei-row">
              <span class="spei-label">Monto sugerido:</span>
              <strong class="spei-val text-green">$299 MXN / Mes</strong>
            </div>
            <div class="spei-row">
              <span class="spei-label">Concepto:</span>
              <strong class="spei-val text-gold">Tu Nombre o Correo</strong>
            </div>
          </div>

          <div class="spei-action">
            <p class="spei-note">Una vez hecha tu transferencia, envíanos la captura para activarte de inmediato:</p>
            <a id="whatsapp-spei-btn" href="https://wa.me/525546921238?text=Hola%20Carlos,%20ya%20realic%C3%A9%20mi%20transferencia%20para%20Rey%20Taco%20Picks%20VIP.%20Mi%20correo%20es:%20" target="_blank" class="whatsapp-btn">
              📲 Enviar Comprobante por WhatsApp
            </a>
          </div>
        </div>

        <!-- Panel 3: VIP Code Redemption -->
        <div id="panel-code" class="auth-panel hidden">
          <div class="modal-header">
            <h2>🎟️ Canjear Código de Acceso VIP</h2>
            <p>Si pagaste por transferencia y recibiste tu código, ingrésalo aquí</p>
          </div>
          
          <form id="code-form" class="auth-form">
            <div class="form-group">
              <label>Código de Activación</label>
              <input type="text" id="vip-code-input" required placeholder="Ej. TACOVIP2026" style="text-transform: uppercase; font-weight: bold; letter-spacing: 2px;" />
            </div>
            <p id="code-msg" class="auth-error hidden"></p>
            <button type="submit" id="redeem-btn" class="submit-btn btn-gold">Activar Pase VIP</button>
          </form>
        </div>

      </div>
    </div>
  </div>
`

// State
let currentUser: any = null;
let isSubscribed = false;
let isLoginMode = true;

// Restore session from localStorage
try {
  const savedUser = localStorage.getItem('rey_taco_user');
  if (savedUser) {
    currentUser = JSON.parse(savedUser);
    if (currentUser.email === 'carlosds1017@gmail.com' || currentUser.is_premium) {
      isSubscribed = true;
    }
  }
} catch (e) {}

// Admin auto-check: if currentUser is carlosds1017@gmail.com, grant full access
if (currentUser?.email === 'carlosds1017@gmail.com') {
  isSubscribed = true;
}

// Auth UI Logic
const authModal = document.getElementById('auth-modal')!;
const closeModalBtn = document.getElementById('close-modal')!;
const loginBtn = document.getElementById('login-btn')!;
const premiumBadge = document.querySelector('.premium-badge') as HTMLButtonElement;

const tabLogin = document.getElementById('tab-login')!;
const tabSpei = document.getElementById('tab-spei')!;
const tabCode = document.getElementById('tab-code')!;

const panelLogin = document.getElementById('panel-login')!;
const panelSpei = document.getElementById('panel-spei')!;
const panelCode = document.getElementById('panel-code')!;

const subtabLogin = document.getElementById('subtab-login')!;
const subtabRegister = document.getElementById('subtab-register')!;
const modalTitle = document.getElementById('modal-title')!;
const modalSubtitle = document.getElementById('modal-subtitle')!;
const authForm = document.getElementById('auth-form') as HTMLFormElement;
const emailInput = document.getElementById('auth-email') as HTMLInputElement;
const passwordInput = document.getElementById('auth-password') as HTMLInputElement;
const errorMsg = document.getElementById('auth-error')!;
const successMsg = document.getElementById('auth-success')!;
const submitBtn = document.getElementById('auth-submit-btn') as HTMLButtonElement;

const copyClabeBtn = document.getElementById('copy-clabe-btn')!;
const codeForm = document.getElementById('code-form') as HTMLFormElement;
const vipCodeInput = document.getElementById('vip-code-input') as HTMLInputElement;
const codeMsg = document.getElementById('code-msg')!;

function switchMainTab(tab: 'login' | 'spei' | 'code') {
  [tabLogin, tabSpei, tabCode].forEach(t => t.classList.remove('active'));
  [panelLogin, panelSpei, panelCode].forEach(p => p.classList.add('hidden'));

  if (tab === 'login') {
    tabLogin.classList.add('active');
    panelLogin.classList.remove('hidden');
  } else if (tab === 'spei') {
    tabSpei.classList.add('active');
    panelSpei.classList.remove('hidden');
  } else if (tab === 'code') {
    tabCode.classList.add('active');
    panelCode.classList.remove('hidden');
  }
}

tabLogin.addEventListener('click', () => switchMainTab('login'));
tabSpei.addEventListener('click', () => switchMainTab('spei'));
tabCode.addEventListener('click', () => switchMainTab('code'));

function openModal(defaultTab: 'login' | 'spei' | 'code' = 'login') {
  switchMainTab(defaultTab);
  authModal.classList.remove('hidden');
}

function closeModal() {
  authModal.classList.add('hidden');
  errorMsg.classList.add('hidden');
  successMsg.classList.add('hidden');
  codeMsg.classList.add('hidden');
}

function updateSubtabUI() {
  errorMsg.classList.add('hidden');
  successMsg.classList.add('hidden');
  if (isLoginMode) {
    subtabLogin.classList.add('active');
    subtabRegister.classList.remove('active');
    modalTitle.textContent = 'Iniciar Sesión';
    modalSubtitle.textContent = 'Accede a tus picks premium y análisis IA';
    submitBtn.textContent = 'Entrar al Sistema';
  } else {
    subtabRegister.classList.add('active');
    subtabLogin.classList.remove('active');
    modalTitle.textContent = 'Crear Cuenta';
    modalSubtitle.textContent = 'Únete y recibe predicciones de alto valor';
    submitBtn.textContent = 'Registrarse';
  }
}

loginBtn.addEventListener('click', () => {
  if (currentUser) {
    // Logout confirmation
    if (confirm(`¿Cerrar sesión de ${currentUser.email}?`)) {
      currentUser = null;
      isSubscribed = false;
      localStorage.removeItem('rey_taco_user');
      if (supabase) supabase.auth.signOut();
      updateAuthHeaderState();
      fetchPicks();
    }
  } else {
    openModal('login');
  }
});

closeModalBtn.addEventListener('click', closeModal);
authModal.addEventListener('click', (e) => {
  if (e.target === authModal) closeModal();
});

subtabLogin.addEventListener('click', () => { isLoginMode = true; updateSubtabUI(); });
subtabRegister.addEventListener('click', () => { isLoginMode = false; updateSubtabUI(); });

premiumBadge?.addEventListener('click', () => {
  if (!isSubscribed) {
    openModal('spei');
  }
});

// Copy CLABE
copyClabeBtn?.addEventListener('click', () => {
  navigator.clipboard.writeText('012180015228133759');
  copyClabeBtn.textContent = '✅ ¡Copiada!';
  setTimeout(() => { copyClabeBtn.textContent = '📋 Copiar'; }, 2500);
});

// VIP Code Redemption
codeForm?.addEventListener('submit', (e) => {
  e.preventDefault();
  const code = vipCodeInput.value.trim().toUpperCase();
  const validCodes = ['REYTACOVIP', 'TACOVIP2026', 'CARLOSVIP', 'GOLDENPICK'];
  
  if (validCodes.includes(code)) {
    isSubscribed = true;
    currentUser = { email: currentUser?.email || 'VIP Member', is_premium: true };
    localStorage.setItem('rey_taco_user', JSON.stringify(currentUser));
    codeMsg.className = 'auth-success';
    codeMsg.textContent = '🎉 ¡Código válido! Acceso VIP activado con éxito.';
    codeMsg.classList.remove('hidden');
    updateAuthHeaderState();
    setTimeout(() => {
      closeModal();
      fetchPicks();
    }, 1500);
  } else {
    codeMsg.className = 'auth-error';
    codeMsg.textContent = '❌ Código no válido o expirado. Contacta a soporte por WhatsApp.';
    codeMsg.classList.remove('hidden');
  }
});

function updateAuthHeaderState() {
  if (currentUser?.email === 'carlosds1017@gmail.com') {
    loginBtn.textContent = '👑 Admin (Carlos)';
    premiumBadge.innerHTML = '👑 Admin VIP';
    premiumBadge.classList.add('badge-gold');
  } else if (isSubscribed) {
    loginBtn.textContent = `👤 ${currentUser?.email?.split('@')[0] || 'Usuario'}`;
    premiumBadge.innerHTML = '👑 VIP Activado';
    premiumBadge.classList.add('badge-gold');
  } else if (currentUser) {
    loginBtn.textContent = `👤 ${currentUser?.email?.split('@')[0] || 'Usuario'}`;
    premiumBadge.innerHTML = 'Pagar VIP';
    premiumBadge.classList.remove('badge-gold');
  } else {
    loginBtn.textContent = 'Iniciar Sesión';
    premiumBadge.innerHTML = 'Acceso Premium';
    premiumBadge.classList.remove('badge-gold');
  }
}

// Auth Logic (Supabase + Admin Bypass)
authForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = emailInput.value.trim();
  const password = passwordInput.value;
  
  submitBtn.disabled = true;
  submitBtn.textContent = "Procesando...";
  errorMsg.classList.add('hidden');
  successMsg.classList.add('hidden');

  // Direct Admin Login for Carlos
  if (email.toLowerCase() === 'carlosds1017@gmail.com') {
    currentUser = { email: 'carlosds1017@gmail.com', is_premium: true, role: 'admin' };
    isSubscribed = true;
    localStorage.setItem('rey_taco_user', JSON.stringify(currentUser));
    successMsg.textContent = '👑 ¡Bienvenido, Administrador Carlos!';
    successMsg.classList.remove('hidden');
    updateAuthHeaderState();
    setTimeout(() => {
      closeModal();
      fetchPicks();
    }, 1000);
    submitBtn.disabled = false;
    return;
  }

  if (!supabase) {
    errorMsg.textContent = "Error: Base de datos no conectada.";
    errorMsg.classList.remove('hidden');
    submitBtn.disabled = false;
    return;
  }

  try {
    if (isLoginMode) {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
      
      // Check if user is premium in profiles table
      let isPrem = false;
      try {
        const { data: profile } = await supabase.from('profiles').select('is_premium').eq('id', data.user.id).single();
        if (profile?.is_premium) isPrem = true;
      } catch (pe) {}

      currentUser = { email: data.user.email, id: data.user.id, is_premium: isPrem };
      isSubscribed = isPrem;
      localStorage.setItem('rey_taco_user', JSON.stringify(currentUser));
      
      successMsg.textContent = '✅ ¡Sesión iniciada con éxito!';
      successMsg.classList.remove('hidden');
      updateAuthHeaderState();
      setTimeout(() => {
        closeModal();
        fetchPicks();
      }, 1000);
    } else {
      const { data, error } = await supabase.auth.signUp({ email, password });
      if (error) throw error;
      
      currentUser = { email: data.user?.email || email, id: data.user?.id, is_premium: false };
      localStorage.setItem('rey_taco_user', JSON.stringify(currentUser));
      
      successMsg.textContent = '✅ Cuenta creada con éxito. Ahora puedes adquirir tu pase VIP por SPEI.';
      successMsg.classList.remove('hidden');
      updateAuthHeaderState();
      setTimeout(() => {
        switchMainTab('spei');
      }, 1500);
    }
  } catch (err: any) {
    errorMsg.textContent = err.message || "Error al procesar la solicitud.";
    errorMsg.classList.remove('hidden');
  } finally {
    submitBtn.disabled = false;
  }
});

// Initial header state
updateAuthHeaderState();


function getSportColorClass(sport: string) {
  const s = sport.toLowerCase();
  if (s.includes('fútbol') || s.includes('futbol') || s.includes('soccer')) return 'tag-green';
  if (s.includes('mlb') || s.includes('beisbol') || s.includes('baseball')) return 'tag-blue';
  if (s.includes('nfl') || s.includes('americano') || s.includes('football')) return 'tag-orange';
  return 'tag-default';
}

function renderPicks(picks: any[]) {
  const container = document.getElementById('picks-container')!;
  if (!picks || picks.length === 0) {
    container.innerHTML = '<div class="loading">No hay picks disponibles hoy.</div>';
    container.className = '';
    return;
  }

  container.className = 'picks-grid';
  
  container.innerHTML = picks.map((pick: any, index: number) => {
    const isLocked = index > 0 && !isSubscribed;
    const sportClass = getSportColorClass(pick.categoria || pick.deporte || '');
    const confValue = parseInt(pick.confianza) || 0;
    
    return `
      <div class="pick-card ${isLocked ? 'locked' : ''} ${pick.es_parlay ? 'parlay-card' : ''}">
        ${isLocked ? `
          <div class="paywall-overlay">
            <div class="lock-icon">🔒</div>
            <h4>Contenido Premium</h4>
            <p>Suscríbete para desbloquear el análisis completo y multiplicar tus ganancias.</p>
            <button class="unlock-btn" onclick="document.querySelector('.premium-badge').click()">Suscribirse / Iniciar Sesión</button>
          </div>
        ` : ''}
        
        <div class="card-content ${isLocked ? 'blurred' : ''}">
          <div class="card-header">
            <span class="sport-tag ${sportClass}">${pick.categoria || pick.deporte || 'Mercado'}</span>
            ${pick.tiene_valor ? '<span class="value-badge">VALOR DETECTADO</span>' : ''}
          </div>
          
          <div class="card-body">
            <h4 class="match-name">${pick.partido || pick.evento}</h4>
            
            <div class="the-pick">
              <span class="pick-text">${pick.pick}</span>
              <div class="odds-container">
                <span class="pick-odds">${pick.cuota}</span>
                ${pick.odds_mercado ? `<span class="market-odds">Cuota Mercado: ${pick.odds_mercado}</span>` : ''}
              </div>
            </div>

            <div class="confidence-container">
              <div class="confidence-header">
                <span>Nivel de Confianza</span>
                <span>${pick.confianza || (confValue + '%')}</span>
              </div>
              <div class="confidence-bar-bg">
                <div class="confidence-bar-fill" style="width: ${confValue}%"></div>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <p class="ai-reasoning"><strong>Alpha (IA):</strong> ${pick.razonamiento}</p>
          </div>
        </div>
      </div>
    `
  }).join('');
}

async function fetchPicks() {
  if (supabase) {
    try {
      const { data, error } = await supabase.from('picks').select('*').order('id', { ascending: true });
      if (error) throw error;
      renderPicks(data);
    } catch (err) {
      console.error("Error cargando desde Supabase:", err);
      fallbackLocalFetch();
    }
  } else {
    fallbackLocalFetch();
  }
}

function fallbackLocalFetch() {
  // Fake data just for preview if local fetch fails or no JSON
  const fakePicks = [
    {
      categoria: 'Fútbol',
      partido: 'Real Madrid vs Barcelona',
      pick: 'Real Madrid ML',
      cuota: '2.10',
      odds_mercado: '1.95',
      tiene_valor: true,
      confianza: '85%',
      razonamiento: 'El modelo detecta una ventaja significativa debido a las lesiones recientes del equipo visitante.',
      es_parlay: false
    },
    {
      categoria: 'MLB',
      partido: 'Yankees vs Red Sox',
      pick: 'Yankees -1.5',
      cuota: '1.85',
      odds_mercado: '1.80',
      tiene_valor: false,
      confianza: '70%',
      razonamiento: 'Pitcher abridor con ERA muy bajo en casa.',
      es_parlay: true
    }
  ];
  
  renderPicks(fakePicks);
}

function renderHistory(history: any[]) {
  const container = document.getElementById('history-container')!;
  if (!history || history.length === 0) {
    container.innerHTML = '<tr><td colspan="5" class="text-center">No hay historial disponible.</td></tr>';
    return;
  }
  
  container.innerHTML = history.map((item: any) => {
    let statusClass = 'status-pending';
    let statusText = 'Pendiente';
    if (item.estado === 'ganado') {
      statusClass = 'status-won';
      statusText = 'Ganado';
    } else if (item.estado === 'perdido') {
      statusClass = 'status-lost';
      statusText = 'Perdido';
    }

    return `
      <tr>
        <td>${item.fecha || item.fecha_generacion || 'N/A'}</td>
        <td>${item.partido || item.evento || 'N/A'}</td>
        <td>${item.pick}</td>
        <td>${item.cuota}</td>
        <td><span class="status-badge ${statusClass}">${statusText}</span></td>
      </tr>
    `;
  }).join('');
}

async function fetchHistory() {
  if (supabase) {
    try {
      const today = new Date().toISOString().split('T')[0];
      const { data, error } = await supabase.from('picks').select('*').neq('fecha_generacion', today).order('id', { ascending: false }).limit(20);
      if (error) throw error;
      if (data && data.length > 0) {
        renderHistory(data);
      } else {
        fallbackLocalHistory();
      }
    } catch (err) {
      console.error("Error cargando historial:", err);
      fallbackLocalHistory();
    }
  } else {
    fallbackLocalHistory();
  }
}

function fallbackLocalHistory() {
  const fakeHistory = [
    { fecha: '2023-10-25', partido: 'Lakers vs Suns', pick: 'Lakers -3.5', cuota: '1.90', estado: 'ganado' },
    { fecha: '2023-10-24', partido: 'Arsenal vs Sevilla', pick: 'Arsenal ML', cuota: '1.55', estado: 'perdido' },
    { fecha: '2023-10-24', partido: 'Chiefs vs Chargers', pick: 'Over 48.5', cuota: '1.90', estado: 'ganado' },
    { fecha: '2023-10-26', partido: 'Heat vs Celtics', pick: 'Heat +5.5', cuota: '1.90', estado: 'pendiente' },
  ];
  renderHistory(fakeHistory);
}

fetchPicks();
fetchHistory();
loadTickets();

function loadTickets() {
  const grid = document.getElementById('tickets-grid');
  if (!grid) return;
  
  // Try to load tickets from the /tickets/ folder
  // We'll check for known ticket files
  const ticketFiles: string[] = [];
  
  // Scan for ticket images (we'll try sequential names)
  const checkTicket = (filename: string) => {
    const img = new Image();
    img.onload = () => {
      ticketFiles.push(filename);
      renderTickets(ticketFiles);
    };
    img.src = `/tickets/${filename}`;
  };
  
  // Check for recently saved tickets (timestamp-based names)
  const now = Math.floor(Date.now() / 1000);
  for (let i = 0; i < 20; i++) {
    const ts = now - (i * 86400); // Check last 20 days
    checkTicket(`ticket_${ts}.jpg`);
  }
  
  // Also try numbered tickets
  for (let i = 1; i <= 10; i++) {
    checkTicket(`ticket_${i}.jpg`);
  }
  
  // Show placeholder if no tickets found after a delay
  setTimeout(() => {
    if (ticketFiles.length === 0) {
      grid.innerHTML = '<p class="tickets-empty">📸 Envía fotos de tickets ganadores al bot de Telegram y aparecerán aquí automáticamente.</p>';
    }
  }, 2000);
}

function renderTickets(files: string[]) {
  const grid = document.getElementById('tickets-grid');
  if (!grid) return;
  
  grid.innerHTML = files.map(f => `
    <div class="ticket-card">
      <img src="/tickets/${f}" alt="Ticket Ganador" loading="lazy" />
    </div>
  `).join('');
}

// ============================================================
//  CHARTS (Chart.js)
// ============================================================
declare const Chart: any;

function initCharts() {
  // Bankroll Chart (Line)
  const bankrollCtx = document.getElementById('bankroll-chart') as HTMLCanvasElement;
  if (bankrollCtx && typeof Chart !== 'undefined') {
    new Chart(bankrollCtx, {
      type: 'line',
      data: {
        labels: ['Día 1', 'Día 2', 'Día 3', 'Día 4', 'Día 5', 'Día 6', 'Día 7'],
        datasets: [{
          label: 'Bankroll ($MXN)',
          data: [1000, 1020, 990, 1050, 1080, 1060, 1110],
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#22c55e',
          pointBorderColor: '#22c55e',
          pointRadius: 4,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#94a3b8' }
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#94a3b8', callback: (v: number) => '$' + v }
          }
        }
      }
    });
  }

  // Sport Accuracy Chart (Doughnut)
  const sportCtx = document.getElementById('sport-chart') as HTMLCanvasElement;
  if (sportCtx && typeof Chart !== 'undefined') {
    new Chart(sportCtx, {
      type: 'doughnut',
      data: {
        labels: ['Fútbol', 'MLB', 'NFL', 'MMA', 'Tenis'],
        datasets: [{
          data: [72, 65, 58, 80, 60],
          backgroundColor: [
            '#22c55e',
            '#3b82f6',
            '#f97316',
            '#ef4444',
            '#a855f7'
          ],
          borderColor: '#111827',
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#94a3b8', padding: 16, font: { size: 12 } }
          }
        },
        cutout: '65%'
      }
    });
  }
}

// Initialize charts after DOM is ready
setTimeout(initCharts, 500);
