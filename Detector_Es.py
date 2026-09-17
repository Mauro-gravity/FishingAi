import os
import re
import pickle
from heuristica import inspeccion_seguridad_avanzada, PATRON_DOMINIO

# --- CARGAR MODELOS (generados por train_model.py) ---
print("Cargando modelos de IA pre-entrenados (version ESPAÑOL)...")

RUTAS_REQUERIDAS = [
    'modelo_texto_es.pkl', 'vectorizador_texto_es.pkl',
    'modelo_urls.pkl', 'vectorizador_urls.pkl',
]
faltantes = [r for r in RUTAS_REQUERIDAS if not os.path.exists(r)]
if faltantes:
    print(f"ERROR: Faltan estos archivos: {faltantes}")
    print("Ejecuta primero train_model.py para generarlos.")
    exit()

with open('modelo_texto_es.pkl', 'rb') as f:
    modelo_texto = pickle.load(f)
with open('vectorizador_texto_es.pkl', 'rb') as f:
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


# --- INTERFAZ DE CONSOLA ---
print("-" * 70)
print("PhishGuard AI - VERSION ESPAÑOL")
print("-" * 70)

while True:
    entrada_original = input("\nIntroduce el mensaje a analizar (o escribe 'salir'): ")

    if entrada_original.strip().lower() == 'salir':
        print("Desconectando escudos. Mantente seguro.")
        break

    if not entrada_original.strip():
        continue

    porcentaje_ia_texto, porcentaje_ia_url = evaluar_con_ia(entrada_original)
    porcentaje_ia_final = max(porcentaje_ia_texto, porcentaje_ia_url)

    puntos_heuristica, alertas = inspeccion_seguridad_avanzada(entrada_original)

    probabilidad_final = (porcentaje_ia_final * 0.15) + (puntos_heuristica * 0.85)
    if probabilidad_final > 100:
        probabilidad_final = 100.0

    print("\n--- INFORME TECNICO DE SEGURIDAD ---")
    print(f"   [DEBUG] IA texto: {porcentaje_ia_texto:.2f}% | IA url: {porcentaje_ia_url:.2f}% | Puntos heuristica: {puntos_heuristica}")
    if probabilidad_final >= 50:
        print(f"DICTAMEN: AMENAZA CONFIRMADA / FRAUDE DETECTADO ({probabilidad_final:.2f}%)")
        print("   Evidencias de ataque encontradas en los modulos de inspeccion:")
        for alerta in alertas:
            print(f"   -> {alerta}")
    else:
        print(f"DICTAMEN: MENSAJE CONFIABLE ({100 - probabilidad_final:.2f}% de seguridad)")
        if alertas:
            print("   Nota: se detectaron algunas señales menores, aunque no suficientes para marcarlo como amenaza:")
            for alerta in alertas:
                print(f"   -> {alerta}")
        else:
            print("   Estructura limpia. No hay coincidencia con patrones de fraude conocidos.")
    print("-" * 45)