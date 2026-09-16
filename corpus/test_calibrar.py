#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests del criterio de admisión. Es la regla que decide qué entra al scorer."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibrar


class TestVeredicto(unittest.TestCase):

    def test_admite_lo_que_es_mucho_más_frecuente_en_texto_de_ia(self):
        v = calibrar.veredicto(apariciones_ia=40, por_10k_ia=8.0, por_10k_humano=0.5,
                               docs_humanos_tocados=0.003)
        self.assertEqual(v.estado, 'admitido')

    def test_rechaza_lo_que_tambien_escriben_los_humanos(self):
        """Ratio de 2x no alcanza. Si la gente también lo escribe, no es un tell."""
        v = calibrar.veredicto(apariciones_ia=40, por_10k_ia=4.0, por_10k_humano=2.0,
                               docs_humanos_tocados=0.003)
        self.assertEqual(v.estado, 'rechazado')

    def test_rechaza_lo_que_dispara_sobre_texto_humano(self):
        """Aunque el ratio dé, si marca uno de cada diez textos humanos llora lobo.

        El techo sale del piso que se le pide al scorer entero, dividido por
        cuántos patrones tiene el catálogo. No es un número aparte.
        """
        v = calibrar.veredicto(apariciones_ia=40, por_10k_ia=50.0, por_10k_humano=0.4,
                               docs_humanos_tocados=0.10)
        self.assertEqual(v.estado, 'rechazado')

    def test_marca_sin_evidencia_cuando_la_muestra_no_alcanza(self):
        """Tres apariciones no dicen nada, ni a favor ni en contra.

        Meterlo igual sería exactamente lo que este proyecto dice no hacer:
        afirmar sin poder mostrar el número.
        """
        v = calibrar.veredicto(apariciones_ia=3, por_10k_ia=0.6, por_10k_humano=0.0,
                               docs_humanos_tocados=0.0)
        self.assertEqual(v.estado, 'sin evidencia')

    def test_el_ratio_es_infinito_si_el_humano_nunca_lo_escribe(self):
        v = calibrar.veredicto(apariciones_ia=40, por_10k_ia=8.0, por_10k_humano=0.0,
                               docs_humanos_tocados=0.0)
        self.assertEqual(v.estado, 'admitido')
        self.assertEqual(v.ratio, float('inf'))

    def test_el_veredicto_dice_por_qué(self):
        """El rechazo tiene que poder publicarse con su número al lado.

        Esa lista es lo que hace defendible al catálogo, así que el motivo no
        es opcional.
        """
        v = calibrar.veredicto(apariciones_ia=40, por_10k_ia=4.0, por_10k_humano=2.0,
                               docs_humanos_tocados=0.003)
        self.assertIn('2.0', v.motivo)


if __name__ == '__main__':
    unittest.main(verbosity=2)
