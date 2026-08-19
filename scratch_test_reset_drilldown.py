import undetected_chromedriver as uc
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

from backend.scraper import get_shadow_script, extract_events_from_page

options = uc.ChromeOptions()
options.add_argument("--window-size=1600,1000")
driver = uc.Chrome(options=options, version_main=151)

try:
    driver.get("https://www.playdoit.mx/es/")
    time.sleep(8)
    
    def click_sports_home():
        s = get_shadow_script() + """
        var shadow = getShadow();
        if(!shadow) return false;
        var all = Array.from(shadow.querySelectorAll('*'));
        var dep = all.find(n => (n.textContent||'').trim().toLowerCase() === 'deportes' && n.children.length === 0);
        if (dep) { (dep.parentElement || dep).click(); return true; }
        return false;
        """
        driver.execute_script(s)
        time.sleep(2)
        
    # 1. Champions League
    s_champ = get_shadow_script() + """
    var shadow = getShadow();
    if(!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var champ = all.find(n => n.children.length === 0 && (n.textContent||'').trim().toLowerCase() === 'uefa champions league');
    if (champ) { (champ.parentElement || champ).click(); champ.click(); return true; }
    return false;
    """
    print("Click Champions:", driver.execute_script(s_champ))
    time.sleep(4)
    evts_c = extract_events_from_page(driver)
    print(f"Champions matches: {len(evts_c)}")
    for e in evts_c:
        print("  🇪🇺", e.get('local'), "vs", e.get('visitante'), e.get('cuotas'))
        
    # 2. Reset back to Deportes
    click_sports_home()
    
    # 3. KBO
    s_beis = get_shadow_script() + """
    var shadow = getShadow();
    if(!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var beis = all.find(n => n.children.length === 0 && (n.textContent||'').trim().toLowerCase() === 'béisbol');
    if (beis) { (beis.parentElement || beis).click(); return true; }
    return false;
    """
    print("Click Beisbol:", driver.execute_script(s_beis))
    time.sleep(2)
    
    s_corea = get_shadow_script() + """
    var shadow = getShadow();
    if(!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var corea = all.find(n => n.children.length === 0 && ((n.textContent||'').trim().toLowerCase() === 'corea del sur' || (n.textContent||'').trim().toLowerCase() === 'kbo'));
    if (corea) { (corea.parentElement || corea).click(); return true; }
    return false;
    """
    print("Click Corea:", driver.execute_script(s_corea))
    time.sleep(2)
    
    s_kbo = get_shadow_script() + """
    var shadow = getShadow();
    if(!shadow) return false;
    var all = Array.from(shadow.querySelectorAll('*'));
    var kbo = all.find(n => n.children.length === 0 && ((n.textContent||'').trim().toLowerCase() === 'kbo' || (n.textContent||'').trim().toLowerCase() === 'kbo league'));
    if (kbo) { (kbo.parentElement || kbo).click(); return true; }
    return false;
    """
    print("Click KBO:", driver.execute_script(s_kbo))
    time.sleep(3)
    evts_k = extract_events_from_page(driver)
    print(f"KBO matches: {len(evts_k)}")
    for e in evts_k:
        print("  🇰🇷", e.get('local'), "vs", e.get('visitante'), e.get('cuotas'))

finally:
    driver.quit()
