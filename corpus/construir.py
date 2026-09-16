#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma los dos corpus contra los que se calibra el catálogo.

    python3 corpus/construir.py --ia 60         genera texto de IA con el CLI claude
    python3 corpus/construir.py --humano 200    baja prensa rioplatense pre-2023
    python3 corpus/construir.py --openrouter gpt                 modelo de .env.local
    python3 corpus/construir.py --openrouter grok x-ai/grok-4.6  cualquier otro

El corpus de IA se versiona: es contenido generado y no hay derechos de nadie.
El humano NO se versiona. Queda en cache/, que está en .gitignore, y al repo
sube únicamente frecuencias.json, que son conteos. El script es reproducible
desde fuentes.json, así que cualquiera puede rehacer la medición.
"""
import concurrent.futures
import collections
import hashlib
import json
import os
import random
import re
import subprocess
import tempfile
import sys
import time
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'tools'))
import textosaurio as dino

AGENTE = 'textosaurio/1.0 (corpus de calibración; +https://github.com/alfonsopintos89/textosaurio)'
PAUSA = 1.5          # segundos entre pedidos: ir despacio es parte del trato
# Cien y no más: la diaria tiene paywall, así que lo público de cada nota es la
# bajada, unas 100-150 palabras de prosa real. El mínimo se aplica DESPUÉS de
# sacar la plantilla, que en ese sitio son 215 palabras de términos y
# condiciones por nota — más que el artículo.
MINIMO_PALABRAS = 100
PALABRAS_DE_PARRAFO = 12   # un renglón más corto que esto es navegación, no prosa


def bajar(url):
    pedido = urllib.request.Request(url, headers={'User-Agent': AGENTE})
    return urllib.request.urlopen(pedido, timeout=30).read().decode('utf-8', 'replace')


def prosa(html):
    """Los párrafos de una nota, sin el menú ni los pies de foto.

    Un renglón de menos de doce palabras es navegación, epígrafe o botón. Se
    van todos: meterlos al corpus mediría la maquetación del diario en vez de
    cómo escribe la gente.
    """
    renglones = [r for r in dino.texto_visible(html).split('\n')
                 if len(r.split()) >= PALABRAS_DE_PARRAFO]
    return '\n'.join(renglones)


def sub_sitemaps_pre_corte(locs, patron_fecha, corte):
    """Los sub-sitemaps cuyo nombre declara una fecha anterior al corte.

    `corte` es una tupla (año, mes). Un sub-sitemap sin fecha en el nombre queda
    afuera: el corpus entero se sostiene sobre la fecha de corte, y un documento
    que no puede probar la suya vale menos que no tenerlo.
    """
    patron = re.compile(patron_fecha)
    elegidos = []
    for loc in locs:
        m = patron.search(loc)
        if m and (int(m.group(1)), int(m.group(2))) < corte:
            elegidos.append(loc)
    return elegidos


def _urls_paginado(fuente, corte):
    """Sitios cuyo sitemap se pagina y trae la fecha en la URL del artículo."""
    encontradas = []
    patron = re.compile(fuente['patron_anio'])
    desde, hasta = fuente['paginas']
    # De a saltos: cada página del sitemap trae mil artículos, así que tocar una
    # de cada ocho ya cubre 2012-2022 entero con una décima parte de los pedidos.
    for pagina in range(desde, hasta + 1, fuente.get('paso', 8)):
        try:
            xml = bajar(fuente['sitemap'].format(pagina=pagina))
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            sys.stderr.write('  sitemap p=%d: %s\n' % (pagina, e))
            continue
        for url in re.findall(r'<loc>(.*?)</loc>', xml):
            m = patron.search(url)
            if m and int(m.group(1)) < corte[0]:
                encontradas.append(url)
        sys.stderr.write('\r  sitemap p=%d — %d urls' % (pagina, len(encontradas)))
        time.sleep(PAUSA)
    sys.stderr.write('\n')
    return encontradas


def _urls_indice(fuente, corte):
    """Sitios con índice de sitemaps donde la fecha está en el nombre del archivo.

    Es el caso más limpio: el filtro de fecha se aplica antes de bajar nada, así
    que no se toca una sola URL posterior al corte.
    """
    indice = bajar(fuente['sitemap'])
    subs = sub_sitemaps_pre_corte(re.findall(r'<loc>(.*?)</loc>', indice),
                                  fuente['patron_fecha_sitemap'], corte)
    sys.stderr.write('  %d sub-sitemaps anteriores al corte\n' % len(subs))
    encontradas = []
    for sub in subs:
        time.sleep(PAUSA)
        try:
            xml = bajar(sub)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            sys.stderr.write('  %s: %s\n' % (sub.rsplit('/', 1)[-1], e))
            continue
        encontradas += re.findall(r'<loc>(.*?)</loc>', xml)
        sys.stderr.write('\r  %d urls' % len(encontradas))
    sys.stderr.write('\n')
    return encontradas


UMBRAL_PLANTILLA = 0.2


def quitar_plantilla(documentos, umbral=UMBRAL_PLANTILLA):
    """Saca los renglones que se repiten en más de `umbral` de los documentos.

    Un pie de página, un aviso de suscripción o un selector de edición aparecen
    en todas las notas del sitio. Dejarlos adentro haría que el corpus midiera
    la maquetación del diario en vez de cómo escribe la gente, y el renglón
    repetido pesaría cien veces más que cualquier frase real.

    En eldiarioAR es peor todavía: comparte plantilla con elDiario.es, así que
    el texto de template viene en peninsular y ensuciaría justo el eje que mide
    el registro.

    Los documentos que quedan sin nada propio se descartan.
    """
    if not documentos:
        return []
    veces = collections.Counter()
    for doc in documentos:
        for renglon in set(doc.split('\n')):
            veces[renglon] += 1
    piso = max(2, int(len(documentos) * umbral))
    plantilla = set(r for r, n in veces.items() if n >= piso)

    limpios = []
    for doc in documentos:
        propios = [r for r in doc.split('\n') if r not in plantilla]
        if propios:
            limpios.append('\n'.join(propios))
    return limpios


def urls_pre_corte(fuente, corte):
    """Las URLs de artículos anteriores al corte, leídas del sitemap del sitio."""
    if fuente.get('modo') == 'indice':
        return _urls_indice(fuente, corte)
    return _urls_paginado(fuente, corte)


def limpiar_cache(destino, prefijo):
    """Aplica `quitar_plantilla` a los textos ya bajados de una fuente.

    Va aparte de la descarga porque la plantilla solo se puede ver mirando el
    conjunto: un renglón repetido no se distingue de prosa hasta que tenés los
    otros cien documentos al lado.
    """
    nombres = sorted(n for n in os.listdir(destino)
                     if n.startswith(prefijo) and n.endswith('.txt'))
    if not nombres:
        return
    textos = [open(os.path.join(destino, n), encoding='utf-8').read() for n in nombres]
    antes = sum(len(t.split()) for t in textos)

    veces = collections.Counter()
    for t in textos:
        for r in set(t.split('\n')):
            veces[r] += 1
    piso = max(2, int(len(textos) * UMBRAL_PLANTILLA))
    plantilla = set(r for r, n in veces.items() if n >= piso)

    quedaron = 0
    for nombre, texto in zip(nombres, textos):
        propios = [r for r in texto.split('\n') if r not in plantilla]
        ruta = os.path.join(destino, nombre)
        if len(' '.join(propios).split()) < MINIMO_PALABRAS:
            os.remove(ruta)
            continue
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write('\n'.join(propios))
        quedaron += 1
    despues = sum(len(open(os.path.join(destino, n), encoding='utf-8').read().split())
                  for n in os.listdir(destino) if n.startswith(prefijo))
    print('  %s: %d renglones de plantilla fuera, %d→%d documentos, %d→%d palabras'
          % (prefijo, len(plantilla), len(nombres), quedaron, antes, despues))


def construir_humano(cuantos):
    config = json.load(open(os.path.join(AQUI, 'fuentes.json'), encoding='utf-8'))
    corte = (int(config['corte'][:4]), int(config['corte'][5:7]))
    destino = os.path.join(AQUI, 'humano', 'cache')
    if not os.path.isdir(destino):
        os.makedirs(destino)

    for fuente in config['fuentes']:
        print('── %s (%s)' % (fuente['nombre'], fuente['variedad']))
        urls = urls_pre_corte(fuente, corte)
        print('  %d artículos anteriores a %04d-%02d' % (len(urls), corte[0], corte[1]))
        # Muestra determinística: la misma semilla da el mismo corpus, que es lo
        # que hace reproducible el número publicado.
        random.Random(1976).shuffle(urls)

        guardados = 0
        for url in urls:
            if guardados >= cuantos:
                break
            nombre = '%s-%s.txt' % (fuente['nombre'].replace(' ', ''),
                                    hashlib.sha1(url.encode()).hexdigest()[:10])
            ruta = os.path.join(destino, nombre)
            if os.path.exists(ruta):
                guardados += 1
                continue
            try:
                texto = prosa(bajar(url))
            except (urllib.error.HTTPError, urllib.error.URLError, UnicodeError):
                continue
            finally:
                time.sleep(PAUSA)
            if len(texto.split()) < MINIMO_PALABRAS:
                continue
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(texto)
            guardados += 1
            sys.stderr.write('\r  %d/%d artículos' % (guardados, cuantos))
        sys.stderr.write('\n')
        limpiar_cache(destino, fuente['nombre'].replace(' ', ''))
    return 0


# Prompts neutros a propósito. En ningún caso se le pide al modelo que evite
# sonar a IA: lo que hay que medir es exactamente lo que escribe por defecto.
GENEROS = {
    'landing': [
        'Escribí el copy de una landing para una inmobiliaria en Montevideo.',
        'Escribí el copy de una landing para un estudio contable en Rosario.',
        'Escribí el copy de la home de una app de delivery uruguaya.',
        'Escribí el copy de una landing para una empresa de paneles solares.',
        'Escribí el copy de una landing para una clínica odontológica.',
    ],
    'posteo': [
        'Escribí un posteo de blog sobre cómo elegir un proveedor de software.',
        'Escribí un artículo sobre el mercado inmobiliario uruguayo para un blog.',
        'Escribí una newsletter para clientes de una agencia de marketing.',
        'Escribí un posteo de blog sobre productividad para equipos remotos.',
        'Escribí un artículo sobre inteligencia artificial para un público general.',
    ],
    'producto': [
        'Escribí el README de una librería de JavaScript para manejar fechas.',
        'Escribí la documentación de onboarding de una app de facturación.',
        'Escribí los textos de interfaz de un panel de control de una app de gestión.',
        'Escribí las notas de la versión 2.0 de una app de gestión de stock.',
        'Escribí la página de preguntas frecuentes de un servicio de hosting.',
    ],
}


# Treinta pedidos más para Claude, con rubros que no están en GENEROS. La mitad
# están escritos como los escribe alguien que arma una web con Claude Code, que
# es de donde sale la mayor parte del copy de Claude que termina publicado.
#
# Los números 05 a 09 de cada género son para DESCUBRIR patrones; del 10 al 14
# quedan guardados para VALIDAR. Un patrón descubierto mirando un texto no puede
# probarse sobre ese mismo texto: daría bien siempre.
CLAUDE_EXTRA = {
    'landing': [
        'Escribí el copy de una landing para una escuela de surf en La Paloma.',
        'Escribí el copy de una landing para una veterinaria en Córdoba.',
        'Escribí el copy de una landing para un gimnasio boutique en Palermo.',
        'Escribí el copy de una landing para una bodega familiar de Canelones.',
        'Escribí el copy de una landing para un software de gestión de turnos médicos.',
        'Estoy armando en Next.js la web de una agencia de viajes de Montevideo. Escribí los textos de la home: hero, servicios, por qué elegirnos y llamada a la acción.',
        'Estoy haciendo la landing de una app de finanzas personales para Argentina. Pasame el copy de todas las secciones.',
        'Armá los textos de la home para la web de un estudio de arquitectura en Punta del Este.',
        'Necesito el copy de la landing de un curso online de programación para principiantes.',
        'Escribí los textos de la página principal de una empresa de mudanzas en Buenos Aires.',
    ],
    'posteo': [
        'Escribí un posteo de blog sobre cómo ahorrar en dólares siendo uruguayo.',
        'Escribí un artículo para el blog de una consultora sobre transformación digital en pymes.',
        'Escribí una newsletter mensual para los socios de un club deportivo.',
        'Escribí un posteo de LinkedIn sobre lo que aprendí liderando un equipo de desarrollo.',
        'Escribí un artículo de blog sobre tendencias de diseño web.',
        'Estoy armando el blog de una startup de logística. Escribí el primer artículo, sobre por qué fallan las entregas de última milla.',
        'Para el blog de mi estudio contable, escribí un artículo sobre monotributo para freelancers.',
        'Escribí un posteo para el blog de una marca de café de especialidad sobre cómo preparar un buen filtrado.',
        'Escribí la newsletter de lanzamiento de una nueva función de una app de delivery.',
        'Escribí un artículo sobre trabajo remoto para el blog de una empresa de software uruguaya.',
    ],
    'producto': [
        'Escribí el README de una API REST para gestionar reservas de restaurantes.',
        'Escribí los mensajes de error y confirmación de un formulario de registro.',
        'Escribí la página "Sobre nosotros" de una startup de tecnología educativa.',
        'Escribí el texto de onboarding de una app para organizar gastos compartidos.',
        'Escribí la sección de precios con tres planes para un SaaS de facturación.',
        'Estoy armando el panel de administración de un e-commerce. Escribí los textos de la pantalla de inicio y de los estados vacíos.',
        'Escribí la documentación para desarrolladores de un SDK de pagos.',
        'Escribí los textos de los emails transaccionales de una tienda online: bienvenida, compra confirmada y envío.',
        'Escribí las preguntas frecuentes de una app de alquiler de autos.',
        'Escribí la página de términos de uso resumida en lenguaje claro para una app de citas médicas.',
    ],
}


def construir_claude_extra(en_paralelo=5):
    """Los treinta textos de CLAUDE_EXTRA, generados desde una carpeta neutra.

    El aislamiento está en `_generar_uno`: Claude Code mete en su contexto la
    carpeta de trabajo, el estado de git y la sesión padre, y un repo lleno de
    catálogos de slop no es un contexto neutro.
    """
    destino = os.path.join(AQUI, 'ia')
    tareas = []
    for genero, prompts in CLAUDE_EXTRA.items():
        for j, prompt in enumerate(prompts):
            nombre = 'claude-%s-%02d.txt' % (genero, j + 5)
            tareas.append((genero, j + 5, prompt, os.path.join(destino, nombre), nombre))
    manifiesto = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=en_paralelo) as pool:
        for fila in pool.map(_generar_uno, tareas):
            if fila:
                fila['uso'] = 'validación' if fila['archivo'][-6:-4] >= '10' else 'descubrimiento'
                manifiesto.append(fila)
    ruta_manifiesto = os.path.join(destino, 'manifiesto.json')
    previo = json.load(open(ruta_manifiesto, encoding='utf-8'))
    with open(ruta_manifiesto, 'w', encoding='utf-8') as f:
        json.dump(previo + manifiesto, f, ensure_ascii=False, indent=2)
    print('%d textos nuevos de Claude' % len(manifiesto))
    return 0


# Marcas de que el modelo vio este proyecto mientras escribía. Pasó con doce textos
# de Claude: generados con el repo como carpeta de trabajo, leyeron las reglas de
# dino, pusieron [falta dato] e intentaron correr el linter. Un texto así no mide
# el default del modelo, mide al modelo obedeciendo a este repo.
CONTAMINACION = re.compile(
    r'\bdino\b|textosaurio|\blinter\b|scratchpad|\bslop\b|tools/|\[falta dato\]|deslop|skill\.md',
    re.I)

# Solo lo que el CLI necesita para arrancar y autenticarse. Afuera las variables de
# la sesión de Claude Code que está corriendo esto: con ellas el subproceso se
# engancha a la sesión padre. Y afuera cualquier clave de API que no le compete.
ENTORNO_PERMITIDO = ('HOME', 'PATH', 'USER', 'LOGNAME', 'SHELL', 'LANG', 'LC_ALL',
                     'TERM', 'TMPDIR')

HERRAMIENTAS_BLOQUEADAS = ['Bash', 'Read', 'Write', 'Edit', 'Glob', 'Grep', 'WebFetch',
                           'WebSearch', 'Agent', 'Task', 'Skill', 'NotebookEdit',
                           'TodoWrite']


def contaminado(texto):
    return bool(CONTAMINACION.search(texto))


def entorno_limpio(entorno):
    return dict((k, v) for k, v in entorno.items() if k in ENTORNO_PERMITIDO)


def _generar_uno(tarea):
    """Una llamada al CLI, aislada. Devuelve el manifiesto o None si no sirvió.

    Carpeta temporal vacía y con nombre neutro, entorno sin la sesión padre, y sin
    herramientas: el modelo tiene que escribir, no explorar. Aun así, si el texto
    trae marcas del proyecto, se descarta.
    """
    genero, i, prompt, ruta, nombre = tarea
    if os.path.exists(ruta):
        return None
    try:
        carpeta = tempfile.mkdtemp(prefix='redaccion-')
        salida = subprocess.run(
            ['claude', '-p', prompt + ' Escribilo en español. Solo el texto.',
             '--disallowed-tools'] + HERRAMIENTAS_BLOQUEADAS,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=600,
            cwd=carpeta, env=entorno_limpio(os.environ))
    except (OSError, subprocess.TimeoutExpired):
        sys.stderr.write('  falló %s\n' % nombre)
        return None
    texto = salida.stdout.decode('utf-8', 'replace').strip()
    if len(texto.split()) < 80:
        return None
    if contaminado(texto):
        # Se guarda aparte para poder mirar qué lo delató: sin esto, un falso
        # positivo de la guarda y una contaminación real se ven iguales.
        with open(ruta + '.contaminado', 'w', encoding='utf-8') as f:
            f.write(texto)
        sys.stderr.write('  CONTAMINADO, descartado: %s (%s)\n'
                         % (nombre, CONTAMINACION.search(texto).group(0)))
        return None
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)
    sys.stderr.write('  listo %s (%d palabras)\n' % (nombre, len(texto.split())))
    return {'archivo': nombre, 'genero': genero, 'prompt': prompt,
            'modelo': 'claude (CLI)', 'fecha': time.strftime('%Y-%m-%d')}


def construir_ia(cuantos, en_paralelo=5):
    """Genera el corpus de IA. En paralelo porque una llamada tarda minutos."""
    destino = os.path.join(AQUI, 'ia')
    if not os.path.isdir(destino):
        os.makedirs(destino)

    tareas = []
    por_genero = max(1, cuantos // len(GENEROS))
    for genero, prompts in GENEROS.items():
        for i in range(por_genero):
            prompt = prompts[i % len(prompts)]
            if i >= len(prompts):
                prompt += ' Que sea de otro rubro, distinto de los habituales.'
            nombre = 'claude-%s-%02d.txt' % (genero, i)
            tareas.append((genero, i, prompt, os.path.join(destino, nombre), nombre))

    manifiesto = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=en_paralelo) as pool:
        for fila in pool.map(_generar_uno, tareas):
            if fila:
                manifiesto.append(fila)

    ruta_manifiesto = os.path.join(destino, 'manifiesto.json')
    previo = []
    if os.path.exists(ruta_manifiesto):
        previo = json.load(open(ruta_manifiesto, encoding='utf-8'))
    with open(ruta_manifiesto, 'w', encoding='utf-8') as f:
        json.dump(previo + manifiesto, f, ensure_ascii=False, indent=2)
    print('%d textos en el corpus de IA' % len(os.listdir(destino)))
    return 0



# ── OpenRouter ───────────────────────────────────────────────────────────────
# Para generar el corpus con modelos que no tienen CLI instalado. La clave vive
# en .env.local, que está en .gitignore, y no se imprime nunca: ni en errores,
# ni en el manifiesto.

RAIZ = os.path.dirname(AQUI)
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'


def leer_env(ruta):
    """Un .env mínimo: CLAVE=valor, con o sin comillas, ignorando comentarios."""
    env = {}
    for renglon in open(ruta, encoding='utf-8'):
        renglon = renglon.strip()
        if not renglon or renglon.startswith('#') or '=' not in renglon:
            continue
        clave, valor = renglon.split('=', 1)
        env[clave.strip()] = valor.strip().strip('"').strip("'")
    return env


def cuerpo_openrouter(modelo, prompt):
    """Un solo mensaje de usuario, sin system prompt.

    Cualquier instrucción de estilo, aunque sea neutra, ya es algo que la gente
    que pega un pedido en el chat no escribe, y el corpus mide ese default.
    """
    return {'model': modelo,
            'messages': [{'role': 'user',
                          'content': prompt + ' Escribilo en español. Solo el texto.'}]}


def describir_error(codigo, cuerpo, clave):
    """El error de la API, con la clave tachada si por algún motivo viniera adentro."""
    texto = (cuerpo or '')[:200]
    if clave:
        texto = texto.replace(clave, '[clave]')
    return 'HTTP %s: %s' % (codigo, texto)


def _generar_openrouter(tarea):
    genero, i, prompt, ruta, nombre, clave, modelo = tarea
    if os.path.exists(ruta):
        return None
    datos = json.dumps(cuerpo_openrouter(modelo, prompt)).encode('utf-8')
    pedido = urllib.request.Request(OPENROUTER_URL, data=datos, headers={
        'Authorization': 'Bearer ' + clave,
        'Content-Type': 'application/json',
        'X-Title': 'textosaurio corpus'})
    try:
        respuesta = json.loads(urllib.request.urlopen(pedido, timeout=300).read().decode('utf-8'))
        texto = respuesta['choices'][0]['message']['content'].strip()
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode('utf-8', 'replace')
        sys.stderr.write('  falló %s — %s\n' % (nombre, describir_error(e.code, cuerpo, clave)))
        return None
    except (urllib.error.URLError, KeyError, IndexError, ValueError) as e:
        sys.stderr.write('  falló %s — %s\n' % (nombre, type(e).__name__))
        return None
    if len(texto.split()) < 80:
        sys.stderr.write('  descartado %s: %d palabras\n' % (nombre, len(texto.split())))
        return None
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)
    sys.stderr.write('  listo %s (%d palabras)\n' % (nombre, len(texto.split())))
    return {'archivo': nombre, 'genero': genero, 'prompt': prompt,
            'modelo': modelo + ' (OpenRouter)', 'fecha': time.strftime('%Y-%m-%d'),
            'palabras': len(texto.split())}


# Diez de los pedidos de CLAUDE_EXTRA, para que otros modelos respondan exactamente
# lo mismo que Claude. Con los mismos pedidos se puede separar lo que es acento de
# Claude de lo que es acento de cualquier IA.
CONTRASTE = [('landing', 0), ('landing', 1), ('landing', 5), ('landing', 6),
             ('posteo', 0), ('posteo', 3), ('posteo', 5),
             ('producto', 2), ('producto', 4), ('producto', 5)]


def construir_openrouter(prefijo, modelo=None, en_paralelo=5, contraste=False):
    """Genera los quince textos con un modelo de OpenRouter.

    Sin `modelo` usa OPENROUTER_TEXT_MODEL de .env.local. Con él, cualquier otro
    — así se suman familias al corpus sin tocar la configuración.
    """
    env = leer_env(os.path.join(RAIZ, '.env.local'))
    clave = env.get('OPENROUTER_API_KEY')
    modelo = modelo or env.get('OPENROUTER_TEXT_MODEL')
    if not clave or not modelo:
        sys.stderr.write('faltan OPENROUTER_API_KEY u OPENROUTER_TEXT_MODEL en .env.local\n')
        return 2
    destino = os.path.join(AQUI, 'ia')
    tareas = []
    if contraste:
        for genero, j in CONTRASTE:
            nombre = '%s-%s-%02d.txt' % (prefijo, genero, j + 5)
            tareas.append((genero, j + 5, CLAUDE_EXTRA[genero][j],
                           os.path.join(destino, nombre), nombre, clave, modelo))
    else:
        for genero, prompts in GENEROS.items():
            for i, prompt in enumerate(prompts):
                nombre = '%s-%s-%02d.txt' % (prefijo, genero, i)
                tareas.append((genero, i, prompt, os.path.join(destino, nombre), nombre,
                               clave, modelo))
    print('generando %d textos con %s' % (len(tareas), modelo))
    manifiesto = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=en_paralelo) as pool:
        for fila in pool.map(_generar_openrouter, tareas):
            if fila:
                manifiesto.append(fila)
    ruta_manifiesto = os.path.join(destino, 'manifiesto.json')
    previo = json.load(open(ruta_manifiesto, encoding='utf-8')) if os.path.exists(ruta_manifiesto) else []
    with open(ruta_manifiesto, 'w', encoding='utf-8') as f:
        json.dump(previo + manifiesto, f, ensure_ascii=False, indent=2)
    print('%d textos nuevos' % len(manifiesto))
    return 0 if manifiesto else 1


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--claude-extra':
        sys.exit(construir_claude_extra())
    if args and args[0] in ('--openrouter', '--openrouter-contraste'):
        sys.exit(construir_openrouter(args[1] if len(args) > 1 else 'gpt',
                                      args[2] if len(args) > 2 else None,
                                      contraste=args[0] == '--openrouter-contraste'))
    cuantos = int(args[1]) if len(args) > 1 else 60
    if args and args[0] == '--limpiar':
        config = json.load(open(os.path.join(AQUI, 'fuentes.json'), encoding='utf-8'))
        destino = os.path.join(AQUI, 'humano', 'cache')
        for fuente in config['fuentes']:
            limpiar_cache(destino, fuente['nombre'].replace(' ', ''))
        sys.exit(0)
    if args and args[0] == '--humano':
        sys.exit(construir_humano(cuantos))
    if args and args[0] == '--ia':
        sys.exit(construir_ia(cuantos))
    sys.exit(__doc__)
