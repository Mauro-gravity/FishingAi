import os
import re
import pickle
from heuristica import inspeccion_seguridad_avanzada, PATRON_DOMINIO

# --- CARGAR MODELOS (generados por train_model.py) ---
print("Cargando modelos de IA pre-entrenados (version INGLES)...")

RUTAS_REQUERIDAS = [
    'modelo_texto.pkl', 'vectorizador_texto.pkl',
    'modelo_urls.pkl', 'vectorizador_urls.pkl',
]
faltantes = [r for r in RUTAS_REQUERIDAS if not os.path.exists(r)]
if faltantes:
    print(f"ERROR: Faltan estos archivos: {faltantes}")
    print("Ejecuta primero train_model.py para generarlos.")
    exit()

with open('modelo_texto.pkl', 'rb') as f:
    modelo_texto = pickle.load(f)
with open('vectorizador_texto.pkl', 'rb') as f:
    vectorizador_texto = pickle.load(f)
with open('modelo_urls.pkl', 'rb') as f:
    modelo_urls = pickle.load(f)
with open('vectorizador_urls.pkl', 'rb') as f:
    vectorizador_urls = pickle.load(f)

print("Modelos cargados y listos.\n")


def evaluar_con_ia(entrada_original):
    """Devuelve (porcentaje_ia_texto, porcentaje_ia_url_max)."""
    transformado_texto = vectorizador_texto.transform([entrada_original])
    proba_texto = modelo_texto.predict_proba(transformado_texto)[0]
    idx_spam_texto = list(modelo_texto.classes_).index('spam')
    porcentaje_texto = proba_texto[idx_spam_texto] * 100

    dominios = re.findall(PATRON_DOMINIO, entrada_original.lower())
    porcentaje_url_max = 0.0
    if dominios:
        transformado_urls = vectorizador_urls.transform(dominios)
        proba_urls = modelo_urls.predict_proba(transformado_urls)
        idx_spam_url = list(modelo_urls.classes_).index('spam')
        porcentaje_url_max = max(p[idx_spam_url] for p in proba_urls) * 100

    return porcentaje_texto, porcentaje_url_max


# --- CONSOLE INTERFACE ---
print("-" * 70)
print("PhishGuard AI - ENGLISH VERSION")
print("-" * 70)

while True:
    entrada_original = input("\nEnter the message to analyze (or type 'exit'): ")

    if entrada_original.strip().lower() in ('exit', 'salir'):
        print("Shutting down shields. Stay safe.")
        break

    if not entrada_original.strip():
        continue

    porcentaje_ia_texto, porcentaje_ia_url = evaluar_con_ia(entrada_original)
    porcentaje_ia_final = max(porcentaje_ia_texto, porcentaje_ia_url)

    # NOTA: la heuristica esta escrita principalmente en español (con un
    # diccionario de respaldo en ingles para palabras de urgencia comunes).
    # Las comprobaciones de dominios/marcas funcionan igual en cualquier
    # idioma porque se basan en la estructura de la URL, no en el idioma.
    puntos_heuristica, alertas = inspeccion_seguridad_avanzada(entrada_original)

    probabilidad_final = (porcentaje_ia_final * 0.15) + (puntos_heuristica * 0.85)
    if probabilidad_final > 100:
        probabilidad_final = 100.0

    print("\n--- SECURITY TECHNICAL REPORT ---")
    print(f"   [DEBUG] AI text: {porcentaje_ia_texto:.2f}% | AI url: {porcentaje_ia_url:.2f}% | Heuristic points: {puntos_heuristica}")
    if probabilidad_final >= 50:
        print(f"VERDICT: THREAT CONFIRMED / FRAUD DETECTED ({probabilidad_final:.2f}%)")
        print("   Evidence found in the inspection modules:")
        for alerta in alertas:
            print(f"   -> {alerta}")
    else:
        print(f"VERDICT: TRUSTWORTHY MESSAGE ({100 - probabilidad_final:.2f}% confidence)")
        if alertas:
            print("   Note: minor signals detected, though not enough to flag as a threat:")
            for alerta in alertas:
                print(f"   -> {alerta}")
        else:
            print("   Clean structure. No match with known fraud patterns.")
    print("-" * 45)