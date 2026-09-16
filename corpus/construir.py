#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma los dos corpus contra los que se calibra el catálogo.

    python3 corpus/construir.py --ia 60         genera texto de IA con el CLI claude
    python3 corpus/construir.py --humano 200    baja prensa rioplatense pre-2023

El corpus de IA se versiona: es contenido generado y no hay derechos de nadie.
El humano NO se versiona. Queda en cache/, que está en .gitignore, y al repo
sube únicamente frecuencias.json, que son conteos. El script es reproducible
desde fuentes.json, así que cualquiera puede rehacer la medición.
"""
import concurrent.futures
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'tools'))
import dino

AGENTE = 'dino-textos/0.1 (corpus de calibración; +https://github.com/alfonsopintos89/dino-textos)'
PAUSA = 1.5          # segundos entre pedidos: ir despacio es parte del trato
MINIMO_PALABRAS = 250
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


def urls_pre_corte(fuente, corte):
    """Las URLs de artículos anteriores al corte, leídas del sitemap del sitio."""
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
            if m and int(m.group(1)) < corte:
                encontradas.append(url)
        sys.stderr.write('\r  sitemap p=%d — %d urls' % (pagina, len(encontradas)))
        time.sleep(PAUSA)
    sys.stderr.write('\n')
    return encontradas


def construir_humano(cuantos):
    config = json.load(open(os.path.join(AQUI, 'fuentes.json'), encoding='utf-8'))
    corte = int(config['corte'][:4])
    destino = os.path.join(AQUI, 'humano', 'cache')
    if not os.path.isdir(destino):
        os.makedirs(destino)

    for fuente in config['fuentes']:
        print('── %s (%s)' % (fuente['nombre'], fuente['variedad']))
        urls = urls_pre_corte(fuente, corte)
        print('  %d artículos anteriores a %d' % (len(urls), corte))
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


def _generar_uno(tarea):
    """Una llamada al CLI. Devuelve el manifiesto o None si no sirvió."""
    genero, i, prompt, ruta, nombre = tarea
    if os.path.exists(ruta):
        return None
    try:
        salida = subprocess.run(
            ['claude', '-p', prompt + ' Escribilo en español. Solo el texto.'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=600)
    except (OSError, subprocess.TimeoutExpired):
        sys.stderr.write('  falló %s\n' % nombre)
        return None
    texto = salida.stdout.decode('utf-8', 'replace').strip()
    if len(texto.split()) < 80:
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
            nombre = '%s-%02d.txt' % (genero, i)
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


if __name__ == '__main__':
    args = sys.argv[1:]
    cuantos = int(args[1]) if len(args) > 1 else 60
    if args and args[0] == '--humano':
        sys.exit(construir_humano(cuantos))
    if args and args[0] == '--ia':
        sys.exit(construir_ia(cuantos))
    sys.exit(__doc__)
