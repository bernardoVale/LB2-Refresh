BEGIN
  dbms_output.put_line('INICIO - '||systimestamp||' - Coleta de estatisticas!');
   FOR SCHEM IN (SELECT USERNAME FROM DBA_USERS WHERE ACCOUNT_STATUS='OPEN' AND USERNAME NOT IN
('MGMT_VIEW','SYS','SYSTEM','DBSNMP','SYSMAN','OUTLN','FLOWS_FILES'
,'MDSYS','WMSYS','APPQOSSYS','APEX_030200','OWBSYS_AUDIT'
,'OWBSYS','ORDDATA','ANONYMOUS','EXFSYS','XDB','ORDSYS','CTXSYS','ORDPLUGINS','OLAPSYS'
,'SI_INFORMTN_SCHEMA','SCOTT','XS$NULL','MDDATA','ORACLE_OCM'
,'DIP','APEX_PUBLIC_USER','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR'))
   LOOP
      dbms_output.put_line('INICIO - '||systimestamp||' - Coletando estatisticas do schema:'||schem.USERNAME);
      EXECUTE IMMEDIATE 'BEGIN
      DBMS_STATS.GATHER_SCHEMA_STATS(OWNNAME=> '''||SCHEM.USERNAME||''', CASCADE=> TRUE); END;';
      dbms_output.put_line('FIM - '||systimestamp||' - Coletando estatisticas do schema:'||schem.USERNAME);
   END LOOP;
  dbms_output.put_line('FIM - '||systimestamp||' - Coleta de estatisticas finalizada!');
END;