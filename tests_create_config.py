# coding=utf-8
import unittest
import create_config

class TestCreateConfig(unittest.TestCase):
    """Testes Unitários referentes ao arquivo de configuração"""

    def setUp(self):
        self.config = ''
        self.YESNO = 1
        self.PATH = 2
        self.IP = 3
        self.TEXT = 4
        self.LOG = 5
        self.DMP = 6
        self.SCHEMAS = 7
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

    def test_dump(self):
        self.assertEquals(create_config.isvalid_dump('/tmp/teste.dmp'),True)
        self.assertEquals(create_config.isvalid_dump('config.dmp'),True)
        self.assertNotEqual(create_config.isvalid_dump(''),True)
        self.assertNotEqual(create_config.isvalid_dump('capa.txt'),True)

    def test_log(self):
        self.assertEquals(create_config.isvalid_log('/tmp/teste.log'),True)
        self.assertEquals(create_config.isvalid_log('config.log'),True)
        self.assertNotEqual(create_config.isvalid_log(''),True)
        self.assertNotEqual(create_config.isvalid_log('capa.txt'),True)

    def test_ip(self):
        self.assertTrue(create_config.isvalid_ip('127.0.0.1'))

    def test_isvalid(self):
        self.assertTrue(create_config.isvalid('Yes',self.YESNO,'Yes'))
        self.assertFalse(create_config.isvalid('CARA',self.YESNO,'Yes'))
        self.assertFalse(create_config.isvalid('',self.YESNO,'Yes'))

    def test_text(self):
        self.assertTrue(create_config.isvalid_text('oracle'))
        self.assertTrue(create_config.isvalid_text('oracle!@#!'))
        self.assertFalse(create_config.isvalid_text(' oracle'))
        self.assertFalse(create_config.isvalid_text(' SADDAS   '))

    def test_schemas(self):
        self.assertTrue(create_config.isvalid_schemas('TASY,CAP'))
        self.assertTrue(create_config.isvalid_schemas('TASY'))
        self.assertFalse(create_config.isvalid_schemas('TASY ,CAPA'))
        self.assertFalse(create_config.isvalid_schemas(' '))
        self.assertFalse(create_config.isvalid_schemas('SYS'))
        self.assertFalse(create_config.isvalid_schemas('TASY,SYSTEM'))
        self.assertFalse(create_config.isvalid_schemas('TASY,SYS'))

    def test_remap(self):
        self.assertTrue(create_config.isvalid_remap('CAPA:CAPUDO,CAP:CAPE'))
        self.assertTrue(create_config.isvalid_remap('SALES_DATA:SALES'))
        self.assertFalse(create_config.isvalid_remap('RAxDISCAL,LK'))
        self.assertFalse(create_config.isvalid_remap('home : docampu'))

    def test_hint(self):
        yn_hint = "Responda somente YES(y) ou NO(n)"
        yn_path = "Este não é um JSON válido!"
        yn_text = "Resposta inválida, remova os espaços em branco!"
        yn_ip = "Não é um IP válido!"
        yn_log = "Resposta inválida, o arquivo deve ter extensão .log!"
        yn_dmp = "Resposta inválida, o arquivo deve ter extensão .dmp!"
        yn_schemas = "Schemas inválidos, garanta que não exista espaço ou que não " \
               "tenha inserido schemas do sistema (SYS,SYSTEM)"
        self.assertEquals(create_config.hint(self.YESNO),yn_hint)
        self.assertNotEqual(create_config.hint(self.YESNO),'aeeoo')
        self.assertEquals(create_config.hint(self.PATH),yn_path)
        self.assertNotEqual(create_config.hint(self.PATH),'aeeoo')
        self.assertEquals(create_config.hint(self.IP),yn_ip)
        self.assertNotEqual(create_config.hint(self.IP),'aeeoo')
        self.assertEquals(create_config.hint(self.TEXT),yn_text)
        self.assertNotEqual(create_config.hint(self.TEXT),'aeeoo')
        self.assertEquals(create_config.hint(self.LOG),yn_log)
        self.assertNotEqual(create_config.hint(self.LOG),'aeeoo')
        self.assertEquals(create_config.hint(self.DMP),yn_dmp)
        self.assertNotEqual(create_config.hint(self.DMP),'aeeoo')
        self.assertEquals(create_config.hint(self.SCHEMAS),yn_schemas)
        self.assertNotEqual(create_config.hint(self.SCHEMAS),'aeeoo')
