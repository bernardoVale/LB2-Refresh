# !/usr/bin/python
# -*- coding: utf-8 -*-
import pkgutil
import unittest
import sys

__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'

from lb2refresh import *


class TestCommands(unittest.TestCase):

    def fileToString(self, file):
        with open(file, 'r') as f:
            string = f.read()
        return string

    def setUp(self):
        self.r = LB2Refresh()
    def test_imported_successful(self):
        #Exemplares de sucesso
        #/Users/bernardovale/PycharmProjects/LB2-Refresh/unit_test/utils-tests.py
        self.assertTrue(
            self.r.imported_successful(self.fileToString('../tests/impdp_sucess01.txt')))
        self.assertTrue(
            self.r.imported_successful(self.fileToString('../tests/impdp_sucess02.txt')))
        # IMPDP Com erros fatais
        self.assertFalse(
            self.r.imported_successful(self.fileToString('../tests/impdp_failure01.txt')))
        self.assertFalse(
            self.r.imported_successful(self.fileToString('../tests/impdp_failure02.txt')))
        self.assertFalse(
            self.r.imported_successful(self.fileToString('../tests/impdp_failure03.txt')))
        self.assertFalse(
            self.r.imported_successful(self.fileToString('../tests/impdp_failure04.txt')))

    def test_refresh_status(self):
        RefreshUtils.refresh_status('oi')
        self.assertEquals(self.fileToString('status.txt'), 'oi')

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
        output, err = RefreshUtils.call_command('echo -n teste')
        self.assertEqual('teste', output)

        print err
        print output


class TestConfigFile(unittest.TestCase):
    """Testes Unitários referentes ao arquivo de configuração"""

    def setUp(self):
        self.r = LB2Refresh()
        self.r.read_config('config.json')

    def test_file_exists(self):
        """ Testa se os arquivos existem """

        cfg = RefreshUtils.file_exists('config.json')
        cfg2 = RefreshUtils.file_exists('arquivoinexistente.txt')
        self.assertEqual(cfg, True)
        self.assertEqual(cfg2, False)

    def test_config_open(self):
        '''Testa se o JSON foi aberto corretamente'''
        self.assertIsInstance(self.r.config, dict)

    def test_backup_exists(self):
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
        self.assertEqual(file, 'teste.dmp')
        self.assertEqual(file2, 'teste.dmp')
