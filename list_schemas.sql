set head off;
select '"SCHEMAS": [' FROM DUAL;
select '"'||username||'",' from dba_users where default_tablespace='TS_DT_CLIENTES';