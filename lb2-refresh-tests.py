# coding=utf-8
__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'

from lb2Refresh import *
import cx_Oracle

class TestConfigFile(unittest.TestCase):
    """Testes Unitários referentes ao arquivo de configuração"""

    def setUp(self):
        self.r = LB2Refresh()

    def test_fileExists(self):
        """ Testa se os arquivos existem """

        cfg = self.r.fileExists('/Users/bernardovale/config.json')
        cfg2 = self.r.fileExists('/Users/bernardovale/arquivoinexistente.txt')
        self.assertEqual(cfg, True)
        self.assertEqual(cfg2, False)

    def test_configOpen(self):
        '''Testa se o JSON foi aberto corretamente'''

        self.r.readConfig('/Users/bernardovale/Documents/LB2/scripts/lb2_refresh/config.json')
        self.assertIsInstance(self.r.config, dict)

    def test_backupExists(self):
        '''Testa a propriedade backup_file do arquivo JSON'''

        self.r.readConfig('/Users/bernardovale/Documents/LB2/scripts/lb2_refresh/config.json')
        self.assertEqual(self.r.config['backup_file'], '/Users/bernardovale/dpfull.dmp')
        self.assertEqual(self.r.fileExists(self.r.config['backup_file']), True)

    def test_config_properties(self):
        '''Testa todas as propriedades do JSON'''

        self.r.readConfig('/Users/bernardovale/Documents/LB2/scripts/lb2_refresh/config.json')
        self.r.buildConfig()
        self.assertEqual(self.r.config.ip, '10.200.0.116')
        self.assertEqual(self.r.config.sid, 'rest')
        self.assertEqual(self.r.config.senha, 'oracle')
        self.assertEqual(self.r.config.user, 'system')
        self.assertEqual(self.r.config.directory, 'DATAPUMP')
        self.assertEqual(self.r.config.backup_file, '/Users/bernardovale/dpfull.dmp')
        self.assertEqual(self.r.config.log_dir, '/u01/app/oracle/backup/log')
        self.assertEqual(self.r.config.schemas, ['OE', 'SCOTT', 'SH'])
        self.assertEqual(self.r.config.coletar_estatisticas, 'false')

class TestOracle(unittest.TestCase):
    """ Testes referentes a conectividade com o
        banco de Dados Oracle
    """
    def setUp(self):
        self.r = LB2Refresh()
        self.conn = ""

    def test_connection(self):
        c = Config()
        c.senha = 'oracle'
        c.sid = 'rest'
        c.user = 'system'
        c.ip = "10.200.0.116"
        mustByConnection = self.r.estabConnection(c)
        self.assertIsInstance(mustByConnection,cx_Oracle.Connection)

if __name__ == '__main__':
    unittest.main()
