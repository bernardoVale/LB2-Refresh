# coding=utf-8
import logging
import paramiko
from utils.lb2refresh_utils import RefreshUtils

__author__ = 'bernardovale'


class SSH:

    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port

    def connect(self):
        """
        Realiza a conexão ssh pelo paramiko e retorna
        um canal de comunicação
        :return: SSHClient
        """
        logging.debug("Método connect")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            logging.info("Iniciando conexão ssh...")
            ssh.connect(self.ip, username=self.username,
                        password=self.password, port=self.port, timeout=120)
        except:
            RefreshUtils.leave_with_message("Impossível conectar com as"
                                            " credências e/ou timeout excedido (120 segundos)")
        logging.info("Conexão estabelecida com host remoto %s retornando conexão...", self.ip)
        return ssh

    def run_cmd(self, cmd):
        """
        Executa um comando no host remoto
        :param cmd: comando a ser executado
        :return: List do stdout
        """
        logging.debug("Método run_cmd")
        ssh = self.connect()
        stdin, stdout, stderr = ssh.exec_command(cmd)
        error_list = stderr.readlines()
        out_list = stdout.readlines()
        print out_list
        print error_list
        if len(error_list) != 1:
            RefreshUtils.leave_with_message("Erro ao executar comando remoto. Resposta:" + str(error_list) + "")
        return out_list


def run_remote(cmd, ip, username, password, port=22):
    """
    Método para esconder a complexidade da classe
    :param cmd: comando
    :param ip: ip
    :param username: user
    :param password: senha
    :param port: porta do ssh
    :return: List com o resultado.
    """
    logging.debug("Método run_remote")
    ssh = SSH(ip, username, password, port)
    return ssh.run_cmd(cmd)