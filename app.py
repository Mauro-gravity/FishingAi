import os
import re
import sys
import pickle
import time
import flet as ft

from heuristica import inspeccion_seguridad_avanzada, PATRON_DOMINIO


# ==============================================================
# RECURSOS Y COLORES
# ==============================================================

def ruta_recurso(ruta_relativa: str) -> str:
    """
    Devuelve una ruta válida tanto durante el desarrollo como dentro
    del ejecutable generado mediante PyInstaller/Flet Pack.
    """
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, ruta_relativa)


COLOR_FONDO = "#E7EBF2"
COLOR_SUPERFICIE = "#E7EBF2"
COLOR_SUPERFICIE_CLARA = "#F5F7FB"

COLOR_TEXTO = "#303744"
COLOR_TEXTO_SUAVE = "#7D8798"

COLOR_ACENTO = "#5C7CFA"
COLOR_ACENTO_OSCURO = "#4664D9"
COLOR_ACENTO_SUAVE = "#DCE4FF"

COLOR_PELIGRO = "#E4526B"
COLOR_PELIGRO_SUAVE = "#FCE3E8"

COLOR_SEGURO = "#2EAE7D"
COLOR_SEGURO_SUAVE = "#DDF5EB"

COLOR_ADVERTENCIA = "#F2A93B"
COLOR_ADVERTENCIA_SUAVE = "#FFF0D7"

COLOR_SOMBRA_OSCURA = "#C3C9D4"
COLOR_SOMBRA_CLARA = "#FFFFFF"


def sombra_exterior() -> list[ft.BoxShadow]:
    return [
        ft.BoxShadow(
            spread_radius=1,
            blur_radius=18,
            color=COLOR_SOMBRA_CLARA,
            offset=ft.Offset(-7, -7),
        ),
        ft.BoxShadow(
            spread_radius=1,
            blur_radius=18,
            color=COLOR_SOMBRA_OSCURA,
            offset=ft.Offset(7, 7),
        ),
    ]


def sombra_suave() -> list[ft.BoxShadow]:
    return [
        ft.BoxShadow(
            blur_radius=10,
            color="#FFFFFF",
            offset=ft.Offset(-4, -4),
        ),
        ft.BoxShadow(
            blur_radius=10,
            color="#C8CED9",
            offset=ft.Offset(4, 4),
        ),
    ]


# ==============================================================
# COMPONENTES VISUALES
# ==============================================================

def tarjeta_neumorfica(
    contenido: ft.Control,
    padding=20,
    radius=24,
    expand=False,
    **kwargs,
) -> ft.Container:
    return ft.Container(
        content=contenido,
        bgcolor=COLOR_SUPERFICIE,
        border_radius=radius,
        padding=padding,
        shadow=sombra_exterior(),
        expand=expand,
        **kwargs,
    )


def superficie_hundida(
    contenido: ft.Control,
    padding=14,
    radius=16,
    **kwargs,
) -> ft.Container:
    """
    Simula una superficie hundida. Flet no dispone de sombras internas
    nativas, por lo que se combinan borde, degradado y sombra suave.
    """
    return ft.Container(
        content=contenido,
        padding=padding,
        border_radius=radius,
        border=ft.Border.all(1, "#D5DAE3"),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#DDE1E8", "#F1F4F9"],
        ),
        shadow=[
            ft.BoxShadow(
                blur_radius=8,
                color="#BCC3CF",
                offset=ft.Offset(3, 3),
            ),
            ft.BoxShadow(
                blur_radius=7,
                color="#FFFFFF",
                offset=ft.Offset(-2, -2),
            ),
        ],
        **kwargs,
    )


def texto_neumorfico(
    valor: str,
    size=22,
    weight=ft.FontWeight.BOLD,
    color=COLOR_TEXTO,
) -> ft.Stack:
    estilo = {
        "size": size,
        "weight": weight,
        "font_family": "Arial",
    }

    return ft.Stack(
        controls=[
            ft.Container(
                content=ft.Text(
                    valor,
                    color=COLOR_SOMBRA_CLARA,
                    **estilo,
                ),
                left=-1,
                top=-1,
            ),
            ft.Container(
                content=ft.Text(
                    valor,
                    color=COLOR_SOMBRA_OSCURA,
                    **estilo,
                ),
                left=1,
                top=1,
            ),
            ft.Container(
                content=ft.Text(
                    valor,
                    color=color,
                    **estilo,
                )
            ),
        ]
    )


def insignia(
    texto: str,
    icono,
    color: str,
    fondo: str,
) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icono, size=15, color=color),
                ft.Text(
                    texto,
                    size=11,
                    weight=ft.FontWeight.W_600,
                    color=color,
                ),
            ],
            spacing=6,
            tight=True,
        ),
        bgcolor=fondo,
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=11, vertical=6),
    )


def boton_neumorfico(
    texto: str,
    icono,
    color=COLOR_ACENTO,
) -> ft.Container:
    boton = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(icono, size=19, color="#FFFFFF"),
                ft.Text(
                    texto,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color="#FFFFFF",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        bgcolor=color,
        color="#FFFFFF",
        elevation=0,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=16),
            overlay_color="#22FFFFFF",
            padding=ft.Padding.symmetric(horizontal=22),
        ),
        expand=True,
    )

    return ft.Container(
        content=boton,
        border_radius=16,
        shadow=[
            ft.BoxShadow(
                blur_radius=12,
                color="#AAB4D6",
                offset=ft.Offset(5, 5),
            ),
            ft.BoxShadow(
                blur_radius=10,
                color="#FFFFFF",
                offset=ft.Offset(-4, -4),
            ),
        ],
    )


# ==============================================================
# MODELOS
# ==============================================================

class ModeloManager:
    def __init__(self):
        self.modelos = {}
        self.listo = False
        self.error = None

    def cargar(self, callback_progreso=None):
        rutas = [
            ("modelo_texto_es", "modelo_texto_es.pkl"),
            ("vectorizador_texto_es", "vectorizador_texto_es.pkl"),
            ("modelo_texto_en", "modelo_texto.pkl"),
            ("vectorizador_texto_en", "vectorizador_texto.pkl"),
            ("modelo_urls", "modelo_urls.pkl"),
            ("vectorizador_urls", "vectorizador_urls.pkl"),
        ]

        rutas_resueltas = [
            (clave, ruta_recurso(archivo))
            for clave, archivo in rutas
        ]

        faltantes = [
            archivo
            for _, archivo in rutas_resueltas
            if not os.path.exists(archivo)
        ]

        if faltantes:
            nombres = [os.path.basename(archivo) for archivo in faltantes]
            self.error = f"Faltan archivos de modelo: {', '.join(nombres)}"
            return

        try:
            for indice, (clave, archivo) in enumerate(rutas_resueltas):
                with open(archivo, "rb") as fichero:
                    self.modelos[clave] = pickle.load(fichero)

                if callback_progreso:
                    callback_progreso(
                        (indice + 1) / len(rutas_resueltas)
                    )

            self.listo = True

        except Exception as error:
            self.error = f"No se pudieron cargar los modelos: {error}"

    def analizar(self, mensaje: str, idioma: str):
        if idioma == "es":
            modelo_texto = self.modelos["modelo_texto_es"]
            vectorizador_texto = self.modelos["vectorizador_texto_es"]
        else:
            modelo_texto = self.modelos["modelo_texto_en"]
            vectorizador_texto = self.modelos["vectorizador_texto_en"]

        transformado_texto = vectorizador_texto.transform([mensaje])
        probabilidades_texto = modelo_texto.predict_proba(
            transformado_texto
        )[0]

        indice_spam_texto = list(
            modelo_texto.classes_
        ).index("spam")

        porcentaje_texto = (
            probabilidades_texto[indice_spam_texto] * 100
        )

        dominios = re.findall(PATRON_DOMINIO, mensaje.lower())
        porcentaje_url_maximo = 0.0

        if dominios:
            modelo_urls = self.modelos["modelo_urls"]
            vectorizador_urls = self.modelos["vectorizador_urls"]

            transformado_urls = vectorizador_urls.transform(dominios)
            probabilidades_urls = modelo_urls.predict_proba(
                transformado_urls
            )

            indice_spam_url = list(
                modelo_urls.classes_
            ).index("spam")

            porcentaje_url_maximo = max(
                probabilidad[indice_spam_url]
                for probabilidad in probabilidades_urls
            ) * 100

        porcentaje_ia = max(
            porcentaje_texto,
            porcentaje_url_maximo,
        )

        puntos_heuristica, alertas = (
            inspeccion_seguridad_avanzada(mensaje)
        )

        probabilidad_final = (
            porcentaje_ia * 0.15
        ) + (
            puntos_heuristica * 0.85
        )

        return min(probabilidad_final, 100.0), alertas


# ==============================================================
# APLICACIÓN
# ==============================================================

def main(page: ft.Page):
    page.title = "PhishGuard AI"
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    page.spacing = 0

    page.window.width = 920
    page.window.height = 760
    page.window.min_width = 520
    page.window.min_height = 560

    icono_ventana = ruta_recurso("assets/icon.ico")
    if os.path.exists(icono_ventana):
        page.window.icon = icono_ventana

    estado = {
        "idioma": "es",
        "animacion_contador": 0,
    }

    gestor = ModeloManager()

    textos = {
        "es": {
            "subtitulo": "Análisis inteligente de mensajes y enlaces",
            "entrada_titulo": "Mensaje para analizar",
            "entrada_descripcion":
                "Pega un correo, SMS o mensaje sospechoso.",
            "placeholder":
                "Pega aquí el mensaje, email o SMS a analizar...",
            "analizar": "Analizar mensaje",
            "analizando": "Analizando...",
            "resultado_titulo": "Resultado del análisis",
            "resultado_vacio": "Aún no se ha realizado ningún análisis",
            "resultado_vacio_sub":
                "El nivel de riesgo y las alertas aparecerán aquí.",
            "amenaza": "AMENAZA DETECTADA",
            "confiable": "MENSAJE CONFIABLE",
            "riesgo": "probabilidad de fraude",
            "confianza": "confianza de seguridad",
            "sin_alertas":
                "No se detectaron patrones de fraude conocidos.",
            "alertas": "Indicadores detectados",
            "cargando": "Cargando motores de inteligencia...",
            "listo": "Protección activa",
            "vacio": "Introduce un mensaje antes de analizarlo.",
            "error_analisis": "No se pudo completar el análisis.",
        },
        "en": {
            "subtitulo": "Intelligent message and link analysis",
            "entrada_titulo": "Message to analyze",
            "entrada_descripcion":
                "Paste a suspicious email, SMS, or message.",
            "placeholder":
                "Paste your message, email, or SMS to analyze here...",
            "analizar": "Analyze message",
            "analizando": "Analyzing...",
            "resultado_titulo": "Analysis result",
            "resultado_vacio": "No analysis has been performed yet",
            "resultado_vacio_sub":
                "The risk level and alerts will appear here.",
            "amenaza": "THREAT DETECTED",
            "confiable": "TRUSTWORTHY MESSAGE",
            "riesgo": "fraud probability",
            "confianza": "safety confidence",
            "sin_alertas":
                "No known fraud patterns were detected.",
            "alertas": "Detected indicators",
            "cargando": "Loading intelligence engines...",
            "listo": "Protection active",
            "vacio": "Enter a message before analyzing it.",
            "error_analisis": "The analysis could not be completed.",
        },
    }

    def t(clave: str) -> str:
        return textos[estado["idioma"]][clave]

    # ==========================================================
    # SPLASH SCREEN
    # ==========================================================

    ruta_logo = ruta_recurso("assets/icon.png")

    if os.path.exists(ruta_logo):
        logo_carga = ft.Image(
            src=ruta_logo,
            width=82,
            height=82,
            fit="contain",

        )
    else:
        logo_carga = ft.Icon(
            ft.Icons.SHIELD_ROUNDED,
            size=64,
            color=COLOR_ACENTO,
        )

    contenedor_logo_carga = ft.Container(
        content=logo_carga,
        width=120,
        height=120,
        alignment=ft.Alignment.CENTER,
        bgcolor=COLOR_SUPERFICIE,
        border_radius=36,
        shadow=sombra_exterior(),
        animate_scale=ft.Animation(
            850,
            ft.AnimationCurve.EASE_IN_OUT,
        ),
        scale=1,
    )

    barra_progreso = ft.ProgressBar(
        value=0,
        color=COLOR_ACENTO,
        bgcolor="#D4D9E3",
        height=7,
        border_radius=10,
    )

    porcentaje_carga = ft.Text(
        "0%",
        size=12,
        color=COLOR_TEXTO_SUAVE,
        weight=ft.FontWeight.W_600,
    )

    texto_carga = ft.Text(
        t("cargando"),
        size=13,
        color=COLOR_TEXTO_SUAVE,
        text_align=ft.TextAlign.CENTER,
    )

    vista_carga = ft.Container(
        content=ft.Column(
            controls=[
                contenedor_logo_carga,
                ft.Container(height=13),
                texto_neumorfico("PhishGuard AI", size=29),
                ft.Text(
                    "Smart protection",
                    size=12,
                    color=COLOR_TEXTO_SUAVE,
                ),
                ft.Container(height=25),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "AI ENGINE",
                                        size=10,
                                        color=COLOR_TEXTO_SUAVE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    porcentaje_carga,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            barra_progreso,
                        ],
                        spacing=9,
                    ),
                    width=310,
                ),
                ft.Container(height=10),
                texto_carga,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=COLOR_FONDO,
        opacity=1,
        animate_opacity=ft.Animation(
            450,
            ft.AnimationCurve.EASE_OUT,
        ),
    )

    # ==========================================================
    # CABECERA
    # ==========================================================

    icono_cabecera = ft.Container(
        content=ft.Icon(
            ft.Icons.SHIELD_ROUNDED,
            color=COLOR_ACENTO,
            size=28,
        ),
        width=52,
        height=52,
        alignment=ft.Alignment.CENTER,
        border_radius=17,
        bgcolor=COLOR_SUPERFICIE,
        shadow=sombra_suave(),
    )

    titulo_principal = texto_neumorfico(
        "PhishGuard AI",
        size=24,
    )

    subtitulo_principal = ft.Text(
        t("subtitulo"),
        size=12,
        color=COLOR_TEXTO_SUAVE,
    )

    selector_idioma = ft.CupertinoSlidingSegmentedButton(
        selected_index=0,
        thumb_color=COLOR_ACENTO,
        bgcolor="#D8DDE6",
        padding=ft.Padding.all(4),
        controls=[
            ft.Container(
                content=ft.Text(
                    "ES",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                ),
                padding=ft.Padding.symmetric(
                    horizontal=13,
                    vertical=7,
                ),
            ),
            ft.Container(
                content=ft.Text(
                    "EN",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                ),
                padding=ft.Padding.symmetric(
                    horizontal=13,
                    vertical=7,
                ),
            ),
        ],
    )

    indicador_estado = insignia(
        t("listo"),
        ft.Icons.CHECK_CIRCLE_ROUNDED,
        COLOR_SEGURO,
        COLOR_SEGURO_SUAVE,
    )

    cabecera = ft.Row(
        controls=[
            ft.Row(
                controls=[
                    icono_cabecera,
                    ft.Column(
                        controls=[
                            titulo_principal,
                            subtitulo_principal,
                        ],
                        spacing=2,
                    ),
                ],
                spacing=15,
            ),
            ft.Row(
                controls=[
                    indicador_estado,
                    selector_idioma,
                ],
                spacing=12,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ==========================================================
    # TARJETA DE ENTRADA
    # ==========================================================

    entrada_titulo = ft.Text(
        t("entrada_titulo"),
        size=16,
        weight=ft.FontWeight.BOLD,
        color=COLOR_TEXTO,
    )

    entrada_descripcion = ft.Text(
        t("entrada_descripcion"),
        size=12,
        color=COLOR_TEXTO_SUAVE,
    )

    contador_caracteres = ft.Text(
        "0 caracteres",
        size=11,
        color=COLOR_TEXTO_SUAVE,
    )

    caja_texto = ft.TextField(
        hint_text=t("placeholder"),
        multiline=True,
        min_lines=7,
        max_lines=9,
        border=ft.InputBorder.NONE,
        bgcolor="transparent",
        color=COLOR_TEXTO,
        cursor_color=COLOR_ACENTO,
        text_size=14,
        content_padding=ft.Padding.all(4),
        expand=True,
    )

    envoltura_caja = superficie_hundida(
        contenido=caja_texto,
        padding=16,
        radius=18,
    )

    boton_analizar = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.SECURITY_ROUNDED,
                    size=19,
                    color="#FFFFFF",
                ),
                ft.Text(
                    t("analizar"),
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        bgcolor=COLOR_ACENTO,
        elevation=0,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=16),
            overlay_color="#22FFFFFF",
        ),
        expand=True,
        animate_scale=ft.Animation(
            140,
            ft.AnimationCurve.EASE_OUT,
        ),
    )

    contenedor_boton = ft.Container(
        content=boton_analizar,
        border_radius=16,
        shadow=[
            ft.BoxShadow(
                blur_radius=12,
                color="#AEB8D6",
                offset=ft.Offset(5, 5),
            ),
            ft.BoxShadow(
                blur_radius=10,
                color="#FFFFFF",
                offset=ft.Offset(-4, -4),
            ),
        ],
    )

    tarjeta_entrada = tarjeta_neumorfica(
        ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.MAIL_OUTLINE_ROUNDED,
                                        color=COLOR_ACENTO,
                                        size=20,
                                    ),
                                    width=38,
                                    height=38,
                                    alignment=ft.Alignment.CENTER,
                                    bgcolor=COLOR_ACENTO_SUAVE,
                                    border_radius=12,
                                ),
                                ft.Column(
                                    controls=[
                                        entrada_titulo,
                                        entrada_descripcion,
                                    ],
                                    spacing=1,
                                ),
                            ],
                            spacing=11,
                        ),
                        contador_caracteres,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                envoltura_caja,
                contenedor_boton,
            ],
            spacing=16,
            expand=True,
        ),
        expand=True,
    )

    # ==========================================================
    # TARJETA DE RESULTADOS
    # ==========================================================

    resultado_titulo = ft.Text(
        t("resultado_titulo"),
        size=16,
        weight=ft.FontWeight.BOLD,
        color=COLOR_TEXTO,
    )

    icono_resultado = ft.Icon(
        ft.Icons.SHIELD_OUTLINED,
        size=38,
        color=COLOR_TEXTO_SUAVE,
    )

    circulo_progreso = ft.ProgressRing(
        value=0,
        width=126,
        height=126,
        stroke_width=9,
        color=COLOR_ACENTO,
        bgcolor="#D2D7E0",
    )

    porcentaje_central = ft.Text(
        "--",
        size=25,
        weight=ft.FontWeight.BOLD,
        color=COLOR_TEXTO,
    )

    medidor_riesgo = ft.Stack(
        controls=[
            circulo_progreso,
            ft.Container(
                content=ft.Column(
                    controls=[
                        icono_resultado,
                        porcentaje_central,
                    ],
                    spacing=1,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=126,
                height=126,
                alignment=ft.Alignment.CENTER,
            ),
        ],
        width=126,
        height=126,
    )

    veredicto = ft.Text(
        t("resultado_vacio"),
        size=16,
        weight=ft.FontWeight.BOLD,
        color=COLOR_TEXTO,
        text_align=ft.TextAlign.CENTER,
    )

    detalle_porcentaje = ft.Text(
        t("resultado_vacio_sub"),
        size=12,
        color=COLOR_TEXTO_SUAVE,
        text_align=ft.TextAlign.CENTER,
    )

    encabezado_alertas = ft.Row(
        controls=[
            ft.Icon(
                ft.Icons.FACT_CHECK_OUTLINED,
                size=17,
                color=COLOR_TEXTO_SUAVE,
            ),
            ft.Text(
                t("alertas"),
                size=12,
                color=COLOR_TEXTO_SUAVE,
                weight=ft.FontWeight.W_600,
            ),
        ],
        spacing=7,
    )

    lista_alertas = ft.Column(
        controls=[
            ft.Container(
                content=ft.Text(
                    t("sin_alertas"),
                    size=12,
                    color=COLOR_TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.Alignment.CENTER,
                padding=12,
            )
        ],
        spacing=9,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    panel_alertas = superficie_hundida(
        contenido=ft.Column(
            controls=[
                encabezado_alertas,
                ft.Divider(
                    height=1,
                    color="#CDD2DC",
                ),
                lista_alertas,
            ],
            spacing=10,
            expand=True,
        ),
        padding=14,
        radius=17,
        expand=True,
    )

    tarjeta_resultado = tarjeta_neumorfica(
        ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.ANALYTICS_OUTLINED,
                                color=COLOR_ACENTO,
                                size=20,
                            ),
                            width=38,
                            height=38,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=COLOR_ACENTO_SUAVE,
                            border_radius=12,
                        ),
                        resultado_titulo,
                    ],
                    spacing=11,
                ),
                ft.Container(
                    content=medidor_riesgo,
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.only(top=4),
                ),
                ft.Column(
                    controls=[
                        veredicto,
                        detalle_porcentaje,
                    ],
                    spacing=5,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                panel_alertas,
            ],
            spacing=14,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
    )

    # ==========================================================
    # FUNCIONES DE INTERFAZ
    # ==========================================================

    def actualizar_contador_caracteres(e=None):
        cantidad = len(caja_texto.value or "")
        palabra = "caracteres" if estado["idioma"] == "es" else "characters"
        contador_caracteres.value = f"{cantidad} {palabra}"
        page.update()

    caja_texto.on_change = actualizar_contador_caracteres

    def crear_alerta(texto: str, peligrosa=True) -> ft.Container:
        color = COLOR_PELIGRO if peligrosa else COLOR_SEGURO
        fondo = (
            COLOR_PELIGRO_SUAVE
            if peligrosa
            else COLOR_SEGURO_SUAVE
        )

        icono = (
            ft.Icons.WARNING_AMBER_ROUNDED
            if peligrosa
            else ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icono, size=17, color=color),
                    ft.Text(
                        texto,
                        size=12,
                        color=COLOR_TEXTO,
                        expand=True,
                    ),
                ],
                spacing=9,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=fondo,
            border=ft.Border.all(1, f"{color}33"),
            border_radius=12,
            padding=11,
        )

    def animar_contador(
        identificador: int,
        valor_final: float,
        texto_detalle: str,
    ):
        pasos = 24

        for paso in range(pasos + 1):
            if identificador != estado["animacion_contador"]:
                return

            valor_actual = valor_final * paso / pasos
            porcentaje_central.value = f"{valor_actual:.0f}%"
            circulo_progreso.value = valor_actual / 100
            detalle_porcentaje.value = (
                f"{valor_actual:.1f}% {texto_detalle}"
            )
            page.update()
            time.sleep(0.015)

    def mostrar_resultado(
        probabilidad_final: float,
        alertas: list,
    ):
        es_amenaza = probabilidad_final >= 50

        if es_amenaza:
            texto_veredicto = t("amenaza")
            detalle = t("riesgo")
            valor_mostrado = probabilidad_final
            color = COLOR_PELIGRO
            icono = ft.Icons.GPP_BAD_ROUNDED
        else:
            texto_veredicto = t("confiable")
            detalle = t("confianza")
            valor_mostrado = 100 - probabilidad_final
            color = COLOR_SEGURO
            icono = ft.Icons.GPP_GOOD_ROUNDED

        veredicto.value = texto_veredicto
        veredicto.color = color

        icono_resultado.name = icono
        icono_resultado.color = color

        circulo_progreso.color = color
        circulo_progreso.value = 0
        porcentaje_central.value = "0%"
        porcentaje_central.color = color

        lista_alertas.controls.clear()

        if alertas:
            for alerta in alertas:
                lista_alertas.controls.append(
                    crear_alerta(alerta, peligrosa=True)
                )
        else:
            lista_alertas.controls.append(
                crear_alerta(t("sin_alertas"), peligrosa=False)
            )

        boton_analizar.disabled = False
        boton_analizar.content.controls[1].value = t("analizar")
        boton_analizar.content.controls[0].name = (
            ft.Icons.SECURITY_ROUNDED
        )

        estado["animacion_contador"] += 1
        identificador = estado["animacion_contador"]

        page.update()
        page.run_thread(
            animar_contador,
            identificador,
            valor_mostrado,
            detalle,
        )

    def mostrar_error(mensaje: str):
        boton_analizar.disabled = False
        boton_analizar.content.controls[1].value = t("analizar")
        boton_analizar.content.controls[0].name = (
            ft.Icons.SECURITY_ROUNDED
        )

        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color="#FFFFFF"),
            bgcolor=COLOR_PELIGRO,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.snack_bar.open = True
        page.update()

    def ejecutar_analisis(mensaje: str, idioma: str):
        try:
            probabilidad, alertas = gestor.analizar(
                mensaje,
                idioma,
            )
            mostrar_resultado(probabilidad, alertas)

        except Exception as error:
            mostrar_error(f"{t('error_analisis')} {error}")

    def on_analizar_click(e):
        mensaje = (caja_texto.value or "").strip()

        if not mensaje:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    t("vacio"),
                    color="#FFFFFF",
                ),
                bgcolor=COLOR_ADVERTENCIA,
                behavior=ft.SnackBarBehavior.FLOATING,
            )
            page.snack_bar.open = True
            page.update()
            return

        boton_analizar.disabled = True
        boton_analizar.content.controls[1].value = t("analizando")
        boton_analizar.content.controls[0].name = (
            ft.Icons.HOURGLASS_TOP_ROUNDED
        )

        boton_analizar.scale = 0.97
        page.update()
        boton_analizar.scale = 1
        page.update()

        page.run_thread(
            ejecutar_analisis,
            mensaje,
            estado["idioma"],
        )

    boton_analizar.on_click = on_analizar_click

    def on_cambio_idioma(e):
        estado["idioma"] = (
            "es"
            if selector_idioma.selected_index == 0
            else "en"
        )

        subtitulo_principal.value = t("subtitulo")
        entrada_titulo.value = t("entrada_titulo")
        entrada_descripcion.value = t("entrada_descripcion")
        caja_texto.hint_text = t("placeholder")
        boton_analizar.content.controls[1].value = t("analizar")
        resultado_titulo.value = t("resultado_titulo")
        encabezado_alertas.controls[1].value = t("alertas")

        indicador_estado.content.controls[1].value = t("listo")

        if porcentaje_central.value == "--":
            veredicto.value = t("resultado_vacio")
            detalle_porcentaje.value = t("resultado_vacio_sub")

            lista_alertas.controls.clear()
            lista_alertas.controls.append(
                ft.Container(
                    content=ft.Text(
                        t("sin_alertas"),
                        size=12,
                        color=COLOR_TEXTO_SUAVE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=12,
                )
            )

        actualizar_contador_caracteres()

    selector_idioma.on_change = on_cambio_idioma

    # ==========================================================
    # DISEÑO RESPONSIVE
    # ==========================================================

    area_tarjetas = ft.ResponsiveRow(
        controls=[
            ft.Container(
                content=tarjeta_entrada,
                col={"xs": 12, "md": 7},
                padding=ft.Padding.only(
                    right=7,
                    bottom=12,
                ),
            ),
            ft.Container(
                content=tarjeta_resultado,
                col={"xs": 12, "md": 5},
                padding=ft.Padding.only(
                    left=7,
                    bottom=12,
                ),
            ),
        ],
        spacing=0,
        run_spacing=6,
        expand=True,
    )

    vista_principal = ft.Container(
        content=ft.Column(
            controls=[
                cabecera,
                area_tarjetas,
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.LOCK_OUTLINE_ROUNDED,
                            size=13,
                            color=COLOR_TEXTO_SUAVE,
                        ),
                        ft.Text(
                            "PhishGuard AI - Local threat analysis",
                            size=10,
                            color=COLOR_TEXTO_SUAVE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                ),
            ],
            spacing=20,
            expand=True,
        ),
        padding=ft.Padding.symmetric(
            horizontal=28,
            vertical=22,
        ),
        expand=True,
        opacity=0,
        animate_opacity=ft.Animation(
            550,
            ft.AnimationCurve.EASE_IN,
        ),
    )

    raiz = ft.Stack(
        controls=[
            vista_principal,
            vista_carga,
        ],
        expand=True,
    )

    page.add(raiz)

    # ==========================================================
    # CARGA Y ANIMACIONES
    # ==========================================================

    def animar_logo_carga():
        crecer = True

        while not gestor.listo and not gestor.error:
            contenedor_logo_carga.scale = (
                1.055 if crecer else 1.0
            )
            crecer = not crecer

            try:
                page.update()
            except Exception:
                return

            time.sleep(0.85)

    def cargar_modelos():
        page.run_thread(animar_logo_carga)

        def progreso(fraccion: float):
            barra_progreso.value = fraccion
            porcentaje_carga.value = f"{fraccion * 100:.0f}%"
            page.update()

        gestor.cargar(callback_progreso=progreso)

        if gestor.error:
            texto_carga.value = gestor.error
            texto_carga.color = COLOR_PELIGRO
            barra_progreso.color = COLOR_PELIGRO
            porcentaje_carga.color = COLOR_PELIGRO
            contenedor_logo_carga.scale = 1
            page.update()
            return

        texto_carga.value = t("listo")
        texto_carga.color = COLOR_SEGURO
        porcentaje_carga.value = "100%"
        contenedor_logo_carga.scale = 1
        page.update()

        time.sleep(0.35)

        vista_carga.opacity = 0
        vista_principal.opacity = 1
        page.update()

        time.sleep(0.5)

        vista_carga.visible = False
        page.update()

    page.run_thread(cargar_modelos)


if __name__ == "__main__":
    ft.run(
        main,
        assets_dir="assets",
    )
