# Ejemplo completo: la landing de una veterinaria

Una corrida entera, de punta a punta. El texto original lo escribió Claude sin datos del
negocio, como parte del corpus de este repo. La veterinaria no existe. Los datos del
último paso son inventados para la demo, y así se dice donde aparecen.

Los archivos:

- [`veterinaria/original.md`](veterinaria/original.md): lo que escribió Claude, sin tocar.
- [`veterinaria/original.textosaurio.md`](veterinaria/original.textosaurio.md): con las
  recomendaciones aplicadas.
- [`veterinaria/completo.md`](veterinaria/completo.md): con los datos que faltaban.

## 1. El script

```
$ python3 tools/textosaurio.py ejemplos/veterinaria/original.md --formato web

Textosaurio · original.md · web · 459 palabras · trato: vos

  1  Sin completar           1/10   21 para revisar
  2  Especificidad           7/10   9 datos concretos, 0 frases genéricas
  3  Correcto y completo    10/10   nada que marcar
  4  Suena humano           10/10   nada que marcar
  5  Hecho para el formato  10/10   nada que marcar

  GENERAL  6/10  (el promedio da 7,6, pero hay cosas sin completar: tope 6)
```

El texto suena bien y no tiene errores. Pero le quedan 21 huecos: `[Nombre]`, `[barrio]`
seis veces, `[teléfono]`, `[hora]` cuatro veces, `[Completar según el servicio.]`.
Publicado así, un cliente vería corchetes.

## 2. El criterio de Claude

El skill lee el texto entero y ajusta. Cada ajuste lleva su cita.

```
Textosaurio · original.md · web · trato: vos

  1  Sin completar            1/10
  2  Especificidad            6/10   (script: 7)
  3  Correcto y completo      8/10   (script: 10)
  4  Suena humano             8/10   (script: 10)
  5  Hecho para el formato    8/10   (script: 10)

  GENERAL  6/10 (el promedio da 6,2, pero quedan huecos y hay testimonios sin respaldo)
```

- **Especificidad −1:** «Resultados rápidos para decidir a tiempo» no dice qué tan
  rápidos. «Horario extendido» no dice hasta qué hora.
- **Correcto y completo −2:** «las urgencias las atendemos siempre», pero el horario de
  contacto no incluye domingos. «Corte, baño y corte de uñas» repite «corte».
- **Suena humano −2:** «Eternamente agradecido», firmado `Julián, [barrio]`: tres
  testimonios que nadie puede respaldar. Eso es prueba inventada y activa el tope.
- **Hecho para el formato −2:** `## Hero` y `## Footer` quedarían visibles en la página. El
  título `Veterinaria [Nombre]` no dice dónde queda, y lo que la gente busca es
  «veterinaria en General Paz».

## 3. Las recomendaciones

Se eligió **todas**. Un fragmento:

```
── 1 Sin completar (1/10)
   · «— Mariana, [barrio]» (y los otros dos testimonios)
     → sacar la sección hasta tener testimonios reales, con permiso de quien los da
     Por qué: un testimonio con un barrio de plantilla es inventado, y el lector lo nota.
   · «[Completar según el servicio.]»
     → sacar la pregunta sobre animales exóticos, o responderla con un sí o un no
     Por qué: una pregunta frecuente sin respuesta es peor que no tenerla.

── 2 Especificidad (6/10)
   · «Resultados rápidos para decidir a tiempo»
     → «Los hacemos acá mismo. Los resultados están en [falta dato: plazo de entrega].»
     Por qué: «rápido» lo dice cualquiera; un plazo se puede cumplir o no.
   · «horario extendido para que puedas venir después del trabajo»
     → «De lunes a viernes cerramos a las [falta dato: hora de cierre]»
```

Ninguna recomendación inventa un plazo, un horario ni un teléfono. Donde falta el dato,
queda `[falta dato: …]`.

## 4. Aplicadas y vueltas a puntuar

```
                           antes   después
  1  Sin completar           1        1     (quedan 14 [falta dato])
  2  Especificidad           6        8
  3  Correcto y completo     8        9
  4  Suena humano            8        9
  5  Hecho para el formato   8        9
  GENERAL                    6        6     → completá los datos y llega a 9,6
```

El general no se mueve, y es a propósito: el texto está mejor, pero todavía no se puede
publicar. Lo que falta completar, 12 datos en 14 lugares:

```
[falta dato: barrio]                     [falta dato: barrios que cubren]
[falta dato: dirección]                  [falta dato: horario] (semana y sábado)
[falta dato: hora de cierre]             [falta dato: teléfono]
[falta dato: plazo de entrega]           [falta dato: número de WhatsApp]
[falta dato: teléfono de urgencias]      [falta dato: si hay cuotas y con qué tarjetas]
[falta dato: días y horario de urgencias]
[falta dato: cuántos veterinarios y sus nombres]
```

## 5. Con los datos completos

Datos inventados para la demo: Veterinaria Los Plátanos, General Paz, 25 de Mayo 1480,
teléfonos 351 555-0142 y 0143.

```
$ python3 tools/textosaurio.py ejemplos/veterinaria/completo.md --formato web

  1  Sin completar          10/10   nada que marcar
  2  Especificidad          10/10   28 datos concretos, 0 frases genéricas
  3  Correcto y completo    10/10   nada que marcar
  4  Suena humano           10/10   nada que marcar
  5  Hecho para el formato  10/10   nada que marcar

  GENERAL  10/10
```

Con el criterio de Claude queda en **9,6**. Correcto y completo baja a 9 porque «te
explicamos cuánto cuesta cada una» no viene con un solo precio de referencia. Suena humano
también baja a 9, porque «Cuidamos a tu mascota como si fuera nuestra» es una frase hecha;
se dejó porque es el lema de la marca, y cambiarlo le toca a quien escribe.
