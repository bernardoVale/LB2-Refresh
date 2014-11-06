#!/bin/bash
#-------------------------------------------------------------
#       Script de Status - LB2 Refresh
#
#       Autor: Bernardo S E Vale
#       Data:   05/11/2014
#       email: bernardo.vale@lb2.com.br
#       LB2 Consultoria - Leading Business 2 the Next Level!
#-------------------------------------------------------------
export LB2REFRESH_HOME=/home/suporte/lb2refresh
SHUTDOWN_WAIT=20
lb2refresh_pid() {
    echo `ps aux | grep lb2Refresh_v2.py | grep -v grep | awk '{ print $2 }'`
}
impdp_pid(){
   echo `ps aux | grep impdp | grep -v grep | awk '{ print $2 }'`
}
start() {
    pid=$(lb2refresh_pid)
    if [ -n "$pid" ]
    then
        echo "ERRO - A atualizacao ja foi iniciada, aguarde o final (pid: $pid)"
	    echo "Caso seja necessario, finalize o atualizacao no menu de suporte"
    else
        echo "Iniciando LB2-Refresh"
	    $LB2REFRESH_HOME/lb2Refresh_v2.py --config config.json --sendbackup --coletar --posscript $LB2REFRESH_HOME/pos_import.sql --log $LB2REFRESH_HOME &
    fi
    return 0
}
status(){
    pid=$(lb2refresh_pid)
    if [ -n "$pid" ]
    then
       echo "Atualizacao em andamento - OK - PID: $pid"
        cat status.txt
    else
        if [ -a status.txt ]
        then
            GOT=`cat status.txt`
            EXPECTED="LB2 REFRESH FINALIZADO!"
            if [ "$GOT" = "$EXPECTED" ]
            then
                echo "Atualizacao finalizada com sucesso - OK"
                rm -rf status.txt
            else
                echo "Script finalizado antecipadamente - ERROR"
                echo "Verifique os logs do LB2 Refresh"
            fi
        else
            echo "Nenhuma atualizacao em Andamento - ERROR"
        fi
    fi
    return 0
}
stop() {
    pid=$(lb2refresh_pid)
    if [ -n "$pid" ]
    then
        echo "Parando o LB2 Refresh..."
	kill $pid
        let kwait=$SHUTDOWN_WAIT
        count=0
        count_by=5
        until [ `ps -p $pid | grep -c $pid` = '0' ] || [ $count -gt $kwait ]
        do
            echo "Aguardando o fim do processo. Timeout para remover a forca o pid: ${count}/${kwait}"
            sleep $count_by
            let count=$count+$count_by;
        done
        if [ $count -gt $kwait ]; then
            echo "Matando o processo que nao parou apos $SHUTDOWN_WAIT segundos"
            kill -9 $pid
        fi
    else
	    pid=$(impdp_pid)
	    if [ -n "$pid" ]
	    then
		    echo "Parando o Oracle Datapump - Import"
            kill $pid
            let kwait=$SHUTDOWN_WAIT
            count=0
            count_by=5
            until [ `ps -p $pid | grep -c $pid` = '0' ] || [ $count -gt $kwait ]
    	    do
        	    echo "Aguardando o fim do processo. Timeout para remover a forca o pid: ${count}/${kwait}"
        	    sleep $count_by
        	    let count=$count+$count_by;
    	    done
    	    if [ $count -gt $kwait ]; then
        	    echo "Matando o processo que nao parou apos $SHUTDOWN_WAIT segundos"
        	    kill -9 $pid
    	    fi
	    else
        	echo "Nenhuma atualizacao em andamento!"
    	fi
    fi
    return 0
}

case $1 in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
       status
	    ;;
esac

exit 0