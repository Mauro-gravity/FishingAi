PhishGuard AI

PhishGuard AI es una aplicación de análisis de seguridad diseñada para detectar posibles casos de phishing, fraude e ingeniería social en mensajes, correos electrónicos, SMS y enlaces.

Combina modelos de machine learning con un sistema de detección heurística para identificar diferentes indicadores de riesgo y generar una puntuación final.

⚠ ️ PhishGuard AI es una herramienta de apoyo a la seguridad. Sus resultados no garantizan que un mensaje sea seguro o malicioso.

---

Características

**Análisis mediante machine learning**
 -Análisis de dominios y URL.
 -Sistema de detección heurística.
 - 🇪🇸 Soporte para español.
 -🇬🇧 Soporte para inglés
 -Detección de patrones de phishing.
 -Detección de posibles fraudes de identidad.
 -Detección de solicitudes sospechosas de dinero.
 -Detección de posibles fraudes BEC (Business Email Compromise).
 -Detección de posibles fraudes de suplantación de ejecutivos.
 -Detección de patrones relacionados con SSO/MFA.
 -Detección de posibles suplantaciones de marcas en dominios.
 -Detección de dominios que utilizan técnicas similares a leetspeak.
 -Detección de solicitudes sospechosas relacionadas con códigos QR.
 -Interfaz gráfica moderna.
 -Sistema de puntuación de riesgo.
 -Funcionamiento local mediante modelos pre entrenados.

---

    ¿Cómo funciona?

PhishGuard AI utiliza dos capas principales de análisis:

1. Machine Learning

La aplicación utiliza modelos previamente entrenados para analizar:

- El contenido del mensaje.
- Los dominios y las URL encontradas dentro del mensaje.

Estos modelos generan probabilidades relacionadas con la posibilidad de que el contenido sea spam o fraudulento.

2. Análisis heurístico

Además del modelo de IA, PhishGuard AI busca patrones conocidos de ingeniería social y fraude.

Entre ellos:

- Enlaces externos sospechosos.
- Suplantación de marcas.
- Dominios que contienen varias marcas.
- Técnicas de homografía.
- Sustitución de caracteres.
- Solicitudes de autenticación sospechosas.
- Fraudes relacionados con familiares.
- Cambios sospechosos en cuentas bancarias.
- Solicitudes de transferencias.
- Mensajes que intentan generar urgencia.
- Posibles ataques BEC.
* Solicitudes para mantener los pagos en secreto.
- Técnicas relacionadas con códigos QR.

Finalmente, ambas capas se combinan para calcular una probabilidad de fraude.

De forma aproximada, el sistema utiliza:

- 15 % de machine learning.
    + 85 % de análisis heurístico.

---

    Interfaz

La aplicación dispone de una interfaz gráfica creada con Flet.

Permite:

1. Introducir un mensaje.
2. Seleccionar el idioma.
3. Ejecutar el análisis.
4. Obtener una puntuación de riesgo.
5. Consultar los indicadores detectados.

Idiomas disponibles:

* 🇪🇸 Español
* 🇬🇧 Inglés

---

##     Estructura del proyecto

FishingAi/
│
├── app.py
├── Detector_Es.py
├── Detector_En.py
├── heuristica.py
│
└── modelo_texto_es.pkl
└── vectorizador_texto_es.pkl
│
└── modelo_texto.pkl
└── vectorizador_texto.pkl
│
└── modelo_urls.pkl
└── vectorizador_urls.pkl
│
└── modelo_actualizado.pkl
└── vectorizador_actualizado.pkl
│
└── assets/
│ └── icon.png
│ └── icon.ico
│
└── README.md


### Archivos principales

| Archivo | Función
| ---------------------------- | ---------------------------------------------------
| app.py | Interfaz gráfica y gestión principal de la aplicación
| Detector_Es.py | Detector en español mediante consola
| Detector_En.py | Detector en inglés mediante consola
| heuristica.py | Sistema de detección de patrones sospechosos
| modelo_texto_es.pkl | Modelo de texto en español
| vectorizador_texto_es.pkl | Vectorizador del modelo español    
| `modelo_texto.pkl` | Modelo de texto en inglés |
| `vectorizador_texto.pkl` | Vectorizador del modelo inglés |
| `modelo_urls.pkl` | Modelo para analizar URL |
| `vectorizador_urls.pkl` | Vectorizador de URL |

---

    Requisitos

Se recomienda utilizar:

- Python 3.10+
* pip
- Flet
- scikit-learn.

Puedes instalar las dependencias necesarias con el siguiente comando:

bash
pip install flet scikit-learn


Si el proyecto incluye un archivo requirements.txt, puedes utilizar:

`bash
pip install -r requirements.txt
`

---

   Instalación

Clona el repositorio:

git clone 0url


Entra en la carpeta:

cd FishingAi


Instala las dependencias:

bash
pip install -r requirements.txt


---

Ejecutar PhishGuard AI.

Para iniciar la aplicación gráfica:

bash
python app.py


También existen detectores independientes mediante consola:

### Español

`bash
python Detector_Es.py
`

### English:

bash
python Detector_En.py


---

   Ejemplo de uso:

Introduce un mensaje como:

text
Tu cuenta necesita ser verificada inmediatamente.
Accede al siguiente enlace para evitar el bloqueo:
 
url


PhishGuard AI analizará:

- El texto.
- Los dominios encontrados.
- Los patrones de urgencia.
- Los indicadores de ingeniería social.
- Las características del dominio.

Después mostrará un resultado similar a este:

`AMENAZA DETECTADA

Probabilidad de fraude: 87 %

Indicadores detectados:
- Hipervínculo externo
- Solicitud urgente
- Patrón sospechoso de autenticación

---

    Sistema heurístico

El módulo heuristica.py contiene gran parte de la lógica de detección.

Entre las funciones implementadas se encuentran:

- detectar_homografo()
- detectar_secuestro_hilo()
- detectar_fraude_familiar()
- detectar_homografo_numerico()
- detectar phishing_sso()
- detectar_marca_multiple_en_dominio()
- detectar_suplantacion_marca_dominio()
- detectar_fraude_proveedor_bec()
- detectar_fraude_ceo_secreto()


Estas funciones permiten complementar el análisis realizado por los modelos de machine learning.

---

     Privacidad

PhishGuard AI está diseñado para realizar el análisis localmente utilizando los modelos incluidos en el proyecto.

Los mensajes introducidos en la aplicación no necesitan enviarse a una API externa para realizar el análisis.

No obstante, se recomienda revisar el código y la configuración del proyecto antes de utilizarlo en entornos donde se procesen datos sensibles.

---

    Limitaciones

Ningún sistema automático de detección de phishing es perfecto.

PhishGuard AI puede:

- Detectar falsos positivos.
- No detectar determinados ataques.
- Interpretar incorrectamente mensajes legítimos.
- Depender de la calidad de los modelos entrenados.
- Detectar patrones que no necesariamente implican que un mensaje sea malicioso.

Por ello, el resultado debe considerarse una señal de seguridad, no una prueba definitiva.

---

    Tecnologías utilizadas

* Python
* Flet
* scikit-learn
* **Machine Learning**
* **Análisis de texto**
* **Análisis de URL**
* Detección heurística
* Pickle para almacenar modelos entrenados.

---

   Estado del proyecto

    En desarrollo.

PhishGuard AI sigue evolucionando y se pueden añadir nuevos patrones de detección, modelos y funcionalidades.

---

    PhishGuard AI

Analiza. Detecta. Protege.

Una herramienta experimental de análisis de phishing y fraude basada en machine learning y detección heurística.

