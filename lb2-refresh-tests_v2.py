#!/usr/bin/python
# -*- coding: utf-8 -*-
from pprint import pprint
from subprocess import PIPE, Popen
import unittest
import re

__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'

from lb2Refresh_v2 import *

class TestCommands(unittest.TestCase):

    def setUp(self):
        self.r = LB2Refresh()

    def test_command(self):
        """
        Testa a execução de um comando simples via subprocess
        :return:
        """
        output,err = self.r.call_command('echo -n teste')
        self.assertEqual('teste',output)

        print err
        print output

class TestConfigFile(unittest.TestCase):
    """Testes Unitários referentes ao arquivo de configuração"""

    def setUp(self):
        self.r = LB2Refresh()
        self.r.readConfig('config.json')

    def test_fileExists(self):
        """ Testa se os arquivos existem """

        cfg = self.r.fileExists('config.json')
        cfg2 = self.r.fileExists('arquivoinexistente.txt')
        self.assertEqual(cfg, True)
        self.assertEqual(cfg2, False)

    def test_configOpen(self):
        '''Testa se o JSON foi aberto corretamente'''
        self.assertIsInstance(self.r.config, dict)

    def test_backupExists(self):
        '''Testa a propriedade backup_file do arquivo JSON'''

        self.assertEqual(self.r.config['backup_file'], '/backup/datapump/dpfull_20140805.dmp')
        self.assertEqual(self.r.fileExists(self.r.config['backup_file']), True)

    def test_truncate_file_dir(self):
        """
        Testa o mecanismo de remoção do path do backup.
        exemplo: /home/oracle/teste.log deve tornar teste.log com esse método
        :return:
        """
        file = self.r.cappedFilePath('/u01/app/oracle/backup/datapump/teste.dmp')
        file2 = self.r.cappedFilePath('teste.dmp')
        self.assertEqual(file,'teste.dmp')
        self.assertEqual(file2,'teste.dmp')

class TestOracle(unittest.TestCase):
    """ Testes referentes a conectividade com o
        banco de Dados Oracle
    """
    def setUp(self):
        self.r = LB2Refresh()
        self.conn = ""
        self.r.readConfig('config.json')
        self.r.buildConfig()

    def test_procedure_is_valid(self):
        """
        Verifica se a procedure do LB2_REFRESH existe e está valida.
        :return:
        """
        self.r.config.user = 'system'
        query = 'set head off \n' \
              'select status from dba_objects where object_name=\'LB2_REFRESH_CLEAN\';'
        result = self.r.run_sqlplus(query,True,False)
        self.assertEqual('VALID',result)

    def test_compile(self):
        """
        Testa a recompilação de objetos
        :return:
        """
        #Esse método so vai funcionar se estiver no Oracle server
        #Esse método deve falhar!

        self.r.config.user = 'sys'
        query = '@$ORACLE_HOME/rdbms/admin/utlrp.sql'
        result = self.r.run_sqlplus(query,False,True)
        self.assertEqual(result,'')

    def test_lb2refresh_clean_v2(self):
        """
        Teste da procedure com chamada via sqlplus
        :return:
        """
        x = lambda y: True if 'Resultado:0:' in y else False
        sql = "create user capa identified by capudo;"
        schema = "CAPA"
        r = self.r.run_sqlplus(sql,False,True)
        print r
        sql = "set serveroutput on; \n" \
              "declare \n" \
              "r varchar2(4000); \n" \
              "begin \n" \
              "r := lb2_refresh_clean('"+schema+"'); \n" \
              "dbms_output.put_line('Resultado:' || r); \n" \
              "end; \n" \
              "/"
        r = self.r.run_sqlplus(sql,True,True)
        print r
        self.assertEqual(x(r),True)
        sql = "set serveroutput on; \n" \
              "declare \n" \
              "r varchar2(4000); \n" \
              "begin \n" \
              "r := lb2_refresh_clean('CAPUDOSO'); \n" \
              "dbms_output.put_line('Resultado:' || r); \n" \
              "end; \n" \
              "/"
        r = self.r.run_sqlplus(sql,False,True)
        print r
        self.assertEqual(x(r),False)

    def test_oracleVariables(self):
         """
         Verifica as variáveis de ambiente.
         :return:
         """
         isOk = self.r.checkOraVariables_v2()
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
