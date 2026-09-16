#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Textosaurio: cinco puntajes del 1 al 10 para un texto en español hecho con IA.

    1 sin completar          marcadores de plantilla que quedaron
    2 especificidad          datos que un competidor no podría copiar
    3 correcto y completo    trato, signos, mayúsculas, repeticiones
    4 suena humano           señales de IA medidas contra prensa rioplatense
    5 hecho para el formato  web, blog, LinkedIn o Instagram

El general es el promedio, con tope en 6 si algo impide publicar. Este script
es la parte que no necesita criterio. El skill (SKILL.md) suma el juicio de
Claude y cita la frase exacta por cada punto que descuenta.
"""
import json
import os
import sys
import html as _html      # con alias: `texto_visible` recibe un parámetro `html`
import re

# Etiquetas que cierran una pieza de copy. Un botón y el párrafo que le sigue son
# dos textos distintos, y la regla de CTA necesita ver dónde termina cada uno.
# `a`, `span`, `strong` y `em` quedan afuera a propósito: son de línea, y cortar
# ahí partiría oraciones al medio y dejaría ciegas a las reglas de construcción.
BLOQUE = re.compile(
    r'</?(?:p|div|section|article|h[1-6]|li|ul|ol|button|form|label'
    r'|td|th|tr|table|br|hr|blockquote|header|footer|nav|main)\b[^>]*>',
    re.I)


def normalizar(t):
    """Pliega las variantes tipográficas a las que los patrones sí matchean.

    Un guion de no separación no es `-`, un espacio duro no es un espacio y una
    comilla curva no es `'`. Si alguna se escapa, `de-vanguardia` y las formas
    con apóstrofo dejan de matchear justo sobre el texto real, que es de donde
    salen los caracteres lindos.

    Lo que NUNCA hace es sacar tildes. Es el reflejo normal al normalizar texto
    en español, y acá dejaría ciego al eje de registro entero: la tilde es lo
    único que separa `regístrate` (tuteo) de `registrate` (voseo).

    Los renglones se conservan. Marcan dónde termina una pieza de copy.
    """
    t = t.replace('‑', '-').replace(' ', ' ').replace('’', "'")
    t = re.sub(r'[^\S\n]+', ' ', t)
    renglones = [r.strip() for r in t.split('\n')]
    return '\n'.join(r for r in renglones if r)


def texto_visible(html):
    """Lo que un visitante lee de verdad. Sin script, sin style, sin etiquetas."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = BLOQUE.sub('\n', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    # Todas las entidades, no seis escritas a mano: las numéricas se colaban como
    # texto literal y cada `&#xed;` rompía una palabra acentuada por la mitad.
    t = _html.unescape(t)
    return normalizar(t)


def prosa_markdown(md):
    """La prosa de un markdown, con los especímenes citados afuera.

    Un literal no es copy. Un catálogo que documenta `potenciar` no shipeó la
    palabra: la citó. Un linter que no distingue las dos cosas hace que todo
    catálogo puntúe cero, así que salen los bloques cercados, el código en
    línea, el texto tachado y el alt de las imágenes.

    El texto de los enlaces se queda, porque se lee como parte de la oración.
    """
    md = re.sub(r'```.*?```', '\n', md, flags=re.S)
    # Un párrafo cortado a mano en varios renglones es una sola pieza de copy. Sin
    # unirlo, una pregunta partida en dos renglones pierde su `¿` en el primero.
    # No se une lo que termina en puntuación o en negrita (`**Te atendemos**` es
    # el título de un bloque) ni lo que abre una lista, un título o una tabla.
    md = re.sub(r'(?<=[^\s.!?:*)\]|])[ \t]*\n(?=[ \t]*[^\W\d_¿¡«(`])', ' ', md)
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', '\n', md)
    md = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', md)
    # Suplentes, no borrados. Sacar `[falta dato]` del todo suelda la cláusula de
    # al lado y puede inventar un ritmo de tres que nadie escribió, y un linter
    # que inventa un acierto es peor que uno que se pierde uno.
    md = re.sub(r'`[^`]*`', ' eso ', md)
    md = re.sub(r'~~.*?~~', ' eso ', md, flags=re.S)
    md = re.sub(r'^\s{0,3}#{1,6}\s*(.*)$', r'\n\1\n', md, flags=re.M)
    md = re.sub(r'\|', '\n', md)
    md = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', '\n', md, flags=re.M)
    md = re.sub(r'^\s*>\s?', '\n', md, flags=re.M)
    md = re.sub(r'[*_>]', ' ', md)
    return normalizar(md)


GRUPOS_SLOP = ('lexico', 'construcciones', 'cadencia', 'ritmo', 'venta')
GRUPOS_REGISTRO = ('pronombres', 'imperativos', 'lexico_peninsular')

# ── señales de IA ──────────────────────────────────────────────────────────────

# Por raíz, para las palabras que en este registro no tienen uso honesto. El copy
# se escribe conjugado y con género, así que matchear la forma exacta se pierde
# la superficie más común de todas: `Acme potencia tu negocio`.
LEXICO_RAIZ = [
    'optimizar', 'transformador', 'robusto',
    'holístico', 'sinergia', 'empoderar', 'desbloquear', 'inigualable',
    'vanguardia', 'meticuloso', 'maximizar', 'disruptivo', 'escalable', 'sofisticado', 
]

# Frases hechas y palabras que solo son tell en su forma exacta. Van enteras
# porque la raíz cazaría el uso corriente: `viaje` es una palabra común y
# marcarla sería llorar lobo, pero `un viaje de transformación` no lo es.
LEXICO_EXACTO = [
    'experiencia única', 'de última generación', 'en constante evolución',
    'en el mundo actual', 'en la era digital', 'de vanguardia', 'soluciones integrales', 'un viaje de', 'el mundo de hoy', 'a otro nivel', 'sin fisuras',
    'de primer nivel', 'de clase mundial', 'nuestra propuesta de valor',
]

# Palabras cuya raíz choca con un sustantivo corriente y necesitan patrón propio.
# `potenciar` es el caso: la raíz `potenci` caza también `potencia` y `potencias`,
# que en prosa política son las grandes potencias y no tienen nada que ver con el
# verbo. Sobre 355.386 palabras de prensa rioplatense, la versión por raíz marcaba
# el 4,1% de los textos. Acá van solo las formas inequívocamente verbales, más la
# tercera persona cuando arrastra un objeto — `potencia tu marca` —, que es la
# superficie que el copy usa de verdad.
LEXICO_PATRON = [
    (r'(?<!\w)potenci(?:ar|ando|ad[oa]s?|amos|an|ará|arán|aría|arían|aron)(?!\w)'
     r'|(?<!\w)potencia(?=\s+(?:tu|su|tus|sus|el|la|los|las|nuestr[oa]s?)\b)',
     'potenciar'),
]

SUFIJOS = (r'(?:a|as|o|os|e|es|an|en|ar|ado|ada|ados|adas|ando|amos|'
           r'ación|aciones|ador|adora|adores|adoras|able|ables|'
           r'ico|ica|icos|icas|mente|'
           r'ó|é|aron|aba|aban|ará|arán|aría|arían)?')


def _raiz(palabra):
    """La raíz de una palabra española, para que todas sus flexiones matcheen.

    Saca la terminación de infinitivo (`potenciar` → `potenci`) o la de género
    (`robusto` → `robust`), y después SUFIJOS deja volver a pegar cualquier
    flexión. Es deliberadamente tosco: no es un lematizador, es lo mínimo que
    hace falta para que una lista curada de veinte palabras no se pierda
    `potenciamos`, `potenciada` y `potenciando`.
    """
    if len(palabra) > 4 and palabra[-2:] in ('ar', 'er', 'ir'):
        return palabra[:-2]
    if len(palabra) > 4 and palabra[-1] in 'oae':
        return palabra[:-1]
    return palabra


def _patron_raiz(palabra):
    raiz = _raiz(palabra)
    if len(raiz) < 4:                      # muy corta para cortarla sin riesgo
        return r'(?<!\w)%s(?!\w)' % re.escape(palabra)
    return r'(?<!\w)%s%s(?!\w)' % (re.escape(raiz), SUFIJOS)


CONSTRUCCIONES = [
    # `no solo X, sino Y` NO está acá, y es el hallazgo más fuerte del proyecto.
    # Es la forma insignia del catálogo inglés y en español no transfiere: es un
    # correlativo gramatical corriente, no un tic de marketing. Sobre 355.386
    # palabras de prensa rioplatense marcaba el 8,6% de los textos, con frases
    # como «advertido no solo por ecologistas sino por organismos como el BCE».
    # Está medida y rechazada en referencias/fuentes.md.
    (r'\bno se trata (?:solo |sólo )?de\b[^.!?]{0,80}[,.]\s*(?:es|sino|se trata)',
     'la forma «no se trata de X, es Y»'),
    (r'\bah[íi] es donde entra\b', '«ahí es donde entra X»'),
    (r'\bya sea que\b', '«ya sea que X o Y»'),
    (r'\b(?:dec[íi]le|dec[íi]|dile|di) adi[óo]s a\b', '«decile adiós a»'),
    (r'\bimagin[áa] (?:un|una|el|la|por un momento)\b', 'el arranque «imaginá un…»'),
    (r'¿\s*(?:el|la|lo)\s+(?:resultado|respuesta|clave|consecuencia|mejor)\s*\?',
     'pregunta que el propio texto contesta'),
    (r'\bcabe (?:destacar|señalar|mencionar)\b|\bes importante (?:señalar|destacar|notar)\b'
     r'|\bvale la pena mencionar\b', 'carraspeo antes de la idea'),
    (r'\bte ayuda a\b|\bpuede ayudar(?:te|lo|la) a\b', 'beneficio con pinzas'),
    (r'\bpodría potencialmente\b|\bquizás posiblemente\b|\bpuede llegar a poder\b',
     'dudas apiladas'),
    (r'\bal siguiente nivel\b', '«llevá tu X al siguiente nivel»'),
    (r'\btodo lo que necesit[áa]s saber\b', '«todo lo que necesitás saber sobre»'),
    (r'\ben un mundo cada vez más\b', 'arranque de posteo genérico'),
    (r'\bdescubr[íie] cómo\b', '«descubrí cómo»'),
]

# La raya al modo inglés: sin espacio de ninguno de los dos lados. En español el
# inciso abre con espacio afuera y cierra con espacio afuera, así que pegada de
# los dos lados es calco directo.
#
# Con una excepción que el corpus enseñó, y que valía el 1,5% de los textos
# humanos: cuando el inciso cierra al final de la oración, la puntuación va
# pegada afuera de la raya — «de gobierno corporativo —en ese orden—.». Eso es
# español correcto, así que ni la puntuación de cierre ni la de apertura cuentan
# como «palabra pegada».
RAYA_INGLESA = re.compile(r'[^\s(¡¿“"\[]—[^\s.,;:!?)\]”"]')

# Dos rayas en una oración es lo NORMAL en español: una abre el inciso y la otra
# lo cierra. El umbral está en cuatro, que ya son dos incisos apilados.
RAYAS_POR_ORACION = 4

# Tres ítems donde el tercero cierra la cláusula Y la enumeración abre la oración.
#
# Esa segunda condición la enseñó el corpus. En español `X, Y y Z` es simplemente
# cómo se enumeran tres cosas, y la forma sola no distingue un tricolon retórico
# de una lista común: sobre prensa rioplatense pre-2023 marcaba el 7,8% de las
# notas con cosas como «políticos, empresarios y periodistas». El tricolon de
# copy abre la oración — `Rápido, simple y confiable.` —, la enumeración de una
# nota va enganchada adentro de una frase más larga. Los ítems además tienen que
# arrancar con letra, que es lo que deja afuera «2010, 2011 y 2012».
RITMO = re.compile(
    r'(?:^|(?<=[.!?])\s+)'
    r'([^\W\d]\w{3,}),\s+([^\W\d]\w{3,})\s+[ye]\s+([^\W\d]\w{3,})\s*[.!?,;:\n]',
    re.M)

# Prueba inventada. Dos cosas la definen, y el corpus enseñó la segunda.
#
# La primera es el número escrito como se escribe en español: el punto separa los
# miles y la coma es el decimal. El patrón en inglés lee `10,000` y acá no vería
# nada.
#
# La segunda es el marco de venta. Un número al lado de un sustantivo de persona
# NO alcanza: un diario cuenta gente todo el tiempo, y sobre prensa rioplatense
# pre-2023 la versión sin marco marcaba el 3,5% de las notas con frases como
# «concurrían unos 250 estudiantes». Lo que convierte al número en prueba es el
# marco que lo rodea: un signo +, un adjetivo de campaña, un posesivo, o un verbo
# que dice que esa gente ya eligió.
_NUMERO = r'(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?'
_PERSONA = (r'(?:usuarios?|clientes?|alumnos?|estudiantes?|equipos?|miembros?'
            r'|empresas?|negocios?|propietarios?|suscriptores?|pacientes?'
            r'|lectores?|marcas?|profesionales?|personas?|familias?|emprendedores?)')
_CAMPANA = r'(?:felices|satisfech[oa]s|activos|verificados|contentos|encantados)'
_YA_ELIGIERON = (r'(?:ya\b|confían|nos eligen|nos eligieron|eligieron|se sumaron'
                 r'|nos acompañan|nos prefieren)')

PRUEBA = re.compile(
    r'\+\s?' + _NUMERO + r'\s*' + _PERSONA + r'(?!\w)'
    r'|' + _NUMERO + r'\s*\+\s*' + _PERSONA + r'(?!\w)'
    r'|' + _NUMERO + r'\s*(?:\w+\s+)?' + _PERSONA + r'\s+' + _CAMPANA + r'(?!\w)'
    r'|(?:nuestros?|nuestras?)\s+' + _NUMERO + r'\s*' + _PERSONA + r'(?!\w)'
    r'|' + _NUMERO + r'\s*' + _PERSONA + r'\s+' + _YA_ELIGIERON,
    re.I)

SUPERLATIVOS = [
    (r'\b(?:los|las) más (?:confiables?|elegid[oa]s|vendid[oa]s|complet[oa]s'
     r'|recomendad[oa]s|buscad[oa]s|usad[oa]s|valorad[oa]s)\b',
     'superlativo que nadie puede chequear'),
    # `del` y `de la` salieron: cazaban `el líder de la asociación bancaria`, que
    # es una persona. Marcaba el 4,9% de la prensa humana.
    (r'\bl[íi]der(?:es)? en\b', '«líderes en»'),
    (r'\bla mejor opción\b|\bel más completo\b|\bla más completa\b',
     'superlativo que nadie puede chequear'),
    (r'\bnúmero uno (?:en|del)\b', '«número uno en»'),
]


def _ventanas(texto, ancho=220):
    """Las oraciones del texto, cortadas en ventanas de ancho fijo.

    El límite hace trabajo real. El texto de interfaz no tiene puntos: los ítems
    de menú, los botones y las etiquetas corren todos juntos, así que un corte
    ingenuo de oraciones trata la página entera como una sola oración y las
    reglas de densidad disparan sobre todo. Un linter que llora lobo se apaga.
    """
    for oracion in re.split(r'(?<=[.!?])\s+|\n', texto):
        for i in range(0, max(1, len(oracion)), ancho):
            yield oracion[i:i + ancho]


def auditar(texto, trato='vos'):
    hallazgos = {'slop': dict((g, []) for g in GRUPOS_SLOP),
                 'registro': dict((g, []) for g in GRUPOS_REGISTRO)}
    slop = hallazgos['slop']
    bajo = texto.lower()

    for palabra in LEXICO_RAIZ:
        n = len(re.findall(_patron_raiz(palabra), bajo))
        if n:
            slop['lexico'].append((palabra, n))
    for frase in LEXICO_EXACTO:
        n = len(re.findall(r'(?<!\w)%s(?!\w)' % re.escape(frase), bajo))
        if n:
            slop['lexico'].append((frase, n))
    for patron, etiqueta in LEXICO_PATRON:
        n = len(re.findall(patron, bajo))
        if n:
            slop['lexico'].append((etiqueta, n))

    for patron, etiqueta in CONSTRUCCIONES:
        n = len(re.findall(patron, bajo))
        if n:
            slop['construcciones'].append((etiqueta, n))

    for ventana in _ventanas(texto):
        if RAYA_INGLESA.search(ventana):
            slop['cadencia'].append(('raya al modo inglés, sin espacios',
                                     ventana[:70].strip()))
            break
    for ventana in _ventanas(texto):
        if ventana.count('—') >= RAYAS_POR_ORACION:
            slop['cadencia'].append(('%d rayas en una misma oración' % ventana.count('—'),
                                     ventana[:70].strip()))
            break
    for m in RITMO.finditer(texto):
        slop['ritmo'].append(('ritmo de tres', m.group(0)[:60].strip()))

    for m in PRUEBA.finditer(texto):
        slop['venta'].append(m.group(0).strip())
    for patron, etiqueta in SUPERLATIVOS:
        for m in re.finditer(patron, bajo):
            slop['venta'].append('%s: «%s»' % (etiqueta, m.group(0)))

    _auditar_registro(texto, hallazgos['registro'], trato)
    return hallazgos


# ── trato: vos, tú o usted ───────────────────────────────────────────────────

# `te` NO está en la lista de vos: es el pronombre del voseo. `vos te vas` es
# rioplatense perfecto, y meterlo dejaría marcado casi todo texto bien escrito.
# Las terminaciones son solo `-áis` y `-éis`. `-ís` tampoco entra, porque
# `vivís`, `salís` y `escribís` son voseo antes que vosotros.
PRONOMBRES = [
    (r'(?<!\w)tú(?!\w)', '«tú» en vez de «vos»'),
    (r'(?<!\w)ti(?!\w)', '«ti» en vez de «vos»'),
    (r'(?<!\w)contigo(?!\w)', '«contigo» en vez de «con vos»'),
    (r'(?<!\w)vosotr[oa]s(?!\w)', '«vosotros»'),
    (r'(?<!\w)os(?!\w)', '«os» como pronombre'),
    (r'(?<!\w)vuestr[oa]s?(?!\w)', '«vuestro»'),
    (r'\w+[áé]is(?!\w)', 'conjugación de vosotros'),
]

# Imperativos de tuteo con el pronombre pegado. El enclítico y la tilde en la
# raíz no dejan lugar a dudas: `regístrate` es tuteo, `registrate` es voseo, y
# la única diferencia entre los dos es el acento escrito.
ENCLITICOS_TUTEO = [
    'regístrate', 'suscríbete', 'únete', 'apúntate', 'inscríbete',
    'contáctanos', 'escríbenos', 'llámanos', 'síguenos', 'conócenos',
    'pruébalo', 'pruébala', 'descúbrelo', 'descúbrela', 'míralo', 'míranos',
    'compártelo', 'descárgalo', 'inténtalo', 'hazlo', 'elígelo', 'cuéntame',
    'cuéntanos', 'dime', 'dinos', 'úsalo', 'llévatelo', 'agéndalo',
]

# Verbos de copy en tuteo. Solo se marcan en posición de llamada a la acción,
# porque `prueba` y `conoce` son también tercera persona del indicativo y
# sustantivo: «el equipo conoce el rubro», «la prueba de carga».
VERBOS_CTA = [
    'descubre', 'prueba', 'conoce', 'elige', 'empieza', 'comienza', 'solicita',
    'agenda', 'reserva', 'descarga', 'contacta', 'aprende', 'consigue',
    'obtén', 'compra', 'explora', 'accede', 'ingresa', 'calcula', 'mira',
    'suscribe', 'registra', 'comparte', 'encuentra', 'suma',
]

# Lo que sigue al verbo cuando NO es una llamada a la acción: `prueba de carga`,
# `descarga del informe`. Un sustantivo arrastra su complemento; un botón no.
TRAS_SUSTANTIVO = ('de', 'del', 'que', 'para', 'en', 'con', 'por')

# Largo máximo de un renglón para considerarlo posición de botón o título. Una
# oración corrida que arranca con `Conoce` es tercera persona, no un botón.
LARGO_CTA = 60

PENINSULAR = [
    (r'(?<!\w)ordenador(?:es)?(?!\w)', '«ordenador» por «computadora»'),
    # Con determinante: `el móvil` es el teléfono, pero `app móvil` y `unidad
    # móvil` son de uso corriente acá y no son tell de nada.
    (r'(?<!\w)(?:el|un|los|unos|mi|tu|su) móvil(?:es)?(?!\w)', '«móvil» por «celular»'),
    (r'(?<!\w)coger(?!\w)', '«coger» por «agarrar» o «tomar»'),
    (r'(?<!\w)zumo(?!\w)', '«zumo» por «jugo»'),
    (r'(?<!\w)gafas(?!\w)', '«gafas» por «lentes» o «anteojos»'),
    (r'(?<!\w)aparcar(?!\w)', '«aparcar» por «estacionar»'),
    (r'(?<!\w)chaval(?:es)?(?!\w)', '«chaval»'),
    # `vale` solo como muletilla: arranca la oración y cierra con coma o punto.
    # `¿cuánto vale?` y `vale la pena` son español de acá y no se tocan.
    (r'(?:^|(?<=[.!?])\s+)vale\s*[,.]', '«vale» como muletilla'),
]

# Formas que solo existen en voseo. Son las que se cuelan cuando el texto está
# en tú o en usted. Van enteras y no por terminación: `-ás` caza también `más`,
# `además` y `jamás`, y `-és` caza `después` e `inglés`.
VOSEO = [
    'vos', 'sos', 'tenés', 'podés', 'querés', 'sabés', 'hacés', 'ponés', 'decís',
    'venís', 'necesitás', 'buscás', 'pensás', 'contás', 'empezás', 'preferís',
    'elegís', 'pedís', 'seguís', 'conseguís', 'encontrás', 'volvés', 'llegás',
    'mirá', 'probá', 'descubrí', 'conocé', 'elegí', 'empezá', 'reservá', 'agendá',
    'descargá', 'comprá', 'pedí', 'dejá', 'hacé', 'tené', 'vení', 'aprovechá',
    'sumate', 'registrate', 'suscribite', 'animate', 'escribinos', 'contactanos',
    'llamanos', 'seguinos', 'contanos', 'decinos', 'consultanos',
]

TRATOS = ('vos', 'tu', 'usted')


def _cta_de_tuteo(bajo):
    for renglon in bajo.split('\n'):
        renglon = renglon.strip()
        if not renglon or len(renglon) > LARGO_CTA:
            continue
        palabras = re.findall(r'[\wáéíóúñü]+', renglon)
        if not palabras or palabras[0] not in VERBOS_CTA:
            continue
        if len(palabras) > 1 and palabras[1] in TRAS_SUSTANTIVO:
            continue                      # `prueba de carga`: sustantivo, no botón
        yield palabras[0]


def _auditar_registro(texto, registro, trato='vos'):
    """Lo que no corresponde al trato elegido.

    Vos es el default porque el proyecto nació para copy rioplatense, y porque
    ahí el problema es el más grave: la IA escribe en tú por defecto y un lector
    de Buenos Aires o Montevideo lo nota en la primera línea. Tú y usted
    marcan lo contrario, que es el mismo error visto desde el otro lado: un
    texto que empezó hablándole de una forma y en algún párrafo cambió.
    """
    bajo = texto.lower()

    def contar(lista_patrones, grupo):
        for patron, etiqueta in lista_patrones:
            n = len(re.findall(patron, bajo, re.M))
            if n:
                registro[grupo].append((etiqueta, n))

    if trato in ('vos', 'usted'):
        pronombres = PRONOMBRES if trato == 'vos' else PRONOMBRES[:3] + [
            (r'(?<!\w)tus?(?!\w)', '«tu» en un texto de usted'),
            (r'(?<!\w)te(?!\w)', '«te» en un texto de usted')]
        contar(pronombres, 'pronombres')
        for forma in ENCLITICOS_TUTEO:
            n = len(re.findall(r'(?<!\w)%s(?!\w)' % re.escape(forma), bajo))
            if n:
                registro['imperativos'].append(('%s (imperativo de tuteo)' % forma, n))
        for verbo in _cta_de_tuteo(bajo):
            registro['imperativos'].append(
                ('%s (imperativo de tuteo en posición de botón)' % verbo, 1))

    if trato in ('tu', 'usted'):
        for forma in VOSEO:
            n = len(re.findall(r'(?<!\w)%s(?!\w)' % re.escape(forma), bajo))
            if n:
                registro['imperativos'].append(('«%s» es voseo' % forma, n))

    if trato == 'vos':
        contar(PENINSULAR, 'lexico_peninsular')


def grupos_de_ia(hallazgos, permitir_prueba=False):
    """Los grupos de señales de IA que el texto tocó."""
    return [g for g in GRUPOS_SLOP
            if hallazgos['slop'][g] and not (permitir_prueba and g == 'venta')]


# ── 1. sin completar ─────────────────────────────────────────────────────────

# Lo que quedó de la plantilla. Cualquiera de estos en producción es un texto que
# no se terminó, y ninguno necesita criterio: un `[Nombre]` es un `[Nombre]`.
MARCADORES = [
    # Lo que el propio skill deja cuando no tiene el dato. Siempre cuenta.
    (r'(?i)\[falta dato[^\[\]\n]*\]', 'falta dato'),
    # Corchetes de plantilla: `[Nombre]`, `[precio]`, `[Escribinos por WhatsApp]`.
    # La prensa también usa corchetes, para aclarar adentro de una cita: «le dijo
    # [a Rusia] que…». Esos van en minúscula o con espacios, y no nombran un
    # campo, así que un corchete marca solo si arranca en mayúscula y es corto, o
    # si adentro hay una palabra de formulario. `[1]` es una nota y no marca.
    (r'\[(?:[A-ZÁÉÍÓÚÑ][^\[\]\n ]*(?: [^\[\]\n ]+){0,3}'
     r'|[^\[\]\n]{0,20}\b(?:nombre|precio|fecha|hora|barrio|ciudad|email|mail|correo'
     r'|teléfono|telefono|dirección|direccion|link|url|enlace|cifra|número|numero|monto'
     r'|dato|empresa|producto|logo|foto|imagen|falta|año|zona|horario|matrícula|cuit|link)\b[^\[\]\n]{0,20})\]',
     'corchete de plantilla'),
    (r'\{\{[^{}\n]{1,60}\}\}|\{[a-z_]{2,30}\}', 'variable de plantilla'),
    (r'(?i)\blorem ipsum\b|\bdolor sit amet\b', 'lorem ipsum'),
    # `siglo XX` es historia, no un hueco.
    (r'(?<![Ss]iglo )(?<!el )(?<![\w-])(?:XX+|xxx+)(?![\w-])', 'XX en lugar de un dato'),
    (r'\b(?:TODO|TBD|PENDIENTE|COMPLETAR|INSERTAR)\b', 'nota interna'),
    (r'(?i)\b(?:insertar|completar|agregar|poner) (?:aquí|acá|aca|aqui)\b', 'nota interna'),
    (r'(?i)\b(?:texto|título|titulo|imagen|nombre) de ejemplo\b', 'texto de ejemplo'),
    (r'(?i)\bnombre (?:apellido|del cliente|de la empresa|de tu empresa)\b', 'nombre genérico'),
    (r'(?i)[\w.+-]+@(?:ejemplo|example|tuempresa|tudominio|dominio|empresa|correo|email|mail)'
     r'\.(?:com|net|org)(?:\.[a-z]{2})?\b', 'mail de ejemplo'),
    (r'(?i)\b(?:www\.)?(?:ejemplo|example|tusitio|tudominio|tuempresa|misitio)\.com\b',
     'dominio de ejemplo'),
    (r'\b(?:1234[- ]?5678|123[- ]?456[- ]?789|0{4}[- ]?0{4})\b', 'teléfono de ejemplo'),
    (r'(?i)\bcalle falsa\b', 'dirección de ejemplo'),
]


# Verbos con los que arranca un botón escrito en un documento de copy.
BOTONES = set(VERBOS_CTA + ENCLITICOS_TUTEO + VOSEO + [
    'ver', 'buscar', 'comprar', 'enviar', 'empezar', 'reservar', 'agendar', 'solicitar',
    'descargar', 'contactar', 'llamar', 'suscribirme', 'quiero', 'saber', 'conocer',
    'probar', 'pedir', 'crear', 'iniciar', 'ingresar', 'registrarme', 'unirme'])


def _es_boton(fragmento):
    """`[Pedí tu turno]` es cómo un documento de copy escribe un botón.

    No es un hueco: el texto del botón ya está escrito. Lo que lo delata es que
    arranca con un imperativo, que en voseo lleva tilde (`Pedí`, `Reservá`) o
    un pronombre pegado (`Escribinos`, `Sumate`).
    """
    primera = (re.findall(r'[\wáéíóúñü]+', fragmento.lower()) or [''])[0]
    return primera in BOTONES or bool(re.match(r'^\w+[áéí](?:te|me|nos|lo|la)?$', primera))


def sin_completar(texto, html=None):
    """Cada hueco de plantilla, como (etiqueta, fragmento)."""
    huecos, tomados = [], []
    for patron, etiqueta in MARCADORES:
        for m in re.finditer(patron, texto):
            if etiqueta == 'corchete de plantilla' and _es_boton(m.group(0)):
                continue
            # `ejemplo.com` adentro de `hola@ejemplo.com` es el mismo hueco.
            if any(a <= m.start() and m.end() <= b for a, b in tomados):
                continue
            tomados.append(m.span())
            falta = m.group(0).lower().startswith('[falta dato')
            huecos.append(('falta dato' if falta else etiqueta, m.group(0)))
    if html is not None:
        vacios = len(re.findall(r'<a\b[^>]*\bhref\s*=\s*["\'](?:#?)["\']', html, re.I))
        if vacios:
            huecos.append(('enlace que no lleva a ningún lado', '%d con href="#"' % vacios))
    return huecos


def _puntaje_sin_completar(huecos):
    # Uno solo ya impide publicar, por eso arranca en 6 y no en 9.
    return 10 if not huecos else max(1, 7 - len(huecos))


# ── 2. especificidad ─────────────────────────────────────────────────────────

# Lo que un competidor no podría copiar tal cual: cifras, precios, plazos,
# fechas, lugares, nombres. La prueba de fondo es cambiar el nombre del negocio
# por el de la competencia: si la oración sigue siendo verdad, es genérica.
CONCRETOS = re.compile(
    r'(?:US\$|\$|USD|ARS|UYU|€)\s?\d+(?:[.,]\d+)*'
    r'|\d+(?:[.,]\d+)*\s?%'
    r'|\d{1,2}(?::\d{2})?\s?(?:hs|h)\b'
    r'|\d+(?:(?:[.,-]|\s(?=\d{3}))\d+)*(?:\s?(?:minutos?|horas?|días?|semanas?|meses|mes|años?|km|metros?|m2|m²'
    r'|kg|kilos?|gramos?|cuotas?|unidades?|litros?|cm))?'
    r'|\b(?:lunes|martes|miércoles|jueves|viernes|sábados?|domingos?)\b'
    r'|\b(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre'
    r'|octubre|noviembre|diciembre)\b', re.I)

# Un nombre propio en mitad de oración: un barrio, una marca, una persona.
PROPIO = re.compile(r'(?<=[a-záéíóúñ,] )[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}[A-Za-záéíóúñ]*'
                    r'(?:\s+(?:de\s+|del\s+)?[A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ]+)*')

# Frases que cualquier negocio de cualquier rubro podría firmar.
GENERICOS = [
    r'\b(?:de|alta|máxima|excelente|la mejor) calidad\b',
    r'\bexcelencia\b', r'\bcompromiso con\b', r'\binnovador(?:a|es|as)?\b',
    r'\bsoluciones(?: integrales| innovadoras| a medida| personalizadas| efectivas)?\b',
    r'\batención personalizada\b', r'\b(?:tus|sus) necesidades\b',
    r'\bamplia experiencia\b', r'(?<!\d )\baños de experiencia\b',
    r'\bequipo de (?:profesionales|expertos)\b', r'\bprofesionales (?:altamente )?calificados\b',
    r'\bservicio integral\b', r'\bnos apasiona\b', r'\bcon pasión\b', r'\bvalor agregado\b',
    r'\bresultados (?:excepcionales|extraordinarios|reales|increíbles)\b',
    r'\bla mejor experiencia\b', r'\bde (?:manera|forma) (?:eficiente|eficaz|sencilla|rápida)\b',
    r'\b(?:fácil y rápido|rápido y fácil|rápida y sencilla|simple y rápido)\b',
    r'\bmejorar tu (?:negocio|empresa|vida)\b', r'\bllev(?:ar|á) tu (?:negocio|marca|empresa)\b',
]


def _renglon_de_titulo(renglon):
    """Un título escrito con Mayúscula En Cada Palabra, como en inglés.

    En español solo va mayúscula la primera palabra y los nombres propios. La IA
    traduce el título en inglés y deja las mayúsculas: `Nuestros Servicios
    Profesionales`.
    """
    palabras = renglon.split()
    if not 2 <= len(palabras) <= 10 or renglon.rstrip()[-1:] in '.:;,':
        return False
    # Con coma es casi siempre una lista de nombres propios: `Veterinaria Los
    # Plátanos, en General Paz, Córdoba`. Un título calcado del inglés no la lleva.
    if ',' in renglon:
        return False
    llenas = [p for p in palabras[1:] if len(p) > 3 and p[0].isalpha()]
    return len(llenas) >= 2 and all(p[0].isupper() and not p.isupper() for p in llenas)


def especificidad(texto):
    """(concretos, genéricos), cada uno una lista de fragmentos."""
    prosa = '\n'.join(r for r in texto.split('\n') if not _renglon_de_titulo(r))
    # Una cifra de clientes inventada no es un dato: es lo contrario.
    prosa = PRUEBA.sub(' ', prosa)
    concretos = [m.group(0) for m in CONCRETOS.finditer(prosa)]
    concretos += [m.group(0) for m in PROPIO.finditer(prosa)]
    bajo = texto.lower()
    genericos = []
    for patron in GENERICOS:
        genericos += [m.group(0) for m in re.finditer(patron, bajo)]
    for patron, _ in SUPERLATIVOS:
        genericos += [m.group(0) for m in re.finditer(patron, bajo)]
    # Un dato repetido no es más específico: el mismo teléfono tres veces es un dato.
    return _sin_repetir(concretos), genericos


def _sin_repetir(items):
    vistos, unicos = set(), []
    for item in items:
        if item.lower() not in vistos:
            vistos.add(item.lower())
            unicos.append(item)
    return unicos


def _puntaje_especificidad(concretos, genericos, palabras):
    """Datos concretos netos cada 100 palabras, llevados a 1-10.

    Cada frase genérica resta un dato: una promesa vacía le saca lugar a una
    verificable. El corte en 3 por cada 100 palabras es una landing donde casi
    cada párrafo trae algo que se puede chequear.
    """
    densidad = (len(concretos) - len(genericos)) * 100.0 / max(palabras, 1)
    for corte, puntaje in ((4, 10), (3, 9), (2, 8), (1.5, 7), (1, 6), (0.5, 5), (0, 4), (-1, 3)):
        if densidad >= corte:
            return puntaje
    return 2


# ── 3. correcto y completo ───────────────────────────────────────────────────

def _oraciones(texto):
    return [o.strip() for o in re.split(r'(?<=[.!?…])\s+|\n', texto) if o.strip()]


def correccion(texto, registro):
    """Errores que se pueden marcar sin criterio, como (etiqueta, ejemplo).

    Ortografía fina, datos que se contradicen y lo que le falta al formato los
    juzga el skill: un regex no sabe si una landing de abogados necesita la
    matrícula.
    """
    errores = []
    for grupo in GRUPOS_REGISTRO:
        if registro[grupo]:
            errores.append((TITULOS[grupo], ', '.join(e for e, _ in registro[grupo][:3])))

    for cierre, apertura, nombre in (('?', '¿', 'pregunta sin «¿»'),
                                     ('!', '¡', 'exclamación sin «¡»')):
        for oracion in _oraciones(texto):
            if oracion.count(cierre) > oracion.count(apertura):
                errores.append((nombre, oracion[:70]))
                break

    # Solo palabras de enlace. `yira yira` y `fiu fiu` se repiten a propósito;
    # `de de` no se repite nunca a propósito.
    m = re.search(r'(?i)(?<!\w)(de|la|el|los|las|que|en|es|un|una|con|por|para|se|lo|del'
                  r'|al|no|y|a)[ \t]+\1(?!\w)', texto)
    if m:
        errores.append(('palabra repetida', m.group(0)))

    for renglon in texto.split('\n'):
        if _renglon_de_titulo(renglon):
            errores.append(('Mayúsculas En Cada Palabra, como en inglés', renglon[:70]))
            break

    return errores


def _puntaje_correccion(errores):
    # El trato cuenta doble: un cambio de vos a tú lo nota cualquier lector.
    pesos = sum(2 if e in TITULOS.values() else 1 for e, _ in errores)
    return max(1, 10 - pesos)


# ── 4. suena humano ──────────────────────────────────────────────────────────

def cadencia_pareja(texto):
    """Todas las oraciones del mismo largo. Una persona alterna sin pensarlo."""
    largos = [len(o.split()) for o in _oraciones(texto) if len(o.split()) >= 3]
    if len(largos) < 8:
        return False
    media = sum(largos) / float(len(largos))
    desvio = (sum((x - media) ** 2 for x in largos) / len(largos)) ** 0.5
    return desvio / media < 0.35


def _puntaje_humano(hallazgos, pareja, permitir_prueba):
    return max(1, 10 - 2 * len(grupos_de_ia(hallazgos, permitir_prueba)) - (1 if pareja else 0))


# ── 5. hecho para el formato ─────────────────────────────────────────────────

FORMATOS = ('web', 'blog', 'linkedin', 'instagram', 'post')

TITULOS_VACIOS = ('inicio', 'home', 'document', 'untitled', 'sin título', 'mi sitio',
                  'página principal', 'react app', 'vite app')


def _controles_html(html):
    fallas = []
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
    titulo = normalizar(_html.unescape(re.sub(r'<[^>]+>', '', m.group(1)))) if m else ''
    if not titulo:
        fallas.append('la página no tiene <title>: es lo que Google muestra como título')
    elif titulo.lower() in TITULOS_VACIOS:
        fallas.append('el <title> es «%s», no describe la página' % titulo)
    if not re.search(r'<meta\b[^>]*name\s*=\s*["\']description["\'][^>]*content\s*=\s*["\']\s*\S',
                     html, re.I) and \
       not re.search(r'<meta\b[^>]*content\s*=\s*["\']\s*\S[^>]*name\s*=\s*["\']description["\']',
                     html, re.I):
        fallas.append('falta la meta descripción: Google arma el resumen con lo que encuentre')
    h1 = len(re.findall(r'<h1\b', html, re.I))
    if h1 != 1:
        fallas.append('hay %d <h1>; lo claro es uno solo, con el tema de la página' % h1)
    sin_alt = [t for t in re.findall(r'<img\b[^>]*>', html, re.I) if not re.search(r'\balt\s*=', t, re.I)]
    if sin_alt:
        fallas.append('%d imágenes sin atributo alt' % len(sin_alt))
    if not re.search(r'<html\b[^>]*\blang\s*=\s*["\']es', html, re.I):
        fallas.append('falta lang="es" en <html>: lectores de pantalla y buscadores lo usan')
    niveles = [int(n) for n in re.findall(r'<h([1-6])\b', html, re.I)]
    for antes, despues in zip(niveles, niveles[1:]):
        if despues > antes + 1:
            fallas.append('los títulos saltan de h%d a h%d' % (antes, despues))
            break
    return fallas


def _parrafos(md):
    return [p for p in re.split(r'\n\s*\n', md)
            if p.strip() and not re.match(r'\s*(?:#|[-*+] |\d+\. |>|```|\|)', p)]


def _controles_markdown(md, formato):
    fallas = []
    cuerpo = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.S)
    frente = md[:len(md) - len(cuerpo)]
    h1 = len(re.findall(r'^#\s', cuerpo, re.M)) + (1 if re.search(r'^title:', frente, re.M) else 0)
    if h1 != 1:
        fallas.append('hay %d títulos principales (# o title:); lo claro es uno solo' % h1)
    palabras = len(cuerpo.split())
    if formato == 'blog':
        if palabras >= 600 and len(re.findall(r'^##\s', cuerpo, re.M)) < 2:
            fallas.append('%d palabras con menos de dos subtítulos (##): '
                          'nadie encuentra lo que busca' % palabras)
        if frente and not re.search(r'^description:\s*\S', frente, re.M):
            fallas.append('el front matter no tiene description: la meta descripción queda vacía')
        parrafos = _parrafos(cuerpo)
        largos = [p for p in parrafos if len(p.split()) > 150]
        if largos:
            fallas.append('%d párrafos de más de 150 palabras' % len(largos))
        if parrafos and len(parrafos[0].split()) > 80:
            fallas.append('el primer párrafo tiene %d palabras: la respuesta tarda en llegar'
                          % len(parrafos[0].split()))
    return fallas


# Los límites duros son los oficiales de cada red. Los cortes del «ver más» no
# están publicados y cambian con el dispositivo: son el corte habitual medido.
REDES = {
    'linkedin': {'largo': 3000, 'gancho': 210, 'hashtags': None},
    'instagram': {'largo': 2200, 'gancho': 125, 'hashtags': 5},
    'post': {'largo': 2200, 'gancho': 125, 'hashtags': 5},
}


def _controles_red(texto, formato):
    regla = REDES[formato]
    fallas = []
    if len(texto) > regla['largo']:
        fallas.append('%d caracteres; %s corta en %d' % (len(texto), formato, regla['largo']))
    gancho = texto.split('\n', 1)[0]
    if len(gancho) > regla['gancho']:
        fallas.append('la primera línea tiene %d caracteres y el «ver más» corta cerca de %d: '
                      'el gancho queda escondido' % (len(gancho), regla['gancho']))
    hashtags = re.findall(r'(?<![\w&])#[^\W\d_][\w]*', texto)
    if regla['hashtags'] and len(hashtags) > regla['hashtags']:
        fallas.append('%d hashtags; Instagram permite %d' % (len(hashtags), regla['hashtags']))
    bloques = [b for b in texto.split('\n') if len(b) > 300]
    if bloques:
        fallas.append('%d bloques de más de 300 caracteres sin cortar: en el celular es una pared'
                      % len(bloques))
    return fallas


def controles_de_formato(texto, crudo, formato, es_html):
    if formato in REDES:
        return _controles_red(texto, formato)
    if es_html:
        return _controles_html(crudo)
    return _controles_markdown(crudo, formato)


def adivinar_formato(ruta, crudo, texto):
    if ruta and re.search(r'\.html?$', ruta, re.I):
        return 'web'
    if re.search(r'^#{1,3}\s', crudo or '', re.M) or len(texto.split()) >= 300:
        return 'blog'
    return 'post'


# ── puntaje general y reporte ────────────────────────────────────────────────

TITULOS = {
    'lexico': 'léxico de IA',
    'construcciones': 'construcciones de IA',
    'cadencia': 'cadencia de puntuación',
    'ritmo': 'ritmo de tres',
    'venta': 'venta y prueba inventada',
    'pronombres': 'pronombres que no van con el trato',
    'imperativos': 'imperativos que no van con el trato',
    'lexico_peninsular': 'léxico peninsular',
}

NOMBRES = [
    ('sin_completar', 'Sin completar'),
    ('especificidad', 'Especificidad'),
    ('correccion', 'Correcto y completo'),
    ('humano', 'Suena humano'),
    ('formato', 'Hecho para el formato'),
]

TOPE = 6


def evaluar(texto, crudo=None, formato='post', es_html=False, trato='vos',
            permitir_prueba=False):
    """Los cinco puntajes, la evidencia de cada uno y el general con tope."""
    crudo = texto if crudo is None else crudo
    hallazgos = auditar(texto, trato)
    palabras = len(texto.split())

    huecos = sin_completar(texto, crudo if es_html else None)
    concretos, genericos = especificidad(texto)
    errores = correccion(texto, hallazgos['registro'])
    pareja = cadencia_pareja(texto)
    fallas = controles_de_formato(texto, crudo, formato, es_html)

    puntajes = {
        'sin_completar': _puntaje_sin_completar(huecos),
        'especificidad': _puntaje_especificidad(concretos, genericos, palabras),
        'correccion': _puntaje_correccion(errores),
        'humano': _puntaje_humano(hallazgos, pareja, permitir_prueba),
        'formato': max(1, 10 - 2 * len(fallas)),
    }
    promedio = sum(puntajes.values()) / 5.0

    prueba = bool(PRUEBA.search(texto)) and not permitir_prueba
    motivos = []
    if huecos:
        motivos.append('hay cosas sin completar')
    if prueba:
        motivos.append('hay prueba que parece inventada')
    general = min(promedio, TOPE) if motivos else promedio

    humano = []
    for grupo in grupos_de_ia(hallazgos, permitir_prueba):
        for item in hallazgos['slop'][grupo][:4]:
            humano.append((TITULOS[grupo], item[0] if isinstance(item, tuple) else item))
    if pareja:
        humano.append(('ritmo parejo', 'todas las oraciones tienen casi el mismo largo'))

    return {
        'palabras': palabras,
        'formato': formato,
        'trato': trato,
        'puntajes': puntajes,
        'promedio': round(promedio, 1),
        'general': round(general, 1),
        'tope': motivos,
        'evidencia': {
            'sin_completar': huecos,
            'especificidad': {'concretos': concretos, 'genericos': genericos},
            'correccion': errores,
            'humano': humano,
            'formato': fallas,
        },
    }


def _coma(numero):
    return ('%.1f' % numero).replace('.', ',').replace(',0', '')


def _resumen(clave, evidencia):
    e = evidencia[clave]
    if clave == 'especificidad':
        return '%d datos concretos, %d frases genéricas' % (len(e['concretos']), len(e['genericos']))
    if not e:
        return 'nada que marcar'
    return '%d para revisar' % len(e)


def reportar(r, nombre=''):
    print('Textosaurio · %s%s · %d palabras · trato: %s\n'
          % (nombre + ' · ' if nombre else '', r['formato'], r['palabras'], r['trato']))
    for i, (clave, titulo) in enumerate(NOMBRES, 1):
        print('  %d  %-22s %2d/10   %s' % (i, titulo, r['puntajes'][clave],
                                          _resumen(clave, r['evidencia'])))
    print('')
    if r['tope'] and r['promedio'] > TOPE:
        print('  GENERAL  %s/10  (el promedio da %s, pero %s: tope %d)'
              % (_coma(r['general']), _coma(r['promedio']), ' y '.join(r['tope']), TOPE))
    elif r['tope']:
        print('  GENERAL  %s/10  (no se puede publicar: %s)'
              % (_coma(r['general']), ' y '.join(r['tope'])))
    else:
        print('  GENERAL  %s/10' % _coma(r['general']))

    for i, (clave, titulo) in enumerate(NOMBRES, 1):
        e = r['evidencia'][clave]
        if clave == 'especificidad':
            lineas = (['concreto: %s' % c for c in e['concretos'][:6]] +
                      ['genérico: «%s»' % g for g in e['genericos'][:6]])
        else:
            lineas = [('%s: «%s»' % x) if isinstance(x, tuple) else x for x in e]
        if not lineas:
            continue
        print('\n── %d %s' % (i, titulo))
        for linea in lineas[:10]:
            print('   · %s' % linea)
        if len(lineas) > 10:
            print('   · …y %d más' % (len(lineas) - 10))


def leer_utf8(ruta):
    """Lee siempre como UTF-8, diga lo que diga el locale de la máquina.

    `open()` sin `encoding=` usa el del sistema. Un texto en UTF-8 leído como
    cp1252 convierte cada tilde en mojibake, y entonces `regístrate` deja de
    matchear y el control de trato queda mudo. Un gate que aprueba porque no
    supo leer es peor que no tener gate.
    """
    return open(ruta, encoding='utf-8', errors='replace').read()


USO = """textosaurio: cinco puntajes del 1 al 10 para un texto hecho con IA

  python3 textosaurio.py landing.html
  python3 textosaurio.py nota.md
  python3 textosaurio.py --texto "un borrador pegado acá"

  --formato F        web, blog, linkedin, instagram o post (si no, lo adivina)
  --trato T          vos (default), tu o usted
  --minimo N         sale con error si el general queda abajo de N (default 8)
  --permitir-prueba  tus cifras de clientes son reales y las podés mostrar
  --vista ID         puntúa solo un elemento de la página, por su id
  --json             el resultado en JSON, para otro programa
"""


def _valor(argv, bandera, validos=None):
    if bandera not in argv:
        return argv, None
    i = argv.index(bandera)
    if i + 1 >= len(argv) or (validos and argv[i + 1] not in validos):
        raise ValueError('%s necesita uno de: %s' % (bandera, ', '.join(validos or ['un valor'])))
    valor = argv[i + 1]
    return argv[:i] + argv[i + 2:], valor


def main(argv):
    if not argv:
        sys.stderr.write(USO)
        return 2
    try:
        argv, formato = _valor(argv, '--formato', FORMATOS)
        argv, trato = _valor(argv, '--trato', TRATOS)
        argv, minimo = _valor(argv, '--minimo')
        argv, vista = _valor(argv, '--vista')
        minimo = float(minimo.replace(',', '.')) if minimo else 8.0
    except ValueError as e:
        sys.stderr.write('textosaurio: %s\n' % e)
        return 2
    permitir_prueba = '--permitir-prueba' in argv
    como_json = '--json' in argv
    argv = [a for a in argv if a not in ('--permitir-prueba', '--json')]

    ruta = None
    if argv and argv[0] == '--texto':
        crudo = ' '.join(argv[1:])
    elif argv:
        ruta = argv[0]
        try:
            crudo = leer_utf8(ruta)
        except (IOError, OSError) as e:
            sys.stderr.write('textosaurio: no pude leer %s: %s\n' % (ruta, e.strerror))
            return 2
    else:
        sys.stderr.write(USO)
        return 2

    # La extensión manda. Un .md que habla de `<title>` sigue siendo markdown, y
    # leerlo como HTML dejaba adentro todos los ejemplos citados entre comillas.
    es_md = bool(ruta and re.search(r'\.mdx?$', ruta, re.I))
    es_html = bool(ruta and re.search(r'\.html?$', ruta, re.I)) or \
        (not es_md and bool(re.match(r'\s*<(?:!doctype|html|body|p|div|h1|section)\b', crudo, re.I)))
    if es_html:
        if vista:
            inicio = crudo.find('id="%s"' % vista)
            if inicio < 0:
                sys.stderr.write('textosaurio: no hay ningún elemento con id "%s"\n' % vista)
                return 2
            sigue = crudo.find('id="view-', inicio + 1)
            crudo = crudo[inicio:sigue if sigue > 0 else len(crudo)]
        texto = texto_visible(crudo)
    elif es_md or re.search(r'^#{1,6}\s', crudo, re.M):
        texto = prosa_markdown(re.sub(r'^---\n.*?\n---\n', '', crudo, flags=re.S))
    else:
        texto = normalizar(crudo)

    # Nada que puntuar es una falla, nunca un aprobado.
    if not texto.split():
        sys.stderr.write('textosaurio: no hay texto para puntuar, la entrada está vacía\n')
        return 2

    formato = formato or adivinar_formato(ruta, crudo, texto)
    if vista and formato == 'web':
        es_html = False               # un fragmento no tiene <title> ni <html>
        crudo = texto
    resultado = evaluar(texto, crudo, formato, es_html, trato or 'vos', permitir_prueba)

    if como_json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        reportar(resultado, os.path.basename(ruta) if ruta else '')
    return 0 if resultado['general'] >= minimo else 1


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main(sys.argv[1:]))
