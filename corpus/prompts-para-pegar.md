# Prompts para generar el corpus de IA a mano

Para cuando el modelo no tiene CLI instalado y hay que pasar por la web. Son los mismos
quince prompts que usa `construir.py`, así que los corpus quedan comparables.

## Las tres reglas

**No le pidas que escriba bien.** Nada de "que no suene a IA", "que suene natural", "en
rioplatense", "sin clichés". El corpus tiene que capturar lo que el modelo escribe **por
defecto**, que es lo que escribe la gente que lo usa sin pensar. Pedirle que evite los tells
es medir otra cosa.

**No edites lo que devuelve.** Ni los títulos, ni los botones, ni las viñetas. Copiá y pegá
tal cual, aunque te parezca malo. Sobre todo si te parece malo.

**Una conversación nueva por prompt.** Si encadenás los quince en el mismo chat, el modelo
arrastra el estilo del anterior y los quince textos salen parecidos entre sí. Eso arruina la
medición: quedarían quince muestras de una sola cosa en vez de quince muestras.

## Dónde guardar cada uno

```
corpus/ia/gpt-landing-00.txt
corpus/ia/gemini-landing-00.txt
```

El prefijo es el modelo, después el género y el número del prompt. Cuando termines:

```bash
python3 corpus/registrar.py --modelo "GPT-5.6 (web)"     # registra los que falten
python3 corpus/calibrar.py                               # vuelve a medir todo
python3 corpus/verificar_falsos_positivos.py
```

Mezclar modelos en el mismo corpus no es un problema: es mejor. El slop que te cruzás en la
calle no salió todo del mismo lado.

## Los prompts

A cada uno agregale al final: `Escribilo en español. Solo el texto.`

### landing

- `00` — Escribí el copy de una landing para una inmobiliaria en Montevideo.
- `01` — Escribí el copy de una landing para un estudio contable en Rosario.
- `02` — Escribí el copy de la home de una app de delivery uruguaya.
- `03` — Escribí el copy de una landing para una empresa de paneles solares.
- `04` — Escribí el copy de una landing para una clínica odontológica.

### posteo

- `00` — Escribí un posteo de blog sobre cómo elegir un proveedor de software.
- `01` — Escribí un artículo sobre el mercado inmobiliario uruguayo para un blog.
- `02` — Escribí una newsletter para clientes de una agencia de marketing.
- `03` — Escribí un posteo de blog sobre productividad para equipos remotos.
- `04` — Escribí un artículo sobre inteligencia artificial para un público general.

### producto

- `00` — Escribí el README de una librería de JavaScript para manejar fechas.
- `01` — Escribí la documentación de onboarding de una app de facturación.
- `02` — Escribí los textos de interfaz de un panel de control de una app de gestión.
- `03` — Escribí las notas de la versión 2.0 de una app de gestión de stock.
- `04` — Escribí la página de preguntas frecuentes de un servicio de hosting.

## Cuántos hacen falta

El criterio pide diez apariciones de un patrón en el corpus de IA para que el número
signifique algo. Con quince textos hay 10.471 palabras, y ni `potenciar` ni
`no solo X, sino Y` llegan a diez.

Treinta textos más — quince de GPT y quince de Gemini — llevan el corpus a unas 30.000
palabras. Ahí un patrón que aparezca tres veces cada 10.000 palabras ya cruza el mínimo, y
esa frecuencia es la que tienen los tells fuertes en copy generado. Si con 30.000 palabras
`potenciar` sigue sin aparecer, eso también es un resultado, y hay que escribirlo.
