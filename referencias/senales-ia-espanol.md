# Señales de escritura por IA en español

Las señales que usa el puntaje «Suena humano». Cinco grupos, dos puntos cada uno.

Todo espécimen de esta página va en `código` o ~~tachado~~. No es decoración: un literal
no es copy, y `textosaurio.py` los saltea al leer un `.md`. Así es como esta página pasa el
scorer que documenta.

Cada patrón lleva su estado de calibración. **Admitido** quiere decir que el corpus lo
respalda. **Sin evidencia** quiere decir que está en el catálogo pero la muestra todavía no
alcanza para afirmarlo. Los rechazados están en `referencias/fuentes.md`, con el número que
los rechazó al lado.

## 1. Léxico de IA

Dos listas que funcionan distinto.

**Por raíz.** El copy se escribe conjugado y con género. `Acme potencia tu negocio` es la
forma más común de la palabra, y matchear la forma exacta se la pierde entera. Así que
`potenciar` caza también `potenciamos`, `potenciada`, `potenciando` y `potenciación`.

La lista: `optimizar`, `transformador`, `robusto`, `holístico`, `sinergia`, `empoderar`,
`desbloquear`, `inigualable`, `vanguardia`, `meticuloso`, `maximizar`, `disruptivo`,
`escalable`, `sofisticado`.

`potenciar` está aparte, con patrón propio, y el motivo enseña algo. La raíz `potenci` caza
también `potencia` y `potencias`, que en prosa política son ~~las grandes potencias
occidentales~~ y no tienen nada que ver con el verbo: así marcaba el 4,1% de la prensa
humana. Ahora entran solo las formas inequívocamente verbales, más la tercera persona cuando
arrastra objeto — `potencia tu marca` —, que es la superficie que el copy usa de verdad.

**Exactas.** Frases hechas, y palabras que solo son tell en una forma precisa. Van enteras
porque la raíz cazaría el uso corriente: `viaje` es una palabra común y marcarla sería
llorar lobo, pero `un viaje de` transformación no lo es.

La lista: `experiencia única`, `de última generación`, `en constante evolución`,
`en el mundo actual`, `en la era digital`, `de vanguardia`, `soluciones integrales`,
`un viaje de`, `el mundo de hoy`, `a otro nivel`, `sin fisuras`, `de primer nivel`,
`de clase mundial`, `nuestra propuesta de valor`.

El arreglo es una palabra más llana. No un sinónimo más pomposo de la misma idea.

> ~~Potenciamos tu negocio con soluciones integrales de vanguardia.~~
> **Hacemos balances y liquidación de sueldos. Nada más.**
> Las tres palabras marcadas no significan nada y se comen un renglón.

## 2. Construcciones de IA

Formas, no palabras. Una forma es un molde que podés rellenar con cualquier cosa, y pesa
más que el léxico: un texto puede pasar el chequeo de vocabulario y seguir leyéndose como
escrito por una máquina.

**Acá está el hallazgo más fuerte del proyecto, y es una ausencia.**

La forma insignia del catálogo inglés es `not just X, but Y`, y su traducción directa es la
primera que cualquiera pondría en un catálogo español. No está en este. Sobre 355.386
palabras de prensa rioplatense anterior a 2023 marcaba el 8,6% de los textos:

> ~~advertido no solo por organizaciones ecologistas sino por organismos como el BCE~~
> ~~no solo se analizan casos de influenza, sino también otros virus respiratorios~~

En español es un correlativo gramatical corriente, no un tic de marketing. El inglés no
obliga a esa correlación, y por eso ahí la forma llama la atención; el español sí la obliga,
y por eso acá no dice nada. La medición está en `referencias/fuentes.md`.

Otras cinco construcciones se cayeron por lo mismo: `en definitiva`, `cuando se trata de`,
`la clave está en`, `empecemos` y `más que un X` son conectores normales del español.

Las que quedaron son las que sí son de registro comercial: `no se trata de X, es Y`,
`ahí es donde entra X`, `ya sea que X o Y`, `al siguiente nivel`,
`todo lo que necesitás saber`, `decile adiós a`, `imaginá un`, `descubrí cómo`,
`en un mundo cada vez más`, `te ayuda a`, `podría potencialmente`, `cabe destacar`, y las
preguntas que el propio texto se contesta, del tipo ~~¿El resultado? Menos reclamos.~~

Se chequean las dos personas gramaticales de cada forma que las tenga. Escribir en tuteo no
es un disfraz: es lo que el modelo emite por defecto, y el otro eje lo marca aparte.

> ~~Descubre cómo llevar tu inmobiliaria al siguiente nivel.~~
> **Cobramos comisión una sola vez, y recién cuando firmás.**
> La primera promete una revelación y entrega una abstracción.

## 3. Cadencia de puntuación

Este grupo es el que NO se puede traducir del inglés, y vale la pena explicar por qué.

En inglés el linter cuenta guiones largos: dos en una oración es tic de máquina. En español
la raya es puntuación legítima y **el inciso lleva dos**, una que abre y otra que cierra.
Contar rayas marcaría todo texto bien puntuado.

Lo que sí es calco es el uso **sin espacios**. En español el inciso abre con espacio afuera
y cierra con espacio afuera. Pegada de los dos lados es inglés:

> ~~El equipo—que trabaja hace años—resolvió el problema.~~
> **El equipo —que trabaja hace años— resolvió el problema.**
> La segunda tiene dos rayas y está perfecta. La primera tiene las mismas dos y es un calco.

Y hay una excepción más que enseñó el corpus, y que valía el 1,5% de los textos humanos:
cuando el inciso cierra al final de la oración, la puntuación va pegada afuera de la raya,
como en ~~de gobierno corporativo —en ese orden—.~~ Eso es español correcto, así que la
puntuación no cuenta como palabra pegada.

La densidad se mide igual, pero recién a partir de cuatro rayas en una oración, que ya son
dos incisos apilados.

El chequeo mira dentro de una ventana de 220 caracteres, y ese límite hace trabajo real. El
texto de interfaz no tiene puntos: los ítems de menú, los botones y las etiquetas corren
todos juntos, así que un corte ingenuo de oraciones trata la página entera como una sola
oración y la regla dispara sobre todo. Un linter que llora lobo se apaga, así que la ventana
se queda.

## 4. Ritmo de tres

Tres ítems seguidos. ~~Rápido, simple y confiable.~~

Tres adjetivos son un ritmo, no un argumento. Uno es retórica; tres en una página es una
máquina.

Acá también hubo que rediseñar. El español no usa coma de Oxford, así que de las dos formas
que busca el linter en inglés, la primera no dispararía nunca. Queda una sola forma: tres
ítems donde el tercero cierra la cláusula.

Esa condición es todo el trabajo. Si el tercer ítem sigue de largo, es una lista de cosas
reales y no un ritmo:

> `Inspección, reparación y reemplazo para casas y comercios` puntúa limpio. Son tres cosas
> que un techista hace de verdad, el tercer ítem se extiende, y marcarlo sería exactamente
> el llorar lobo que hace que el próximo lo apague.

> ~~Confiables, rápidos y siempre a tiempo.~~
> **Seis clavos por chapa. Siempre seis.**
> Una especificación le gana a tres adjetivos. Nadie inventa una línea así, porque el copy
> inventado no la sabe.

## 5. Venta y prueba inventada

Los cuatro grupos anteriores sacan el robot. Este hace la pregunta más difícil: ¿la línea
vende algo? Copy limpio que no dice nada sigue siendo una página muerta.

**La regla dura: nunca inventar prueba.** Ni cantidades de clientes, ni testimonios, ni
puntuaciones que el negocio no se ganó. El scorer marca cualquier número pegado a un
sustantivo de persona, del tipo ~~+10.000 clientes felices~~. Es trigger-happy a propósito:
un falso positivo cuesta diez segundos, un falso negativo pone en tu sitio una afirmación
que no podés respaldar. Si el número es real y lo podés mostrar, `--permitir-prueba` lo baja
a aviso y lo sigue imprimiendo.

Acá hubo otro rediseño obligado. El número se escribe distinto: en español el punto separa
los miles y la coma es el decimal. El patrón en inglés lee `10,000 users` y sobre
`10.000 clientes` no vería absolutamente nada.

También entran los superlativos que nadie puede chequear: `los más confiables`,
`líderes en`, `la mejor opción`, `número uno en`.

> ~~La inmobiliaria más confiable de Montevideo.~~
> **Alquileres, y solo alquileres, desde 2004.**
> `más confiable` no se puede verificar, así que el lector lo descuenta solo. Una fecha no
> se discute.

> ~~Más de 10.000 familias ya confiaron en nosotros.~~
> **Los nombres de los proyectos son de ejemplo. Cambialos por los tuyos antes de publicar.**
> Decir que el casillero está vacío se lee como confianza, no como debilidad.
