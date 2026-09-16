# Controles de formato

Cada control que hace `tools/textosaurio.py`, y de dónde sale. Donde hay una regla
oficial, se cita. Donde no la hay, se dice.

Cada control que falla descuenta 2 puntos.

## Web (`.html`)

| Control | Fuente |
|---|---|
| Tiene `<title>` y no es «Inicio», «Home» o «Document» | Google: «Make sure every page on your site has a title specified in the `<title>` element» y «Avoid vague descriptors like "Home"». [Title links](https://developers.google.com/search/docs/appearance/title-link) |
| Tiene meta descripción | Google la usa para el resumen del resultado. No tiene límite de largo: se corta según el ancho del dispositivo. [Snippets](https://developers.google.com/search/docs/appearance/snippet) |
| Un solo `<h1>` | Práctica de claridad y accesibilidad, no una regla de Google. |
| Toda `<img>` tiene `alt` | Pauta WCAG 1.1.1 (texto alternativo). `alt=""` vale para imágenes decorativas. |
| `<html lang="es">` | Pauta WCAG 3.1.1 (idioma de la página). |
| Los títulos no saltan niveles (h2 → h4) | Práctica de accesibilidad. |

**Lo que no se controla, a propósito:** el largo del `<title>` y de la meta descripción.
Google no publica un límite. Los «60 caracteres» que circulan son una aproximación del
corte visual, no una regla.

## Blog (`.md`)

| Control | Fuente |
|---|---|
| Un solo título principal (`#` o `title:`) | Práctica de claridad. |
| Si tiene 600 palabras o más, al menos dos subtítulos `##` | Práctica de lectura en pantalla: quien busca una respuesta escanea. |
| Si tiene front matter, trae `description:` | Es la meta descripción en casi todos los generadores de sitios. |
| Ningún párrafo pasa las 150 palabras | Práctica de lectura en celular. |
| El primer párrafo no pasa las 80 palabras | Práctica: la respuesta tiene que llegar pronto. |

## LinkedIn

| Control | Fuente |
|---|---|
| Hasta 3.000 caracteres | Límite oficial. [Ayuda de LinkedIn](https://www.linkedin.com/help/linkedin/answer/a528176) |
| La primera línea no pasa los 210 caracteres | No oficial. Es el corte habitual del «ver más» en escritorio; en el celular corta antes. |
| Ningún bloque pasa los 300 caracteres sin salto de línea | Práctica de lectura en celular. |

## Instagram

| Control | Fuente |
|---|---|
| Hasta 2.200 caracteres | Límite oficial del texto de una publicación. |
| Hasta 5 hashtags | Oficial desde diciembre de 2025: Instagram limita a cinco los hashtags por publicación y reel. [Social Media Today](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/) |
| La primera línea no pasa los 125 caracteres | No oficial. Es el corte habitual del «más» en el feed. |
| Ningún bloque pasa los 300 caracteres sin salto de línea | Práctica de lectura en celular. |

## Post (sin formato definido)

Cuando el script no sabe si es LinkedIn o Instagram, aplica los límites más estrictos de
los dos: 2.200 caracteres, 125 en la primera línea y 5 hashtags.

Verificado el 16 de septiembre de 2026. Las redes cambian estas reglas seguido: si una
cambió, se actualiza acá y en `REDES` dentro del script.
