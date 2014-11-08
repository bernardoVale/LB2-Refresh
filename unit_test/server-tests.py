# coding=utf-8
import unittest
from lb2refresh import LB2Refresh

__author__ = 'bernardovale'

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