#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests del descubrimiento de patrones. Lo que importa acá es lo que NO debe
aparecer: una palabra de tema, o algo que la gente también escribe."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import descubrir

HUMANOS = ['el gobierno anunció medidas nuevas para el sector'] * 400 + \
          ['la ciudad amaneció con lluvia y frío intenso'] * 400


class TestNgramas(unittest.TestCase):

    def test_arma_los_ngramas_sin_puntuacion(self):
        self.assertEqual(descubrir.ngramas('Hola, mundo feliz.', 2), {'hola mundo', 'mundo feliz'})

    def test_conserva_las_tildes(self):
        self.assertIn('acá está', descubrir.ngramas('Acá está.', 2))


class TestSobrerrepresentados(unittest.TestCase):

    def test_encuentra_la_frase_de_todos_los_textos_de_ia(self):
        ia = ['sin vueltas te lo resolvemos en %d días' % i for i in range(20)]
        hallados = [h['frase'] for h in descubrir.sobrerrepresentados(ia, HUMANOS, 2, 5)]
        self.assertIn('sin vueltas', hallados)

    def test_no_encuentra_la_palabra_de_un_solo_texto(self):
        """Un texto sobre café repite «café» veinte veces. Eso es tema, no acento.

        Por eso se cuenta en cuántos textos aparece, no cuántas veces.
        """
        ia = ['café café café de especialidad'] + ['texto número %d distinto' % i for i in range(19)]
        hallados = [h['frase'] for h in descubrir.sobrerrepresentados(ia, HUMANOS, 1, 5)]
        self.assertNotIn('café', hallados)

    def test_no_encuentra_lo_que_la_gente_tambien_escribe(self):
        ia = ['el gobierno anunció algo %d' % i for i in range(20)]
        hallados = [h['frase'] for h in descubrir.sobrerrepresentados(ia, HUMANOS, 2, 5)]
        self.assertNotIn('el gobierno', hallados)


if __name__ == '__main__':
    unittest.main(verbosity=2)
