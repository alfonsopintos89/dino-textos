---
name: textosaurio
description: Revisa un texto en español hecho con IA (landing, blog, post de LinkedIn o Instagram) y le pone cinco puntajes del 1 al 10 (sin completar, especificidad, correcto y completo, suena humano, hecho para el formato) más un puntaje general. Después ofrece las recomendaciones y las aplica. Se dispara con /textosaurio, "revisá este texto", "puntuá esta landing", "esto suena a IA", "mejorá este copy".
---

# Textosaurio

Recibís un texto hecho con IA y devolvés cinco puntajes del 1 al 10, un puntaje general
y, si la persona quiere, el texto mejorado.

El objetivo no es engañar a un detector de IA. Es que el texto se pueda publicar: que no
le queden huecos, que diga cosas concretas, que esté bien escrito, que no suene a robot y
que funcione donde se va a publicar.

## Paso 1. Correr el script

```bash
python3 <carpeta de este skill>/tools/textosaurio.py ARCHIVO [--formato F] [--trato T]
```

- `ARCHIVO` puede ser `.html`, `.md` o `.txt`. Si la persona pegó el texto en el chat,
  usá `--texto "…"`.
- `--formato`: `web`, `blog`, `linkedin`, `instagram` o `post`. Si el pedido lo dice
  («esta landing», «mi post de LinkedIn»), pasalo. Si no, el script lo adivina.
- `--trato`: `vos` (default), `tu` o `usted`. Elegí el que usa la mayor parte del texto
  o el que pidió la persona. Si el texto está mitad y mitad y no hay pista, preguntá.
- `--permitir-prueba` solo si la persona confirmó que sus cifras de clientes son reales.

El script da una base objetiva para cada puntaje y la evidencia. No lo reemplaces por tu
impresión: es la parte que no cambia de una corrida a otra.

## Paso 2. Completar los puntajes con criterio

Leé el texto entero y ajustá cada puntaje según la guía de
`referencias/rubrica.md`. Las reglas:

1. **Sin completar solo puede bajar.** Si encontrás un hueco que el script no vio (un
   testimonio de «María G.» que claramente no es real, «Tu Marca», una fecha de
   relleno), bajalo con la misma escala: uno solo deja el puntaje en 6.
2. **Los otros cuatro se mueven como mucho 2 puntos** respecto del script, para arriba o
   para abajo.
3. **Cada punto que sacás o sumás lleva la frase exacta entre comillas.** Sin cita no hay
   ajuste. «Suena genérico» no es evidencia; «“Brindamos soluciones a medida” lo podría
   firmar cualquier estudio» sí.
4. **El general se recalcula** con tus puntajes finales: el promedio de los cinco. Si
   queda algo sin completar o hay prueba inventada (cifras de clientes, testimonios o
   premios que el texto no puede respaldar), el general no pasa de 6.

## Paso 3. Mostrar el resultado

Siempre con esta forma, en este orden:

```
Textosaurio · landing.html · web · trato: vos

  1  Sin completar            4/10
  2  Especificidad            5/10
  3  Correcto y completo      8/10
  4  Suena humano             6/10   (script: 8)
  5  Hecho para el formato    7/10

  GENERAL  6/10 — el promedio da 6, y quedan huecos sin completar
```

- Si tu puntaje final difiere del script, mostralo como `(script: N)`.
- Debajo, **una línea por puntaje** con lo más importante y su cita. Nada más: el
  detalle va en las recomendaciones.

## Paso 4. Preguntar qué recomendaciones quiere

Preguntá con opciones (usá la herramienta de preguntas si la tenés):

- **Todas las recomendaciones**
- **Solo de los puntajes menores a 8**
- **Solo de los puntajes menores a 6**

Si ningún puntaje queda debajo del umbral elegido, decilo en una línea y no inventes
recomendaciones.

Cada recomendación va así, agrupada por puntaje:

```
── 2 Especificidad (5/10)
   · «Ofrecemos atención personalizada para cada cliente»
     → «Te atiende siempre la misma contadora, y te responde el mismo día»
     Por qué: lo primero lo dice cualquier estudio; lo segundo es una promesa que se puede chequear.
```

Máximo cinco por puntaje, empezando por las que más suben el puntaje. Si el cambio
necesita un dato que el texto no tiene (un precio, un plazo, un barrio), la propuesta
lleva `[falta dato: precio del plan básico]` y no un número inventado.

## Paso 5. Ofrecer aplicarlas

Preguntá si querés que aplique las recomendaciones. Si dice que sí:

1. Escribí el texto mejorado **completo** en un archivo nuevo al lado del original:
   `landing.html` → `landing.textosaurio.html`. No pises el original salvo que lo pida.
2. Corré el script sobre el archivo nuevo, con el mismo formato y trato.
3. Mostrá antes y después:

```
                           antes   después
  1  Sin completar           4        5     (quedan 2 [falta dato])
  2  Especificidad           5        8
  3  Correcto y completo     8        9
  4  Suena humano            6        9
  5  Hecho para el formato   7        9
  GENERAL                    6        6     → completá los 2 datos y llega a 9
```

4. Listá los `[falta dato]` que quedaron, para que la persona sepa exactamente qué
   completar. Mientras queden, el general no pasa de 6. Es a propósito: un texto con
   huecos no está listo.

## Reglas que no se rompen

- **Nunca inventar datos ni prueba.** Ni cifras de clientes, ni testimonios, ni
  premios, ni años de experiencia, ni precios. Lo que falta se marca `[falta dato: …]`.
- **Respetar lo que el texto quiere decir.** Mejorar no es cambiar la oferta ni el tono
  de la marca. Si es técnico, sigue siendo técnico.
- **Respetar el trato.** Si el texto es de vos, todo queda en vos: `Descubre` →
  `Descubrí`, `Regístrate` → `Registrate` (sin tilde: la tilde es justo lo que delata el
  tuteo).
- **No tocar lo que está bien.** `no solo X, sino Y` es español correcto y no es señal de
  IA. Una enumeración de tres cosas reales tampoco.
- **Volver a puntuar siempre** después de reescribir. Un modelo que saca señales de IA
  también puede meter otras nuevas.
