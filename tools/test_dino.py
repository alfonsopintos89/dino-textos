#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Suite de regresión de dino.py.

Cada regla llega acá con dos tests: un espécimen que la dispara y un texto
humano parecido que NO la dispara. El segundo es el que importa. Es la
diferencia entre un linter que usás y uno que apagás a la semana.
"""
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dino


class TestNormalizar(unittest.TestCase):

    def test_pliega_comilla_tipografica(self):
        self.assertEqual(dino.normalizar("qué lindo día"), "qué lindo día")
        self.assertEqual(dino.normalizar("no es"), "no es")
        self.assertEqual(dino.normalizar("de‑vanguardia"), "de-vanguardia")

    def test_nunca_saca_tildes(self):
        """La tilde es lo único que separa `regístrate` (tuteo) de `registrate` (voseo).

        Normalizar plegando acentos, que es el reflejo normal, dejaría ciego
        al eje de registro entero.
        """
        self.assertEqual(dino.normalizar("regístrate"), "regístrate")
        self.assertNotEqual(dino.normalizar("regístrate"), dino.normalizar("registrate"))

    def test_colapsa_espacios_pero_conserva_renglones(self):
        """Los renglones marcan dónde termina una pieza de copy.

        Un botón y el párrafo que le sigue son dos textos distintos. Pegados
        en un renglón, la regla de CTA no puede ver dónde empieza cada uno.
        """
        self.assertEqual(dino.normalizar("hola    mundo"), "hola mundo")
        self.assertEqual(dino.normalizar("uno\n\n\ndos"), "uno\ndos")
        self.assertEqual(dino.normalizar("  uno  \n  dos  "), "uno\ndos")


class TestTextoVisible(unittest.TestCase):

    def test_saca_script_style_y_etiquetas(self):
        html = '<style>.a{color:red}</style><p>Hola mundo</p><script>var x=1;</script>'
        self.assertEqual(dino.texto_visible(html), 'Hola mundo')

    def test_decodifica_entidades(self):
        self.assertEqual(dino.texto_visible('<p>m&aacute;s caf&eacute;</p>'), 'más café')
        self.assertEqual(dino.texto_visible('<p>d&#xed;a</p>'), 'día')

    def test_cada_cta_queda_en_su_propio_renglon(self):
        html = '<h1>Inmobiliaria</h1><button>Descubre más</button><p>Vendemos casas.</p>'
        self.assertEqual(dino.texto_visible(html).split('\n'),
                         ['Inmobiliaria', 'Descubre más', 'Vendemos casas.'])


class TestProsaMarkdown(unittest.TestCase):

    def test_saca_los_especimenes_citados(self):
        """Un literal no es copy. Un catálogo que documenta `potenciar` no lo shipeó."""
        md = 'Evitá `potenciar` y ~~no solo esto, sino aquello~~ en tu copy.'
        prosa = dino.prosa_markdown(md)
        self.assertNotIn('potenciar', prosa)
        self.assertNotIn('sino aquello', prosa)

    def test_saca_bloques_de_codigo_y_alt_de_imagenes(self):
        md = 'Texto.\n\n```\npython3 dino.py --texto "potenciar"\n```\n\n![potenciar acá](x.png)'
        prosa = dino.prosa_markdown(md)
        self.assertNotIn('potenciar', prosa)

    def test_conserva_el_texto_de_los_enlaces(self):
        md = 'Leé [la guía de estilo](https://example.com) antes.'
        self.assertIn('la guía de estilo', dino.prosa_markdown(md))

    def test_titulos_y_vinetas_son_renglones_propios(self):
        md = '# Un título\n\n- primer ítem\n- segundo ítem\n'
        renglones = dino.prosa_markdown(md).split('\n')
        self.assertIn('Un título', renglones)
        self.assertIn('primer ítem', renglones)


class TestLexicoDeIA(unittest.TestCase):

    def test_dispara_con_lexico_de_modelo(self):
        h = dino.auditar('Potenciamos tu negocio con una plataforma robusta y holística.')
        self.assertTrue(h['slop']['lexico'])

    def test_caza_la_palabra_por_raiz(self):
        """El copy se escribe conjugado. `potenciamos`, `potenciada`, `potencia`.

        Matchear la forma exacta se pierde justo la superficie más común.
        """
        for forma in ('optimizamos', 'optimizada', 'optimizando', 'optimiza'):
            h = dino.auditar('Una experiencia %s para el cliente.' % forma)
            self.assertTrue(h['slop']['lexico'], forma)

    def test_no_dispara_con_prosa_humana(self):
        h = dino.auditar('Arreglamos techos desde 2001. Seis clavos por chapa, siempre.')
        self.assertEqual(h['slop']['lexico'], [])

    def test_no_dispara_con_una_palabra_de_uso_corriente(self):
        """`viaje` es una palabra común. Marcarla es llorar lobo."""
        h = dino.auditar('El viaje a Salto dura cuatro horas y media.')
        self.assertEqual(h['slop']['lexico'], [])


class TestConstrucciones(unittest.TestCase):

    def test_dispara_con_no_se_trata_de_x_es_y(self):
        h = dino.auditar('No se trata de vender más, es de vender mejor.')
        self.assertTrue(h['slop']['construcciones'])

    def test_dispara_con_ahi_es_donde_entra(self):
        h = dino.auditar('Ahí es donde entra nuestra plataforma.')
        self.assertTrue(h['slop']['construcciones'])

    def test_dispara_con_pregunta_que_se_contesta_sola(self):
        h = dino.auditar('Menos reclamos. ¿El resultado? Clientes que vuelven.')
        self.assertTrue(h['slop']['construcciones'])

    def test_no_dispara_con_un_no_solo_sin_la_forma_completa(self):
        """La forma es `no solo X, sino Y`. Sin el remate no hay tell."""
        h = dino.auditar('No solo vinimos a cobrar: dejamos el presupuesto firmado.')
        self.assertEqual(h['slop']['construcciones'], [])

    def test_no_dispara_con_prosa_humana(self):
        h = dino.auditar('Vino, miró el techo y dijo que no valía la pena cambiarlo.')
        self.assertEqual(h['slop']['construcciones'], [])


class TestCadencia(unittest.TestCase):

    def test_dispara_con_raya_al_modo_ingles(self):
        """Sin espacios de ningún lado es calco del inglés."""
        h = dino.auditar('El equipo—que trabaja hace años—resolvió el problema.')
        self.assertTrue(h['slop']['cadencia'])

    def test_no_dispara_con_el_inciso_bien_escrito(self):
        """En español el inciso lleva espacio afuera y ninguno adentro.

        Dos rayas en una oración es lo NORMAL acá: abre y cierra. Contar rayas
        como hace el linter en inglés marcaría todo texto bien puntuado.
        """
        h = dino.auditar('El equipo —que trabaja hace años— resolvió el problema.')
        self.assertEqual(h['slop']['cadencia'], [])

    def test_no_dispara_con_la_raya_de_cierre_antes_de_puntuacion(self):
        """«—gobierno corporativo—.» es español correcto: el inciso cierra y

        la puntuación de la oración va pegada afuera. El patrón leía el
        «—.» como raya sin espacios, o sea como calco del inglés.
        """
        for frase in ('Habló de riesgo y de gobierno corporativo —en ese orden—.',
                      'Defendió el “originalismo” judicial —según dijo—, y se fue.'):
            h = dino.auditar(frase)
            self.assertEqual(h['slop']['cadencia'], [], frase)

    def test_no_dispara_con_un_guion_comun(self):
        h = dino.auditar('Es un acuerdo público-privado que arrancó en 2019.')
        self.assertEqual(h['slop']['cadencia'], [])


class TestRitmoDeTres(unittest.TestCase):

    def test_dispara_con_tres_adjetivos(self):
        h = dino.auditar('Rápido, simple y confiable.')
        self.assertTrue(h['slop']['ritmo'])

    def test_dispara_con_la_y_convertida_en_e(self):
        h = dino.auditar('Rápido, simple e intuitivo.')
        self.assertTrue(h['slop']['ritmo'])

    def test_no_dispara_con_una_lista_de_servicios_reales(self):
        """Tres cosas que un techista hace de verdad. Marcarlo es llorar lobo."""
        h = dino.auditar('Inspección, reparación y reemplazo para casas y comercios.')
        self.assertEqual(h['slop']['ritmo'], [])


class TestVentaYPrueba(unittest.TestCase):

    def test_dispara_con_prueba_inventada(self):
        h = dino.auditar('Más de 10.000 clientes felices en todo el país.')
        self.assertTrue(h['slop']['venta'])

    def test_lee_el_numero_con_formato_espanol(self):
        """`10.000` es diez mil, no diez. El punto separa miles y la coma decimales.

        El patrón en inglés lee `10,000` y acá no vería absolutamente nada.
        """
        for n in ('10.000', '+5.000', '5.000+', '1.250'):
            h = dino.auditar('%s usuarios ya lo usan.' % n)
            self.assertTrue(h['slop']['venta'], n)

    def test_dispara_con_superlativo_no_verificable(self):
        h = dino.auditar('Somos los más confiables del rubro.')
        self.assertTrue(h['slop']['venta'])

    def test_no_dispara_con_un_numero_que_no_cuenta_personas(self):
        h = dino.auditar('El presupuesto cerró en 10.000 pesos más IVA.')
        self.assertEqual(h['slop']['venta'], [])

    def test_no_dispara_con_un_comparativo_comun(self):
        h = dino.auditar('Es el techo más barato que conseguimos este año.')
        self.assertEqual(h['slop']['venta'], [])


class TestPronombres(unittest.TestCase):

    def test_dispara_con_tuteo(self):
        h = dino.auditar('Si tú querés, lo mandamos a tu casa. Esto es para ti.')
        self.assertTrue(h['registro']['pronombres'])

    def test_dispara_con_vosotros(self):
        h = dino.auditar('Vosotros sabéis lo que hacéis con vuestro tiempo.')
        self.assertTrue(h['registro']['pronombres'])

    def test_no_dispara_con_el_te_del_voseo(self):
        """`te` es el pronombre del voseo. `vos te vas` es rioplatense perfecto.

        Meterlo en la lista junto a `tú` y `ti` dejaría marcado como peninsular
        casi todo texto bien escrito de acá.
        """
        h = dino.auditar('Si querés, te lo mandamos por mail y te avisamos.')
        self.assertEqual(h['registro']['pronombres'], [])


class TestImperativos(unittest.TestCase):

    def test_dispara_con_enclitico_de_tuteo(self):
        """El pronombre pegado no deja lugar a dudas: `regístrate` no es voseo."""
        h = dino.auditar('Regístrate ahora y contáctanos por cualquier duda.')
        self.assertTrue(h['registro']['imperativos'])

    def test_dispara_con_verbo_de_copy_en_posicion_de_boton(self):
        html = '<p>Vendemos casas en toda la costa.</p><button>Descubre más</button>'
        h = dino.auditar(dino.texto_visible(html))
        self.assertTrue(h['registro']['imperativos'])

    def test_no_dispara_con_el_imperativo_voseante(self):
        h = dino.auditar(dino.texto_visible(
            '<button>Registrate</button><button>Probá gratis</button>'))
        self.assertEqual(h['registro']['imperativos'], [])

    def test_no_dispara_con_tercera_persona_del_indicativo(self):
        """`prueba` y `conoce` son también tercera persona. Es la colisión que

        hace difícil a esta regla, y marcarlas sin mirar el contexto convierte
        prosa impecable en un tablero de errores.
        """
        h = dino.auditar('El equipo conoce el rubro y prueba cada material que instala.')
        self.assertEqual(h['registro']['imperativos'], [])

    def test_no_dispara_con_el_sustantivo_encabezando_un_renglon_corto(self):
        """`Prueba de carga` es un sustantivo en un título, no una llamada a la acción."""
        h = dino.auditar(dino.texto_visible('<h2>Prueba de carga</h2>'))
        self.assertEqual(h['registro']['imperativos'], [])


class TestLexicoPeninsular(unittest.TestCase):

    def test_dispara_con_lexico_de_espana(self):
        h = dino.auditar('Abrí el ordenador y dejé el móvil cargando. Vale, listo.')
        self.assertTrue(h['registro']['lexico_peninsular'])

    def test_no_dispara_con_el_equivalente_rioplatense(self):
        h = dino.auditar('Abrí la computadora y dejé el celular cargando. Listo.')
        self.assertEqual(h['registro']['lexico_peninsular'], [])

    def test_no_dispara_con_piso_en_su_sentido_de_aca(self):
        """`piso` es vivienda en España y suelo acá. Sin forma de distinguirlos

        en un regex, la palabra no entra: se pierde un acierto y se evita
        marcar todo texto que hable de un piso mojado.
        """
        h = dino.auditar('El piso está mojado, pisá con cuidado.')
        self.assertEqual(h['registro']['lexico_peninsular'], [])


LIMPIO = 'Arreglamos techos desde 2001. Seis clavos por chapa, siempre.'
SUCIO = ('Potenciamos tu negocio con una plataforma robusta. '
         'Ahí es donde entra nuestro equipo.')


class TestPuntaje(unittest.TestCase):

    def test_texto_limpio_da_puntaje_perfecto(self):
        self.assertEqual(dino.puntuar(dino.auditar(LIMPIO)), (5, 3))

    def test_cada_grupo_con_aciertos_descuenta_un_punto(self):
        """Dos grupos tocados, dos puntos menos. Un grupo con ocho aciertos

        descuenta lo mismo que uno con uno solo: el arreglo es el mismo.
        """
        slop, _ = dino.puntuar(dino.auditar(SUCIO))
        self.assertEqual(slop, 3)

    def test_los_dos_ejes_puntuan_por_separado(self):
        """Un texto puede ser humanísimo y estar escrito en peninsular."""
        slop, registro = dino.puntuar(dino.auditar('Coge el ordenador, por favor.'))
        self.assertEqual(slop, 5)
        self.assertLess(registro, 3)

    def test_permitir_prueba_no_descuenta_el_punto(self):
        h = dino.auditar('Más de 10.000 clientes nos eligieron.')
        self.assertEqual(dino.puntuar(h)[0], 4)
        self.assertEqual(dino.puntuar(h, permitir_prueba=True)[0], 5)


class TestCLI(unittest.TestCase):

    def correr(self, *args):
        return subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          'dino.py')] + list(args),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def test_sale_cero_con_texto_limpio(self):
        self.assertEqual(self.correr('--texto', LIMPIO).returncode, 0)

    def test_sale_uno_con_texto_sucio(self):
        self.assertEqual(self.correr('--texto', SUCIO).returncode, 1)

    def test_entrada_vacia_falla_en_vez_de_aprobar(self):
        """Una entrada vacía que puntúa limpio reporta slop como limpio justo

        en el momento en que el pipeline se rompió. Es la peor falla posible
        en un gate: pasa verde porque no pudo leer nada.
        """
        self.assertEqual(self.correr('--texto', '   ').returncode, 2)

    def test_archivo_ilegible_sale_con_dos(self):
        self.assertEqual(self.correr('/no/existe/che.md').returncode, 2)

    def test_sin_registro_apaga_el_segundo_eje(self):
        salida = self.correr('--texto', 'Coge el ordenador.', '--sin-registro')
        self.assertEqual(salida.returncode, 0)
        self.assertNotIn(b'registro', salida.stdout.lower())

    def test_el_reporte_nombra_los_dos_ejes(self):
        salida = self.correr('--texto', SUCIO).stdout.decode('utf-8')
        self.assertIn('slop', salida)
        self.assertIn('registro', salida)


class TestFalsosPositivosDelCorpus(unittest.TestCase):
    """Especímenes reales del corpus humano que el scorer marcaba mal.

    Cada uno viene de una nota de la diaria anterior a 2023, así que es humano
    por construcción. Son la razón por la que estas tres reglas cambiaron.
    """

    def test_no_marca_una_enumeracion_comun_como_ritmo_de_tres(self):
        """En español `X, Y y Z` es simplemente cómo se enumeran tres cosas.

        La forma sola no distingue una enumeración de un tricolon retórico.
        Lo que sí lo distingue es que el tricolon de copy abre la oración.
        """
        for frase in ('El encuentro reunió a políticos, empresarios y periodistas.',
                      'Recorrió Francia, España e Italia, y volvió en marzo.',
                      'Ganó las tablas, el anual y el clausura.'):
            h = dino.auditar(frase)
            self.assertEqual(h['slop']['ritmo'], [], frase)

    def test_no_marca_los_anios_como_ritmo_de_tres(self):
        h = dino.auditar('Pasó en 2010, 2011 y 2012.')
        self.assertEqual(h['slop']['ritmo'], [])

    def test_no_marca_periodismo_que_cuenta_gente(self):
        """Un diario cuenta personas todo el tiempo. La prueba inventada no es

        un número al lado de un sustantivo: es un número al lado de un
        sustantivo dentro de un marco de venta.
        """
        for frase in ('A la institución concurrían unos 250 estudiantes.',
                      'En ella trabajaban 104 personas.',
                      'Dan clase a unas 5.000 personas en cinco escuelas.',
                      'Investigaban la muerte de 43 estudiantes en Guerrero.'):
            h = dino.auditar(frase)
            self.assertEqual(h['slop']['venta'], [], frase)

    def test_sigue_marcando_la_prueba_con_marco_de_venta(self):
        for frase in ('Más de 10.000 clientes felices.',
                      '+5.000 usuarios ya confían en nosotros.',
                      'Nuestros 300 clientes lo usan todos los días.'):
            h = dino.auditar(frase)
            self.assertTrue(h['slop']['venta'], frase)

    def test_no_marca_los_mas_de_como_superlativo(self):
        """`los más de 5.000` es una cantidad, no un superlativo. El patrón

        `los más \w+` la leía como si fuera «los más confiables».
        """
        h = dino.auditar('Asistieron los más de 5.000 socios convocados.')
        self.assertEqual(h['slop']['venta'], [])

    def test_no_marca_un_superlativo_descriptivo(self):
        h = dino.auditar('Los más afectados fueron los barrios de la costa.')
        self.assertEqual(h['slop']['venta'], [])


class TestFalsosPositivosDeLaSegundaCorrida(unittest.TestCase):
    """Lo que enseñó el corpus corregido: 592 documentos, 355.386 palabras de

    prosa real de las dos orillas. Con el corpus anterior estas reglas no se
    veían, porque aquel era mayormente plantilla de los sitios.
    """

    def test_no_marca_potencia_como_sustantivo(self):
        """`potencia` sustantivo no tiene nada que ver con el verbo `potenciar`.

        La raíz `potenci` cazaba las dos, y en prosa política el sustantivo es
        muchísimo más frecuente.
        """
        for frase in ('Las potencias occidentales pidieron prudencia.',
                      'Hay potencia política en la alegoría.',
                      'Lo que pueden establecer las grandes potencias.'):
            h = dino.auditar(frase)
            self.assertEqual(h['slop']['lexico'], [], frase)

    def test_sigue_marcando_el_verbo_potenciar(self):
        for frase in ('Potenciamos tu negocio.', 'Una solución que potencia tu marca.',
                      'Diseñado para potenciar resultados.'):
            h = dino.auditar(frase)
            self.assertTrue(h['slop']['lexico'], frase)

    def test_no_marca_al_lider_de_una_organizacion(self):
        """`el líder de la asociación bancaria` es una persona, no una

        afirmación de mercado. El patrón leía `líder de la` como si fuera
        `líderes en el rubro`.
        """
        for frase in ('Felicitó al líder de la asociación bancaria.',
                      'Una reunión de líderes de la comunidad.',
                      'Desconfiaba del líder de la compañía.'):
            h = dino.auditar(frase)
            self.assertEqual(h['slop']['venta'], [], frase)

    def test_sigue_marcando_la_afirmacion_de_mercado(self):
        h = dino.auditar('Somos líderes en el mercado uruguayo.')
        self.assertTrue(h['slop']['venta'])

    def test_no_marca_el_correlativo_no_solo_sino(self):
        """En español `no solo X sino Y` es un correlativo gramatical corriente,

        no un tic de marketing. Es la regla insignia del catálogo inglés y es
        la que peor transfiere: marcaba el 8,6% de la prensa humana.
        """
        for frase in ('Fue advertido no solo por ecologistas sino por organismos como el BCE.',
                      'No solo se analizan casos de influenza, sino también otros virus.',
                      'Ellas no solo rompían una imagen tradicional sino que se liberaban.'):
            h = dino.auditar(frase)
            self.assertEqual(h['slop']['construcciones'], [], frase)


if __name__ == '__main__':
    unittest.main(verbosity=2)
