create or replace function lb2_refresh_clean(p_user in varchar2) return varchar2 is
w_user varchar2(100);
 -- Controlo se todas as sessõees já morreram 0 = dead 1 = alive
is_dead integer := 1;
--Quantidade de usuários logados
w_user_count integer;
begin

  --Primeiro teste: O usuário existe?
  select username into w_user from DBA_USERS where username=p_user;
  --Segundo: Preciso garantir que nenhuma conexão exista no usuário
  DBMS_OUTPUT.PUT_LINE('LB2-Refresh:Clean: Removendo conexões do usuário '
      ||p_user);
  FOR r IN (select sid,serial# from sys.v$session where username = p_user) LOOP
        EXECUTE IMMEDIATE 'alter system kill session ''' || r.sid
          || ',' || r.serial# || '''';
  END LOOP;
  while (is_dead = 1) loop
    DBMS_OUTPUT.PUT_LINE('LB2-Refresh:Clean: Verificando se as conexões foram removidas para o usuário '||p_user);
    select count(*) INTO w_user_count from v$session where username = p_user;
    --Não existe nenhuma conexão, posso prosseguir.
    IF w_user_count = 0 then
      DBMS_OUTPUT.PUT_LINE('LB2-Refresh:Clean: Todas as conexões com o usuário '
      ||p_user||' foram mortas. Prosseguindo...');
      is_dead := 0;
    end if;
  end loop;
  --Agora posso remover o usuário
  DBMS_OUTPUT.PUT_LINE('LB2-Refresh:Clean: Removendo o usuário '
      ||p_user||'...');
  execute immediate 'drop user '||p_user||' cascade';
  RETURN '0:LB2-Refresh:Clean finalizado com sucesso para o usuário '||p_user;

  EXCEPTION
   WHEN NO_DATA_FOUND THEN
      rollback;
      return '1:LB2-Refresh:Clean: Usuário '||p_user||' inexistente.'
      ||'Parando o procedimento!';
    WHEN OTHERS THEN
      rollback;
      return '1:LB2-Refresh:Clean: Erro ao remover o usuário '||p_user
      || '.Parando o procedimento!';
end;
/