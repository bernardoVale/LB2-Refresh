#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'

from lb2refresh import *


class TestCommands(unittest.TestCase):

    def fileToString(self,file):
        with open(file,'r') as f:
            string = f.read()
        return string

    def setUp(self):
        self.r = LB2Refresh()

    def test_imported_successful(self):
        #Exemplares de sucesso
        self.assertTrue(
        self.r.imported_successful(self.fileToString('tests/impdp_sucess01.txt')))
        self.assertTrue(
        self.r.imported_successful(self.fileToString('tests/impdp_sucess02.txt')))
        # IMPDP Com erros fatais
        self.assertFalse(
        self.r.imported_successful(self.fileToString('tests/impdp_failure01.txt')))
        self.assertFalse(
        self.r.imported_successful(self.fileToString('tests/impdp_failure02.txt')))
        self.assertFalse(
        self.r.imported_successful(self.fileToString('tests/impdp_failure03.txt')))
        self.assertFalse(
        self.r.imported_successful(self.fileToString('tests/impdp_failure04.txt')))

    def test_refresh_status(self):
        RefreshUtils.refresh_status('oi')
        self.assertEquals(self.fileToString('status.txt'),'oi')

    def test_restartdatabase(self):
        log = "SQL> shutdown abort; \
        ORACLE instance shut down. \
        SQL> startupORA-32004: obsolete or deprecated parameter(s) specified for RDBMS instance \
                ORACLE instance started. \
                \
        Total System Global Area 1068937216 bytes \
        Fixed Size		    2260088 bytes \
        Variable Size		  813695880 bytes \
        Database Buffers	  247463936 bytes \
        Redo Buffers		    5517312 bytes \
        Database mounted. \
        Database opened."
        log_error_1 = "ORA-27154: post/wait create failed \
ORA-27300: OS system dependent operation:semids_per_proc failed with status: 0 \
ORA-27301: OS failure message: Error 0 \
ORA-27302: failure occurred at: sskgpwcr2 \
ORA-27303: additional information: semids = 524, maxprocs = 100000"
        log_error_2 = "SQL> shutdown abort; \
        ORACLE instance shut down. \
        SQL> startupORA-32004: Could not open database."
        self.assertTrue(RefreshUtils.restarted_successful(log))
        self.assertTrue(RefreshUtils.restarted_successful(log))
        self.assertFalse(RefreshUtils.restarted_successful(log_error_1))
        self.assertFalse(RefreshUtils.restarted_successful(log_error_2))

    def test_command(self):
        """
        Testa a execução de um comando simples via subprocess
        :return:
        """
        output,err = RefreshUtils.call_command('echo -n teste')
        self.assertEqual('teste',output)

        print err
        print output

class TestConfigFile(unittest.TestCase):
    """Testes Unitários referentes ao arquivo de configuração"""

    def setUp(self):
        self.r = LB2Refresh()
        self.r.read_config('config.json')

    def test_fileExists(self):
        """ Testa se os arquivos existem """

        cfg = RefreshUtils.file_exists('config.json')
        cfg2 = RefreshUtils.file_exists('arquivoinexistente.txt')
        self.assertEqual(cfg, True)
        self.assertEqual(cfg2, False)

    def test_configOpen(self):
        '''Testa se o JSON foi aberto corretamente'''
        self.assertIsInstance(self.r.config, dict)

    def test_backupExists(self):
        '''Testa a propriedade backup_file do arquivo JSON'''

        self.assertEqual(self.r.config['backup_file'], '/u01/app/oracle/backup/dpfull_$DATA.dmp')
        self.assertEqual(RefreshUtils.file_exists(self.r.config['backup_file']), False)

    def test_truncate_file_dir(self):
        """
        Testa o mecanismo de remoção do path do backup.
        exemplo: /home/oracle/teste.log deve tornar teste.log com esse método
        :return:
        """
        file = RefreshUtils.capped_file_path('/u01/app/oracle/backup/datapump/teste.dmp')
        file2 = RefreshUtils.capped_file_path('teste.dmp')
        self.assertEqual(file,'teste.dmp')
        self.assertEqual(file2,'teste.dmp')

class TestOracle(unittest.TestCase):
    """ Testes referentes a conectividade com o
        banco de Dados Oracle
    """
    def setUp(self):
        self.r = LB2Refresh()
        self.conn = ""
        self.r.read_config('config.json')
        self.r.build_config()

    def test_procedure_is_valid(self):
        """
        Verifica se a procedure do LB2_REFRESH existe e está valida.
        :return:
        """
        self.r.config.user = 'system'
        query = 'set head off \n' \
              'select status from dba_objects where object_name=\'LB2_REFRESH_CLEAN\';'
        result = self.r.run_query(query,True)
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
        result = self.r.run_query(query,False)
        self.assertEqual(result,'')

    def test_lb2refresh_clean_v2(self):
        """
        Teste da procedure com chamada via sqlplus
        :return:
        """
        x = lambda y: True if 'Resultado:0:' in y else False
        sql = "create user capa identified by capudo;"
        schema = "CAPA"
        r = self.r.run_query(sql,False)
        print r
        sql = "set serveroutput on; \n" \
              "declare \n" \
              "r varchar2(4000); \n" \
              "begin \n" \
              "r := lb2_refresh_clean('"+schema+"'); \n" \
              "dbms_output.put_line('Resultado:' || r); \n" \
              "end; \n" \
              "/"
        r = self.r.run_query(sql,True)
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
        r = self.r.run_query(sql,False)
        print r
        self.assertEqual(x(r),False)

    def test_oracleVariables(self):
         """
         Verifica as variáveis de ambiente.
         :return:
         """
         isOk = self.r.check_ora_variables()
         self.assertEqual(isOk,True)

    # def test_hasRefresh_clean(self):
    #     """
    #     Verifica se a procedure lb2_refresh_clean.sql existe no banco!
    #     :return:
    #     """
    #     c = Config()
    #     c.senha = 'oracle'
    #     c.sid = 'oradb'
    #     c.user = 'sys'
    #     c.ip = "10.200.0.204"
    #     sql = 'select status from dba_objects where object_name=\'LB2_REFRESH_CLEAN\''
    #     print sql
    #     con = self.r.estabConnection(c)
    #     cur = con.cursor()
    #     cur.execute(sql)
    #     result = cur.fetchall()
    #     self.assertNotEqual(result,[])
    #     self.assertEqual([result[0][0]],['VALID'])
    #     cur.close()
    #     con.close()

if __name__ == '__main__':
    unittest.main()
