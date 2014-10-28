# coding=utf-8
import unittest
import create_config

class TestCreateConfig(unittest.TestCase):
    """Testes Unitários referentes ao arquivo de configuração"""

    def setUp(self):
        self.config = ''
        self.YESNO = 1
        self.PATH = 2

    def test_yesno(self):
        self.assertTrue(create_config.isvalid_yesno('Yes'))
        self.assertTrue(create_config.isvalid_yesno('Y'))
        self.assertTrue(create_config.isvalid_yesno('N'))
        self.assertTrue(create_config.isvalid_yesno('No'))
        self.assertFalse(create_config.isvalid_yesno('Nasdo'))
        self.assertFalse(create_config.isvalid_yesno(''))

    def test_path(self):
        self.assertEquals(create_config.isvalid_path('/tmp/teste.json'),True)
        self.assertEquals(create_config.isvalid_path('config.json'),True)
        self.assertNotEqual(create_config.isvalid_path(''),True)
        self.assertNotEqual(create_config.isvalid_path('capa.txt'),True)

    def test_ip(self):
        self.assertTrue(create_config.isvalid_ip('127.0.0.1'))

    def test_isvalid(self):
        self.assertTrue(create_config.isvalid('Yes',self.YESNO,'Yes'))
        self.assertFalse(create_config.isvalid('CARA',self.YESNO,'Yes'))
        self.assertTrue(create_config.isvalid('',self.YESNO,'Yes'))

    def test_hint(self):
        yn_hint = "Responda somente YES(y) ou NO(n)"
        yn_path = "Este não é um caminho válido!"
        self.assertEquals(create_config.hint(self.YESNO),yn_hint)
        self.assertNotEqual(create_config.hint(self.YESNO),'aeeoo')
        self.assertEquals(create_config.hint(self.PATH),yn_path)
        self.assertNotEqual(create_config.hint(self.YESNO),'aeeoo')
