#!/usr/bin/python
# -*- coding: utf-8 -*-
from pprint import pprint
import unittest

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
        self.assertEqual(self.r.config.senha, 'refresh')
        self.assertEqual(self.r.config.ospwd, 'oracle')
        self.assertEqual(self.r.config.osuser, 'oracle')
        self.assertEqual(self.r.config.user, 'lb2_refresh')
        self.assertEqual(self.r.config.var_dir, '/home/oracle/.bash_profile')
        self.assertEqual(self.r.config.directory, 'DATAPUMP')
        self.assertEqual(self.r.config.backup_file, '/Users/bernardovale/dpfull.dmp')
        self.assertEqual(self.r.config.logfile, 'import_tasy.log')
        self.assertEqual(self.r.config.schemas, ['TASY'])
        self.assertEqual(self.r.config.coletar_estatisticas, 'false')

class TestOracle(unittest.TestCase):
    """ Testes referentes a conectividade com o
        banco de Dados Oracle
    """
    def setUp(self):
        self.r = LB2Refresh()
        self.conn = ""
        self.r.readConfig('/Users/bernardovale/Documents/LB2/scripts/lb2_refresh/config.json')
        self.r.buildConfig()

    def test_connection(self):
        c = Config()
        c.senha = 'oracle'
        c.sid = 'oradb'
        c.user = 'sys'
        c.ip = "10.200.0.204"
        mustByConnection = self.r.estabConnection(c)
        self.assertIsInstance(mustByConnection,cx_Oracle.Connection)

    def test_lb2refresh_clean(self):
        """
        Testa a função LB2-Refresh-Clean
        Se envio um usuário inválido o primeiro caracter deverá ser 1
        Caso tudo OK 0
        :return:
        """
        c = Config()
        c.senha = 'oracle'
        c.sid = 'oradb'
        c.user = 'sys'
        c.ip = "10.200.0.204"
        c.schemas = "CARALHUDO"
        con = self.r.estabConnection(c)
        cursor = con.cursor()
        cursor.execute("create user capa identified by capa")
        cur = con.cursor()
        res  = cur.callfunc('lb2_refresh_clean', cx_Oracle.STRING, ['CAPA'])
        self.assertEqual(res[0:1],"0")
        res  = cur.callfunc('lb2_refresh_clean', cx_Oracle.STRING, ['CAPACAPUDO'])
        self.assertEqual(res[0:1],"1")
        cur.close()
        con.close()

    def test_check_host(self):
        """
        Verifica a conectividade com o host
        :return:
        """
        teste = self.r.runRemote("echo -n teste")
        self.assertEqual(teste,"teste")

    def test_oracleVariables(self):
         """
         Verifica as variáveis de ambiente.
         :return:
         """
         isOk = self.r.checkOraVariables()
         self.assertEqual(isOk,True)

    def test_hasRefresh_clean(self):
        """
        Verifica se a procedure lb2_refresh_clean.sql existe no banco!
        :return:
        """
        c = Config()
        c.senha = 'oracle'
        c.sid = 'oradb'
        c.user = 'sys'
        c.ip = "10.200.0.204"
        sql = 'select status from dba_objects where object_name=\'LB2_REFRESH_CLEAN\''
        print sql
        con = self.r.estabConnection(c)
        cur = con.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        self.assertNotEqual(result,[])
        self.assertEqual([result[0][0]],['VALID'])
        cur.close()
        con.close()

if __name__ == '__main__':
    unittest.main()
