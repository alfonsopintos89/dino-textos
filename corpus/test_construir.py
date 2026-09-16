#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests del descubrimiento de URLs. La descarga en sí no se testea; el filtro
de fecha sí, porque es lo único que garantiza que el corpus sea humano."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construir


class TestSubSitemapsPreCorte(unittest.TestCase):

    LOCS = [
        'https://x.com/sitemap_contents_2022_11_a59a1_001.xml',
        'https://x.com/sitemap_contents_2022_12_a59a1_001.xml',
        'https://x.com/sitemap_contents_2023_01_a59a1_001.xml',
        'https://x.com/sitemap_contents_2026_09_a59a1_001.xml',
        'https://x.com/sitemap_news.xml',
    ]
    PATRON = r'_(\d{4})_(\d{2})_'

    def test_deja_solo_los_anteriores_al_corte(self):
        elegidos = construir.sub_sitemaps_pre_corte(self.LOCS, self.PATRON, (2023, 1))
        self.assertEqual(len(elegidos), 2)
        self.assertTrue(all('2022' in u for u in elegidos))

    def test_descarta_los_que_no_tienen_fecha_en_el_nombre(self):
        """Sin fecha no hay garantía de que sea humano, así que no entra.

        El corpus se sostiene sobre la fecha de corte. Un documento que no
        puede probar la suya vale menos que no tenerlo.
        """
        elegidos = construir.sub_sitemaps_pre_corte(self.LOCS, self.PATRON, (2023, 1))
        self.assertNotIn('https://x.com/sitemap_news.xml', elegidos)

    def test_el_corte_compara_tambien_el_mes(self):
        elegidos = construir.sub_sitemaps_pre_corte(self.LOCS, self.PATRON, (2022, 12))
        self.assertEqual(elegidos, ['https://x.com/sitemap_contents_2022_11_a59a1_001.xml'])


class TestQuitarPlantilla(unittest.TestCase):
    """Un renglón que se repite en muchos documentos es plantilla, no prosa.

    Sin esto, el corpus mide el pie de página del diario en vez de cómo
    escribe la gente. Y en el caso de eldiarioAR es peor: comparte template
    con elDiario.es, así que la plantilla viene en peninsular y ensuciaría
    justamente el eje que mide el registro.
    """

    def test_saca_el_renglon_que_aparece_en_casi_todos(self):
        docs = ['%s\nSuscribite para seguir leyendo.' % t
                for t in ('nota uno larga', 'nota dos larga', 'nota tres larga',
                          'nota cuatro larga', 'nota cinco larga')]
        limpios = construir.quitar_plantilla(docs, umbral=0.2)
        self.assertTrue(all('Suscribite' not in d for d in limpios))
        self.assertIn('nota uno larga', limpios[0])

    def test_no_saca_un_renglon_que_aparece_en_un_solo_documento(self):
        docs = ['propio de esta nota', 'otra cosa', 'otra más', 'y otra', 'y otra más']
        limpios = construir.quitar_plantilla(docs, umbral=0.2)
        self.assertIn('propio de esta nota', limpios[0])

    def test_descarta_los_documentos_que_quedan_vacios(self):
        docs = ['solo plantilla', 'solo plantilla', 'algo propio\nsolo plantilla']
        limpios = construir.quitar_plantilla(docs, umbral=0.5)
        self.assertEqual(limpios, ['algo propio'])


class TestOpenRouter(unittest.TestCase):

    def test_lee_el_env_con_comillas_y_comentarios(self):
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.env', delete=False) as f:
            f.write('# comentario\nOPENROUTER_API_KEY="sk-abc"\n\nOPENROUTER_TEXT_MODEL=openai/x\n')
        env = construir.leer_env(f.name)
        os.remove(f.name)
        self.assertEqual(env['OPENROUTER_API_KEY'], 'sk-abc')
        self.assertEqual(env['OPENROUTER_TEXT_MODEL'], 'openai/x')

    def test_el_pedido_no_lleva_system_prompt(self):
        """Nada de instrucciones de estilo: se mide lo que el modelo escribe por defecto.

        Un system prompt, aunque sea neutro, ya es una instrucción que la gente
        que pega un pedido en el chat no escribe.
        """
        cuerpo = construir.cuerpo_openrouter('openai/x', 'Escribí una landing.')
        self.assertEqual(cuerpo['model'], 'openai/x')
        self.assertEqual([m['role'] for m in cuerpo['messages']], ['user'])
        self.assertIn('Escribí una landing.', cuerpo['messages'][0]['content'])

    def test_el_error_nunca_muestra_la_clave(self):
        mensaje = construir.describir_error(401, '{"error":"bad key sk-secreta"}', 'sk-secreta')
        self.assertNotIn('sk-secreta', mensaje)
        self.assertIn('401', mensaje)


class TestContaminacion(unittest.TestCase):
    """Un texto del corpus de IA que conoce este proyecto no mide el default del
    modelo: mide al modelo obedeciendo a dino. Pasó, con doce textos de Claude."""

    def test_detecta_las_marcas_del_proyecto(self):
        for texto in ('No pude pasarle tools/dino.py porque quedó pendiente.',
                      'El borrador está en el scratchpad.',
                      'Precio: [falta dato] por mes.',
                      'Lo corrí por el linter y dio 5/5.'):
            self.assertTrue(construir.contaminado(texto), texto)

    def test_no_marca_palabras_que_contienen_una_marca(self):
        for texto in ('Traé una linterna para la excursión nocturna.',
                      'El museo tiene un esqueleto de dinosaurio.'):
            self.assertFalse(construir.contaminado(texto), texto)

    def test_no_marca_copy_normal(self):
        self.assertFalse(construir.contaminado(
            'Encontrá tu lugar en Montevideo. Te ayudamos a comprar o alquilar.'))

    def test_el_entorno_limpio_no_hereda_la_sesion_de_claude_code(self):
        sucio = {'HOME': '/h', 'PATH': '/p', 'CLAUDE_CODE_SESSION_ID': 'x',
                 'CLAUDECODE': '1', 'CLAUDE_PID': '9', 'OPENROUTER_API_KEY': 'k'}
        limpio = construir.entorno_limpio(sucio)
        self.assertEqual(limpio.get('HOME'), '/h')
        self.assertEqual(limpio.get('PATH'), '/p')
        for clave in ('CLAUDE_CODE_SESSION_ID', 'CLAUDECODE', 'CLAUDE_PID', 'OPENROUTER_API_KEY'):
            self.assertNotIn(clave, limpio)


if __name__ == '__main__':
    unittest.main(verbosity=2)
