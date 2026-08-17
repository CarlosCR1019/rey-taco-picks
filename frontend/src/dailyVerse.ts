export interface BlessingVerse {
  text: string;
  reference: string;
  focus: string;
}

export const BLESSING_VERSES: BlessingVerse[] = [
  {
    text: "Será como árbol plantado junto a corrientes de aguas, que da su fruto en su tiempo y su hoja no cae; y todo lo que hace, prosperará.",
    reference: "Salmo 1:3",
    focus: "Prosperidad y Fruto"
  },
  {
    text: "Sea la gracia del Señor nuestro Dios sobre nosotros, y confirma sobre nosotros la obra de nuestras manos; sí, la obra de nuestras manos confirma.",
    reference: "Salmo 90:17",
    focus: "Bendición del Trabajo"
  },
  {
    text: "Encomienda a Jehová tu camino, confía en él; y él hará.",
    reference: "Salmo 37:5",
    focus: "Dirección y Confianza"
  },
  {
    text: "Jehová guardará tu salida y tu entrada desde ahora y para siempre.",
    reference: "Salmo 121:8",
    focus: "Protección Total"
  },
  {
    text: "Pon en manos del Señor todas tus obras, y tus proyectos se cumplirán.",
    reference: "Proverbios 16:3",
    focus: "Éxito en Proyectos"
  },
  {
    text: "Jehová es mi pastor; nada me faltará.",
    reference: "Salmo 23:1",
    focus: "Paz y Provisión"
  },
  {
    text: "Mira que te mando que te esfuerces y seas valiente; no temas ni desmayes, porque Jehová tu Dios estará contigo dondequiera que vayas.",
    reference: "Josué 1:9",
    focus: "Fuerza y Victoria"
  }
];

export function initDailyVerseBanner(containerId: string = 'daily-verse-container') {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Verificar si el usuario lo ocultó en esta sesión
  const isDismissed = sessionStorage.getItem('daily_verse_dismissed') === 'true';
  if (isDismissed) {
    container.innerHTML = '';
    return;
  }

  // Selección diaria determinista por fecha (día del año)
  const now = new Date();
  const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
  let currentIndex = dayOfYear % BLESSING_VERSES.length;

  function renderVerse(idx: number) {
    const verse = BLESSING_VERSES[idx];
    container!.innerHTML = `
      <div class="verse-banner" id="verse-banner-box">
        <div class="verse-glow-bar"></div>
        <div class="verse-main-content">
          <div class="verse-header-tag">
            <span class="verse-sparkle">✨</span>
            <span class="verse-focus-pill">${verse.focus}</span>
            <span class="verse-ref-tag">${verse.reference}</span>
          </div>
          <p class="verse-quote">«${verse.text}»</p>
        </div>
        <div class="verse-toolbar">
          <button id="btn-copy-verse" class="verse-icon-btn" title="Copiar versículo">
            📋
          </button>
          <button id="btn-next-verse" class="verse-icon-btn" title="Ver otro salmo">
            🔄
          </button>
          <button id="btn-dismiss-verse" class="verse-icon-btn close-btn" title="Cerrar">
            &times;
          </button>
        </div>
      </div>
    `;

    // Handler: Ver siguiente versículo
    document.getElementById('btn-next-verse')?.addEventListener('click', () => {
      currentIndex = (currentIndex + 1) % BLESSING_VERSES.length;
      const box = document.getElementById('verse-banner-box');
      if (box) {
        box.classList.add('verse-fade-out');
        setTimeout(() => {
          renderVerse(currentIndex);
        }, 150);
      } else {
        renderVerse(currentIndex);
      }
    });

    // Handler: Copiar versículo
    document.getElementById('btn-copy-verse')?.addEventListener('click', (e) => {
      const copyText = `«${verse.text}» — ${verse.reference}`;
      navigator.clipboard.writeText(copyText).then(() => {
        const btn = e.currentTarget as HTMLButtonElement;
        if (btn) {
          btn.innerHTML = '✅';
          setTimeout(() => { btn.innerHTML = '📋'; }, 1800);
        }
      });
    });

    // Handler: Cerrar / Ocultar banner
    document.getElementById('btn-dismiss-verse')?.addEventListener('click', () => {
      const banner = document.getElementById('verse-banner-box');
      if (banner) {
        banner.style.opacity = '0';
        banner.style.transform = 'translateY(-8px)';
        banner.style.transition = 'all 0.25s ease';
        sessionStorage.setItem('daily_verse_dismissed', 'true');
        setTimeout(() => {
          container!.innerHTML = '';
        }, 250);
      }
    });
  }

  renderVerse(currentIndex);
}
