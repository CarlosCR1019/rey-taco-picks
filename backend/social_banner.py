import os
import sys
import json
import time
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

def generar_banner_redes(picks=None, output_path="banner_hoy.png"):
    """
    Genera un banner gráfico profesional de 1080x1080 px para Instagram / Facebook
    con los 3 mejores picks del día de Rey Taco Picks.
    """
    if not picks:
        # Cargar de picks.json o Supabase
        json_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "picks.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                picks = json.load(f)
        else:
            picks = []

    # Filtrar 3 picks individuales principales
    free_picks = [p for p in picks if not p.get('es_parlay')][:3]
    if not free_picks:
        free_picks = [
            {"categoria": "Liga MX", "partido": "Tigres UANL vs Atlante FC", "pick": "Más de 2.5 Goles Totales", "cuota": "1.67", "confianza": "92%"},
            {"categoria": "Liga MX", "partido": "Juarez vs America", "pick": "Más de 2.5 Goles Totales", "cuota": "1.74", "confianza": "90%"},
            {"categoria": "MLB", "partido": "WAS Nationals vs TEX Rangers", "pick": "Más de 7.5 Carreras Totales", "cuota": "1.95", "confianza": "91%"}
        ]

    # Dimensiones
    width = 1080
    height = 1080
    img = Image.new("RGB", (width, height), color="#080c14")
    draw = ImageDraw.Draw(img)

    # Intentar cargar fuentes del sistema o usar default
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 52)
        font_subtitle = ImageFont.truetype("arialbd.ttf", 34)
        font_card_title = ImageFont.truetype("arialbd.ttf", 32)
        font_card_pick = ImageFont.truetype("arialbd.ttf", 38)
        font_card_meta = ImageFont.truetype("arial.ttf", 26)
        font_footer = ImageFont.truetype("arialbd.ttf", 28)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_card_title = font_title
        font_card_pick = font_title
        font_card_meta = font_title
        font_footer = font_title

    # 1. Fondo degradado sutil
    for y in range(height):
        r = int(8 + (15 - 8) * (y / height))
        g = int(12 + (24 - 12) * (y / height))
        b = int(20 + (39 - 20) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Marco Dorado Exterior
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#D4AF37", width=3)
    draw.rectangle([(26, 26), (width - 26, height - 26)], outline="#AA8C2C", width=1)

    # 3. Header
    draw.text((width // 2, 70), "🌮👑 REY TACO PICKS 👑🌮", fill="#D4AF37", font=font_title, anchor="mt")
    fecha_str = time.strftime('%d de Agosto, %Y • CDMX')
    draw.text((width // 2, 135), f"PRONÓSTICOS DEPORTIVOS IA • {fecha_str.upper()}", fill="#94A3B8", font=font_subtitle, anchor="mt")

    # 4. Tarjetas de los 3 Picks
    start_y = 200
    card_height = 230
    card_margin = 25
    card_width = width - 120
    card_x = 60

    for i, p in enumerate(free_picks):
        cy = start_y + (i * (card_height + card_margin))
        
        # Fondo de Tarjeta
        draw.rounded_rectangle([(card_x, cy), (card_x + card_width, cy + card_height)], radius=18, fill="#111827", outline="#1E293B", width=2)
        
        # Acento lateral rojo/carmesí
        draw.rounded_rectangle([(card_x, cy), (card_x + 12, cy + card_height)], radius=6, fill="#EF4444")

        # Categoría Tag
        cat = p.get('categoria', 'Deportes').upper()
        draw.text((card_x + 35, cy + 25), f"⚽ [{cat}]", fill="#38BDF8", font=font_card_meta)
        
        # Nivel de Confianza Tag (Derecha)
        conf = p.get('confianza', '90%')
        draw.text((card_x + card_width - 35, cy + 25), f"🔥 {conf} Confianza", fill="#22C55E", font=font_card_meta, anchor="ra")

        # Partido
        partido = p.get('partido', 'Partido Destacado')
        draw.text((card_x + 35, cy + 68), partido, fill="#FFFFFF", font=font_card_title)

        # Selección / Pick (Dorado Brillante)
        pick_text = p.get('pick', 'Más de 2.5 Goles')
        draw.text((card_x + 35, cy + 120), f"🎯 {pick_text}", fill="#D4AF37", font=font_card_pick)

        # Cuota y Horario
        cuota = p.get('cuota', '1.75')
        horario = p.get('horario', 'Hoy')
        draw.text((card_x + 35, cy + 175), f"📊 Momio: {cuota}  |  🕒 {horario}  |  💎 Valor Estadístico +EV", fill="#94A3B8", font=font_card_meta)

    # 5. Footer & Call To Action
    footer_y = height - 90
    draw.rectangle([(30, footer_y - 25), (width - 30, height - 30)], fill="#0F172A", outline="#D4AF37", width=1)
    draw.text((width // 2, footer_y - 12), "🌐 DESBLOQUEA PARLAYS IA Y ANÁLISIS EN: reytacopicks.com", fill="#D4AF37", font=font_footer, anchor="mt")

    # Guardar
    img.save(output_path, "PNG", quality=95)
    print(f"🎉 Banner gráfico generado exitosamente: {output_path} ({width}x{height} px)")
    return output_path

if __name__ == "__main__":
    generar_banner_redes()
