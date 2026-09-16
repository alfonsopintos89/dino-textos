# Guía de puntajes

Qué significa cada número en cada uno de los cinco puntajes. El script da la base y
esta guía sirve para ajustarla con criterio: como mucho 2 puntos, y siempre citando la
frase exacta.

## 1. Sin completar

Lo que quedó de la plantilla. No necesita criterio: un `[Nombre]` es un `[Nombre]`.

| Puntaje | Qué significa |
|---|---|
| 10 | No queda nada de plantilla. |
| 6 | Queda un hueco. Ya no se puede publicar. |
| 4 | Quedan tres. |
| 1 | Seis o más. El texto es una plantilla con partes escritas. |

Lo que el script ve: corchetes de formulario (`[Nombre]`, `[precio]`, `[X]`), variables
(`{{nombre}}`, `{id}`), `XX` en lugar de un número, `lorem ipsum`, mails y dominios de
ejemplo, teléfonos como `1234-5678`, `TODO`, y enlaces con `href="#"`.

Lo que tenés que buscar vos, porque un regex no lo distingue:

- Testimonios firmados con un nombre que nadie puede verificar: `María G., cliente feliz`.
- Nombres de marca genéricos: «Tu Marca», «La Empresa».
- Fechas, horarios o direcciones que son obviamente de relleno.
- Secciones anunciadas que no existen («mirá nuestros casos más abajo» y abajo no hay nada).

## 2. Especificidad

**La prueba del competidor:** cambiá el nombre del negocio por el de la competencia. Si la
oración sigue siendo verdad, es genérica. `Brindamos un servicio de calidad` sobrevive al
cambio. «Te respondemos por WhatsApp antes de las 18 hs del mismo día» no.

| Puntaje | Qué significa |
|---|---|
| 9-10 | Casi cada párrafo trae algo que se puede chequear: precio, plazo, lugar, cantidad, nombre, proceso concreto. |
| 7-8 | La mayoría de las promesas son concretas; quedan una o dos frases de relleno. |
| 5-6 | Mitad y mitad. La oferta se entiende, pero cuesta distinguirla de la competencia. |
| 3-4 | Casi todo pasa la prueba del competidor. |
| 1-2 | No hay un solo dato. El texto podría ser de cualquier rubro. |

El script cuenta datos concretos (cifras, precios, plazos, días, meses, nombres propios) y
resta las frases genéricas (`soluciones integrales`, `atención personalizada`, `de
calidad`, `los más confiables`). Subí el puntaje cuando haya datos que el regex no ve
(«la misma contadora de principio a fin»). Bajalo cuando los datos que contó no dicen nada
(«más de 100 soluciones»).

## 3. Correcto y completo

Dos preguntas: ¿está bien escrito? y ¿tiene todo lo que ese formato necesita?

| Puntaje | Qué significa |
|---|---|
| 9-10 | Sin errores, trato parejo, y no falta nada que el lector vaya a buscar. |
| 7-8 | Algún error menor o falta un elemento secundario. |
| 5-6 | Cambia de trato, tiene errores visibles, o falta algo importante. |
| 3-4 | Varios errores o faltan cosas centrales (no se sabe cuánto cuesta ni cómo contactar). |
| 1-2 | No se puede publicar así. |

El script marca: trato mezclado (voseo, tuteo, usted), léxico de España en un texto
rioplatense, preguntas sin `¿` y exclamaciones sin `¡`, `Mayúsculas En Cada Palabra` en
títulos y palabras repetidas como `de de`.

Lo que revisás vos:

- **Ortografía y concordancia** que un regex no ve.
- **Datos que se contradicen**: dos precios distintos, dos horarios, «envío gratis» y
  después «costo de envío».
- **Lo que falta según el formato:**
  - **Web / landing:** qué es, para quién, cuánto cuesta o cómo se cotiza, cómo
    contactar y un llamado a la acción claro.
  - **Blog:** que responda la pregunta del título, y que la respuesta llegue pronto.
  - **LinkedIn / Instagram:** una sola idea, y qué tiene que hacer el lector al terminar.

## 4. Suena humano

Es el puntaje más difícil y el más propenso a opinión. Por eso la base es el script: sus
señales están medidas contra 592 notas de prensa rioplatense escritas por personas, y
ninguna marca más del 0,5% de esas notas.

| Puntaje | Qué significa |
|---|---|
| 9-10 | Suena a alguien que conoce el negocio. Tiene voz propia. |
| 7-8 | Natural, con alguna muletilla de IA suelta. |
| 5-6 | Se nota la IA: vocabulario inflado, formas de plantilla, ritmo parejo. |
| 3-4 | Suena a IA en casi todos los párrafos. |
| 1-2 | Plantilla de IA sin tocar. |

El script marca léxico de IA (`potenciar`, `optimizar`, `robusto`, `de vanguardia`),
construcciones de plantilla (`ahí es donde entra`, `llevá tu X al siguiente nivel`), rayas
al modo inglés, tríadas de adjetivos al principio de oración, prueba inventada y oraciones
todas del mismo largo.

Lo que buscás vos (bajá solo si lo podés citar):

- Cierre que resume lo que ya se dijo («En resumen, …», «En definitiva, …»).
- Todos los ítems de una lista con la misma forma y el mismo largo.
- Negrita al principio de cada viñeta.
- Preguntas retóricas que el propio texto contesta.
- Emojis de decoración en cada título.
- Entusiasmo sin objeto: «¡Estamos felices de acompañarte en este camino!».

Subí si tiene cosas que una IA no escribe por defecto: una opinión con la que alguien
podría no estar de acuerdo, un detalle del oficio, una frase corta después de una larga,
humor.

**Lo que no es señal de IA en español:** `no solo X, sino Y` (aparece en el 8,6% de la
prensa humana), una enumeración común de tres cosas, dos rayas que abren y cierran un
inciso.

## 5. Hecho para el formato

| Puntaje | Qué significa |
|---|---|
| 9-10 | Cumple lo técnico y está pensado para cómo se lee en ese lugar. |
| 7-8 | Falta un detalle técnico o la estructura se puede mejorar. |
| 5-6 | Se nota que se escribió sin pensar dónde va. |
| 3-4 | Varios problemas: sin título, bloques enormes, gancho escondido. |
| 1-2 | No sirve para ese formato. |

Los controles del script, con su fuente, están en `referencias/formatos.md`.

Lo que juzgás vos:

- **Web:** ¿el `<h1>` y el primer párrafo dicen qué es y para quién? ¿El `<title>` usa las
  palabras que alguien buscaría en Google?
- **Blog:** ¿los subtítulos permiten encontrar la respuesta sin leer todo?
- **LinkedIn / Instagram:** ¿la primera línea da ganas de tocar «ver más»? ¿Se lee bien en
  el celular?
