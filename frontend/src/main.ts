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

    <!-- Auth Modal -->
    <div id="auth-modal" class="modal-overlay hidden">
      <div class="modal-content">
        <button id="close-modal" class="close-btn">&times;</button>
        <div class="modal-header">
          <h2 id="modal-title">Iniciar Sesión</h2>
          <p id="modal-subtitle">Accede a tus picks premium</p>
        </div>
        
        <div class="auth-tabs">
          <button id="tab-login" class="auth-tab active">Entrar</button>
          <button id="tab-register" class="auth-tab">Registrarse</button>
        </div>

        <form id="auth-form" class="auth-form">
          <div class="form-group">
            <label>Correo Electrónico</label>
            <input type="email" id="auth-email" required placeholder="tu@correo.com" />
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input type="password" id="auth-password" required placeholder="••••••••" minlength="6" />
          </div>
          <p id="auth-error" class="auth-error hidden"></p>
          <button type="submit" id="auth-submit-btn" class="submit-btn">Entrar al Sistema</button>
        </form>
      </div>
    </div>
  </div>
`

// State
let isSubscribed = false;
let isLoginMode = true;

// Auth UI Logic
const authModal = document.getElementById('auth-modal')!;
const closeModalBtn = document.getElementById('close-modal')!;
const loginBtn = document.getElementById('login-btn')!;
const premiumBadge = document.querySelector('.premium-badge') as HTMLButtonElement;
const tabLogin = document.getElementById('tab-login')!;
const tabRegister = document.getElementById('tab-register')!;
const modalTitle = document.getElementById('modal-title')!;
const modalSubtitle = document.getElementById('modal-subtitle')!;
const authForm = document.getElementById('auth-form') as HTMLFormElement;
const emailInput = document.getElementById('auth-email') as HTMLInputElement;
const passwordInput = document.getElementById('auth-password') as HTMLInputElement;
const errorMsg = document.getElementById('auth-error')!;
const submitBtn = document.getElementById('auth-submit-btn')!;

function openModal(isLogin: boolean = true) {
  isLoginMode = isLogin;
  updateModalUI();
  authModal.classList.remove('hidden');
}

function closeModal() {
  authModal.classList.add('hidden');
  errorMsg.classList.add('hidden');
  authForm.reset();
}

function updateModalUI() {
  errorMsg.classList.add('hidden');
  if (isLoginMode) {
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    modalTitle.textContent = 'Iniciar Sesión';
    modalSubtitle.textContent = 'Accede a tus picks premium';
    submitBtn.textContent = 'Entrar al Sistema';
  } else {
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    modalTitle.textContent = 'Crear Cuenta';
    modalSubtitle.textContent = 'Únete a Rey Taco Picks';
    submitBtn.textContent = 'Registrarse';
  }
}

loginBtn.addEventListener('click', () => openModal(true));
closeModalBtn.addEventListener('click', closeModal);
authModal.addEventListener('click', (e) => {
  if (e.target === authModal) closeModal();
});

tabLogin.addEventListener('click', () => { isLoginMode = true; updateModalUI(); });
tabRegister.addEventListener('click', () => { isLoginMode = false; updateModalUI(); });

premiumBadge?.addEventListener('click', () => {
  if (!isSubscribed) {
    openModal(false);
  }
});

// Auth Logic (Supabase)
authForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!supabase) {
    errorMsg.textContent = "Error: Base de datos no conectada.";
    errorMsg.classList.remove('hidden');
    return;
  }

  const email = emailInput.value;
  const password = passwordInput.value;
  submitBtn.disabled = true;
  submitBtn.textContent = "Procesando...";
  errorMsg.classList.add('hidden');

  try {
    if (isLoginMode) {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
    } else {
      const { error } = await supabase.auth.signUp({ email, password });
      if (error) throw error;
    }
    closeModal();
  } catch (err: any) {
    errorMsg.textContent = err.message || "Error al procesar la solicitud.";
    errorMsg.classList.remove('hidden');
  } finally {
    submitBtn.disabled = false;
    updateModalUI();
  }
});

if (supabase) {
  isSubscribed = true;
  loginBtn.textContent = 'Modo Administrador';
  premiumBadge.innerHTML = '👑 VIP Activado';
  
  supabase.auth.onAuthStateChange(async () => {
    fetchPicks();
    fetchHistory();
  });
}

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
