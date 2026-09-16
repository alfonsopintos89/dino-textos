# Registro rioplatense

El catálogo del segundo eje. Tres grupos, un punto cada uno.

Este eje no existe en la versión inglesa del problema, y no es un capricho: un texto puede
ser humanísimo y estar escrito en peninsular, o estar en voseo perfecto y ser slop puro. Son
dos fallas distintas, se arreglan con ediciones distintas, y por eso puntúan aparte.

A diferencia del eje de slop, este no se calibra contra corpus. Sus reglas son de morfología,
no de frecuencia: `vosotros` es peninsular por gramática, no por estadística. Se sostienen
con los tests de falso positivo, que es lo que corresponde.

## 1. Pronombres y morfología

Lo más barato y lo más inequívoco. `tú`, `ti`, `contigo`, `vosotros`, `vuestro`, el `os`
pronombre, y las conjugaciones terminadas en `-áis` y `-éis`.

Dos cosas que quedaron **afuera** a propósito, y son las que hacen que la regla sirva:

**`te` no está en la lista.** Es el pronombre del voseo. `vos te vas` es rioplatense
perfecto. Meterlo junto a `tú` y `ti` dejaría marcado casi todo texto bien escrito de acá,
que es la forma más rápida de que alguien apague el linter.

**`-ís` tampoco.** Es terminación de `vosotros`, sí, pero antes que eso es voseo:
`vivís`, `salís`, `escribís`. `-áis` y `-éis` no tienen esa colisión.

`tu` sin tilde tampoco se toca: `tu casa` es correcto en voseo. Solo `tú` con tilde es el
tell, y por eso el scorer nunca normaliza quitando acentos.

## 2. Imperativos que no son voseo

El tell más ruidoso del copy en español, y el problema técnico más difícil del proyecto.

Todo lo que genera un modelo dice ~~Descubre nuestra plataforma~~, ~~Prueba gratis~~,
~~Regístrate~~. Pero `descubre` y `prueba` son también tercera persona del indicativo y
sustantivo. Estas dos oraciones son español impecable:

> El equipo `conoce` el rubro y `prueba` cada material que instala.
> La `prueba` de carga dio 400 kilos por metro.

Un `\bdescubre\b` pelado marca las dos. Por eso la regla caza solo donde es inequívoco, por
tres vías:

**Enclíticos de tuteo.** El pronombre pegado no deja lugar a dudas: `regístrate`,
`suscríbete`, `contáctanos`, `pruébalo`, `descúbrelo`, `únete`, `escríbenos`.

**La tilde.** `regístrate` es tuteo, `registrate` es voseo, y esa tilde es la única
diferencia entre las dos. Es la razón concreta por la que la normalización del scorer pliega
comillas y guiones pero jamás toca los acentos: el reflejo normal al normalizar español es
plegar los acentos, y acá dejaría ciego al grupo entero.

**Posición de botón.** Un verbo de una lista cerrada de copy — `descubre`, `prueba`,
`conoce`, `elige`, `empieza`, `solicita`, `agenda`, `reserva`, `descarga` — cuando encabeza
un renglón de menos de sesenta caracteres. Ahí es un botón, un título o una llamada a la
acción, no una oración corrida.

Y todavía con eso hay una salvaguarda más: si al verbo lo sigue `de`, `del`, `que`, `para`,
`en`, `con` o `por`, no se marca. Un sustantivo arrastra su complemento y un botón no, así
que `Prueba de carga` se salva y `Prueba gratis` no.

Fuera de esas tres vías la regla no marca nada. Pierde aciertos, y está bien que los pierda:
un acierto perdido cuesta poco, y un linter que llora lobo lo apagás a la semana.

> ~~Descubre todo lo que podemos hacer por vos.~~
> **Mirá los quince proyectos que entregamos este año.**
> El voseo solo no alcanzaba: la línea también tenía que decir algo.

## 3. Léxico peninsular

`ordenador`, `coger`, `zumo`, `gafas`, `aparcar`, `chaval`.

Tres que están tratadas con cuidado especial, porque el regex ingenuo falla:

**`móvil` solo con determinante.** `el móvil` es el teléfono; `app móvil` y `unidad móvil`
son de uso corriente de este lado y no son tell de nada. La regla pide `el`, `un`, `los`,
`mi`, `tu` o `su` adelante.

**`vale` solo como muletilla.** Tiene que arrancar la oración y cerrar con coma o punto.
`¿cuánto vale?` y `vale la pena` son español de acá y no se tocan.

**`coger` sobrevive dentro de otras palabras.** `recoger` y `escoger` no disparan, porque el
límite de palabra las protege.

Y una que **no entró**: `piso`. Es vivienda en España y suelo acá, y no hay forma de
distinguirlas con un regex. Se pierde el acierto y se evita marcar todo texto que hable de
un piso mojado. `conducir` y `billete` quedaron afuera por lo mismo, y están medidas como
candidatas en `referencias/fuentes.md`.
