"""
heuristica.py

Modulo compartido con toda la logica de deteccion heuristica de PhishGuard AI.
Lo importan tanto detector_es.py como detector_en.py, para no duplicar el
mismo codigo en dos sitios.

Nota: la heuristica de palabras clave esta pensada principalmente para
español (con un pequeño diccionario de respaldo en ingles), pero las
comprobaciones de dominios/URLs (homografos, marcas combinadas, suplantacion
de marca, SSO/AiTM) funcionan igual de bien en cualquier idioma, porque se
basan en la estructura del dominio, no en el idioma del texto.
"""
import re
import unicodedata


def normalizar(texto):
    """Pasa a minusculas y quita tildes/acentos, para que 'Accion' y 'accion'
    se comparen como iguales."""
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto


def normalizar_leetspeak(dominio):
    """Sustituye numeros usados para imitar letras (paypa1, amaz0n) de vuelta
    a su letra original, para comparar contra marcas reales."""
    sustituciones = {'0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '7': 't'}
    resultado = dominio
    for numero, letra in sustituciones.items():
        resultado = resultado.replace(numero, letra)
    return resultado


PATRON_DOMINIO = r'([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9][-a-zA-Z0-9.]*(?:/[^\s]*)?)'


def detectar_homografo(texto):
    patron_sospechoso = r'\b[a-z]+-?[a-z]*[A-Z][a-z]+-?[a-z]*\.(com|net|org|es|xyz|info)\b'
    return bool(re.search(patron_sospechoso, texto))


def detectar_secuestro_hilo(texto):
    texto_min = normalizar(texto)
    marcas_hilo = [
        "volver a escribirte", "el mes pasado", "revisando la contabilidad",
        "texto original del correo", "re: re:", "correo real que",
        "la semana pasada", "como hablamos", "retomando el tema"
    ]
    return sum(1 for m in marcas_hilo if m in texto_min)


def detectar_fraude_familiar(texto):
    texto_min = normalizar(texto)
    marcas_identidad = ["soy yo", "cambie de numero", "nuevo numero",
                         "numero nuevo", "numero prestado", "se me rompio el movil",
                         "perdi el movil", "perdi el telefono", "me robaron el telefono",
                         "tuve un accidente", "no puedo hablar ahora", "no puedo llamar"]
    marcas_dinero = ["transferencia", "bizum", "ingresa", "envia dinero",
                      "enviame dinero", "necesito dinero", "prestame",
                      "hazme un ingreso", "euros", "pago", "dinero", "ingreso"]
    tiene_identidad = any(m in texto_min for m in marcas_identidad)
    tiene_dinero = any(m in texto_min for m in marcas_dinero)
    return tiene_identidad and tiene_dinero


def detectar_homografo_numerico(texto):
    marcas = ["paypal", "google", "microsoft", "netflix", "amazon", "bbva",
              "santander", "correos", "dropbox", "onedrive", "outlook", "visa"]
    patron_dominio = r'([a-z0-9][-a-z0-9]*\.[a-z0-9][-a-z0-9.]*)'
    dominios = re.findall(patron_dominio, texto)
    for dominio in dominios:
        normalizado = normalizar_leetspeak(dominio)
        for marca in marcas:
            if marca in normalizado and marca not in dominio:
                return True, dominio, marca
    return False, None, None


def detectar_phishing_sso(texto):
    """Detecta el patron de ataque AiTM (Adversary-in-the-Middle): un mensaje
    pidiendo 're-autenticar' el acceso SSO/MFA por un enlace externo que no
    pertenece a ningun proveedor de identidad conocido."""
    texto_min = normalizar(texto)
    terminos_sso = [
        "sso", "single sign-on", "acceso unico", "reautenticar",
        "reautenticacion", "proveedor de identidad", "identity provider",
        "doble factor", "autenticacion de dos factores", "codigo de verificacion",
        "codigo mfa", "inicio de sesion unico", "re-authenticate", "two-factor",
        "verification code"
    ]
    proveedores_identidad_conocidos = [
        "microsoftonline.com", "okta.com", "onelogin.com",
        "pingidentity.com", "auth0.com", "accounts.google.com",
        "login.microsoft.com", "adfs"
    ]

    menciona_sso = any(t in texto_min for t in terminos_sso)
    if not menciona_sso:
        return False, None

    patron_dominio = r'([a-z0-9][-a-z0-9]*\.[a-z0-9][-a-z0-9.]*)'
    dominios = re.findall(patron_dominio, texto_min)
    for dominio in dominios:
        if not any(proveedor in dominio for proveedor in proveedores_identidad_conocidos):
            return True, dominio
    return False, None


def detectar_marca_multiple_en_dominio(texto):
    marcas_conocidas = [
        "google", "sharepoint", "microsoft", "onedrive", "dropbox",
        "netflix", "paypal", "visa", "amazon", "bbva", "santander",
        "correos", "factorial", "outlook", "office365", "workspace"
    ]
    patron_dominio = r'([a-z0-9][-a-z0-9]*\.[a-z0-9][-a-z0-9.]*)'
    dominios = re.findall(patron_dominio, texto)
    for dominio in dominios:
        marcas_en_este_dominio = [m for m in marcas_conocidas if m in dominio]
        if len(marcas_en_este_dominio) >= 2:
            return True, dominio, marcas_en_este_dominio
    return False, None, []


MARCAS_DOMINIOS_OFICIALES = {
    "seur": ["seur.com"],
    "correos": ["correos.es"],
    "correos express": ["correosexpress.com"],
    "dhl": ["dhl.com", "dhl.es"],
    "ups": ["ups.com"],
    "fedex": ["fedex.com"],
    "mrw": ["mrw.es"],
    "gls": ["gls-group.com", "gls-spain.es"],
    "bbva": ["bbva.es"],
    "santander": ["bancosantander.es", "santander.es"],
    "caixabank": ["caixabank.es"],
    "paypal": ["paypal.com"],
    "netflix": ["netflix.com"],
    "amazon": ["amazon.es", "amazon.com"],
    "microsoft": ["microsoft.com"],
    "google": ["google.com"],
    "hacienda": ["agenciatributaria.es", "agenciatributaria.gob.es"],
    "seguridad social": ["seg-social.es"],
}


def detectar_suplantacion_marca_dominio(texto):
    patron_dominio = r'([a-z0-9][-a-z0-9]*\.[a-z0-9][-a-z0-9.]*)'
    dominios_en_texto = re.findall(patron_dominio, texto)

    for marca, dominios_oficiales in MARCAS_DOMINIOS_OFICIALES.items():
        if marca not in texto:
            continue
        marca_compacta = marca.replace(" ", "")
        for dominio in dominios_en_texto:
            if marca_compacta in dominio.replace("-", ""):
                es_oficial = any(oficial in dominio for oficial in dominios_oficiales)
                if not es_oficial:
                    return True, marca, dominio
    return False, None, None


def detectar_fraude_proveedor_bec(texto):
    """Detecta el patron de Business Email Compromise (BEC) mas costoso a
    nivel mundial: un 'proveedor' o contacto habitual pide cambiar la cuenta
    bancaria de destino para el proximo pago/factura. No tiene enlaces ni
    urgencia agresiva, por eso es tan dificil de cazar - la señal real es
    la combinacion de 'cambio de cuenta' + 'pago/factura'."""
    texto_min = normalizar(texto)
    marcas_cambio_cuenta = [
        "cambio de cuenta bancaria", "actualizado nuestra cuenta bancaria",
        "nueva cuenta bancaria", "cuenta bancaria actualizada",
        "modificado nuestros datos bancarios", "cambio de datos bancarios",
        "coordenadas bancarias actualizadas", "nueva cuenta para la recepcion",
        "hemos cambiado de banco", "actualizacion de nuestra cuenta"
    ]
    marcas_pago = ["factura", "pago", "transferencia", "abono", "proximo pago", "proxima factura"]

    tiene_cambio = any(m in texto_min for m in marcas_cambio_cuenta)
    tiene_pago = any(m in texto_min for m in marcas_pago)
    return tiene_cambio and tiene_pago


def detectar_fraude_ceo_secreto(texto):
    """Detecta el fraude del CEO (vishing/BEC ejecutivo): alguien que se
    presenta con autoridad, pide guardar el secreto, y solicita un pago.
    Ninguna gestion legitima de empresa pide ocultar una transferencia a
    los compañeros - esa combinacion es la señal real, no la urgencia."""
    texto_min = normalizar(texto)
    marcas_autoridad = ["director general", "el ceo", "la directora", "el director",
                         "la gerente", "el gerente", "presidente de la empresa"]
    marcas_secreto = ["confidencial", "no lo hemos comunicado", "no se lo digas",
                       "no comuniques", "mantenlo en secreto", "no lo comentes",
                       "aun no lo sabe el resto", "no digas nada todavia"]
    marcas_pago = ["pago", "transferencia", "euros", "proveedor", "factura"]

    tiene_autoridad = any(m in texto_min for m in marcas_autoridad)
    tiene_secreto = any(m in texto_min for m in marcas_secreto)
    tiene_pago = any(m in texto_min for m in marcas_pago)
    return tiene_autoridad and tiene_secreto and tiene_pago


def inspeccion_seguridad_avanzada(texto):
    puntos_sospecha = 0
    razones = []
    texto_minusculas = normalizar(texto)

    patrones_qr = ["codigo qr", "escanee", "qr adjunto", "camara de su dispositivo",
                   "![codigo qr", "[codigo qr", "scan the qr", "qr code attached"]
    if any(p in texto_minusculas for p in patrones_qr):
        puntos_sospecha += 55
        razones.append("ALERTA CRITICA: Solicitud de escaneo de CODIGO QR. Tecnica avanzada para evadir cortafuegos.")

    patron_url = r'([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9][-a-zA-Z0-9.]*)'
    enlaces_reales = re.findall(patron_url, texto_minusculas)
    enlaces_simulados = "[" in texto_minusculas and "]" in texto_minusculas

    if enlaces_reales or enlaces_simulados:
        puntos_sospecha += 20
        razones.append("Deteccion de hipervinculos o accesos externos en el mensaje.")

        nubes_servicios = ["onedrive", "sharepoint", "dropbox", "google drive", "google workspace", "microsoft", "factorial", "workspace"]
        if any(marca in texto_minusculas for marca in nubes_servicios):
            excusas_red = [
                "plataforma interna no me dejaba", "enlace de nuestra carpeta",
                "servidor externo", "acceso temporal", "enlace de acceso",
                "carpeta compartida actualizada", "actualizar permisos",
                "actualizacion de la politica", "sincronizacion", "modo de solo lectura",
                "revision automatica de compatibilidad"
            ]
            if any(excusa in texto_minusculas for excusa in excusas_red):
                puntos_sospecha += 45
                razones.append("ALERTA DE INGENIERIA SOCIAL: Intento de suplantacion de nube/software corporativo usando fallos de red/proceso o cambios de politica como pretexto.")

    tiene_marca_multiple, dominio_sospechoso, marcas_encontradas = detectar_marca_multiple_en_dominio(texto_minusculas)
    if tiene_marca_multiple:
        puntos_sospecha += 55
        razones.append(f"ALERTA CRITICA: El dominio '{dominio_sospechoso}' combina varias marcas/servicios distintos ({marcas_encontradas}), algo que ninguna empresa legitima hace nunca.")

    tiene_phishing_sso, dominio_sso = detectar_phishing_sso(texto_minusculas)
    if tiene_phishing_sso:
        puntos_sospecha += 60
        razones.append(f"ALERTA CRITICA: Solicitud de reautenticacion SSO/MFA hacia un dominio ('{dominio_sso}') que no pertenece a ningun proveedor de identidad conocido. Patron de ataque AiTM (intercepta el codigo de doble factor en tiempo real).")

    diccionario_urgencia = [
        "urgente", "inmediatamente", "obligatoria", "bloqueada", "expirara",
        "retencion maxima", "accion requerida", "antes de manana",
        "proceder con la firma", "cerrar esto hoy mismo", "hoy mismo",
        "solo lectura", "antes del", "cumplimiento de la nueva normativa",
        "congratulations", "click here", "claim your prize", "gift card",
        "before it expires", "verify your account", "action required",
        "your account has been", "act now", "limited time"
    ]
    urgencias_detectadas = [p for p in diccionario_urgencia if p in texto_minusculas]

    if len(urgencias_detectadas) >= 4:
        puntos_sospecha += 45
        razones.append(f"Factores de coercion psicologica MUY numerosos detectados: {urgencias_detectadas}")
    elif len(urgencias_detectadas) >= 2:
        puntos_sospecha += 35
        razones.append(f"Factores de coercion psicologica multiple detectados: {urgencias_detectadas}")
    elif len(urgencias_detectadas) == 1:
        puntos_sospecha += 8
        razones.append(f"Uso de alertas temporales o requerimientos: {urgencias_detectadas}")

    tiene_homog_num, dominio_num, marca_num = detectar_homografo_numerico(texto_minusculas)
    if tiene_homog_num:
        puntos_sospecha += 50
        razones.append(f"ALERTA CRITICA: El dominio '{dominio_num}' imita a '{marca_num}' sustituyendo letras por numeros parecidos.")

    tiene_suplantacion, marca_susp, dominio_susp = detectar_suplantacion_marca_dominio(texto_minusculas)
    if tiene_suplantacion:
        puntos_sospecha += 55
        razones.append(f"ALERTA CRITICA: Se menciona la marca '{marca_susp}' pero el dominio '{dominio_susp}' no coincide con ninguno de sus dominios oficiales conocidos.")

    if detectar_fraude_familiar(texto):
        puntos_sospecha += 60
        razones.append("ALERTA CRITICA: Patron de estafa de suplantacion familiar (aviso de cambio de numero + peticion de dinero urgente). Ataque muy comun por WhatsApp, sin necesidad de enlaces.")

    if detectar_fraude_proveedor_bec(texto):
        puntos_sospecha += 60
        razones.append("ALERTA CRITICA: Patron de fraude de proveedor (BEC): solicitud de cambio de cuenta bancaria para un pago/factura. Fraude empresarial de alto coste, sin necesidad de enlaces ni urgencia.")

    if detectar_fraude_ceo_secreto(texto):
        puntos_sospecha += 55
        razones.append("ALERTA CRITICA: Patron de fraude del CEO: autoridad + peticion de secretismo + solicitud de pago. Ninguna gestion legitima pide ocultar una transferencia a los compañeros.")

    if detectar_homografo(texto):
        puntos_sospecha += 40
        razones.append("ALERTA: Posible dominio homografo (letras que imitan visualmente el dominio real, ej. 'I' mayuscula por 'l').")

    marcas_hilo = detectar_secuestro_hilo(texto)
    if marcas_hilo >= 2:
        puntos_sospecha += 35
        razones.append("ALERTA: Patron de secuestro de hilo de correo (referencia a conversacion previa + peticion de accion sobre un archivo/enlace).")
    elif marcas_hilo == 1:
        puntos_sospecha += 10
        razones.append("Mencion de una conversacion o gestion previa (revisar contexto real).")

    return puntos_sospecha, razones 

