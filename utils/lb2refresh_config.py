# coding=utf-8
import logging
import datetime
from utils.datapump_dir_utils import DatapumpDir

__author__ = 'bernardovale'


class Config:
    """
        Objeto de Configuração
        do LB2-Refresh
    """
    # DECLARAÇÃO DAS ANNOTATIONS
    DATA = "$DATA"
    annotations_dict = {DATA: datetime.datetime.now().strftime("%Y%m%d")}

    def __init__(self, config=None):
        # Necessário pois as vezes chamo esse método sem passar um dict
        if isinstance(config, dict):
            # Esses parametros entram no try pois são obrigatórios.
            logging.debug("Método __init__ Config")

            try:
                # Instanciando o DatapumpDir
                self.dirs = DatapumpDir()
                self.sid = config['destino']['sid']
                self.ip = config['destino']['ip']
                self.user = config['destino']['user']
                self.senha = config['destino']['senha']

                #self.directory = config['destino']['directory']
                self.backup_file = self.parse_annotations(config['backup_file'])
                self.logfile = self.parse_annotations(config['logfile'])
                self.schemas = config['schemas']
                self.osuser = config['destino']['osuser']
                self.ospwd = config['destino']['ospwd']
                self.var_dir = config['destino']['var_dir']
                if 'remetente' in config:
                    self.rem_ip = config['remetente']['ip']
                    self.rem_osuser = config['remetente']['osuser']
                    self.rem_ospwd = config['remetente']['ospwd']
                    self.rem_backup_file = self.parse_annotations(config['remetente']['backup_file'])
                    # Opcionais, necessario para o modulo do backup (expdp)
                    if 'senha' in config['remetente']:
                        self.rem_senha = config['remetente']['senha']
                    if 'sid' in config['remetente']:
                        self.rem_sid = config['remetente']['sid']
                    if 'user' in config['remetente']:
                        self.rem_user = config['remetente']['user']
                    if 'var_dir' in config['remetente']:
                        self.rem_var_dir = config['remetente']['var_dir']
                    if 'directory' in config['remetente']:
                        self.rem_directory = config['remetente']['directory']
                # Variáveis opcionais
                if 'datapump_options' in config:
                    if 'remap_tablespace' in config['datapump_options']:
                        self.remap_tablespace = config['datapump_options']['remap_tablespace']
                    if 'remap_schema' in config['datapump_options']:
                        self.remap_schema = config['datapump_options']['remap_schema']

                logging.info("Populando os dados referente ao Directory do DATAPUMP")
                self.find_datapump_directories()
            except (KeyError, NameError) as e:
                logging.error("Falha ao ler um dos parametros."
                              " Verifique o JSON de configuração: Param: %s", e)
                exit(2)

    def find_datapump_directories(self):
        """
        Popula os diretorios do datapump no Config
        :return:
        """
        logging.debug("Método find_datapump_directories")
        #Atualizando o DatapumpDir
        self.dirs.config = self
        self.dirs.check_for_imp_dir()

    def parse_annotations(self, text):
        """
        Verifica se a variavel possui alguma annotation conhecida
        Caso tenha, substitui pelo valor da annotation
        :param text: Valor da variavel
        :return: Variavel com as substituicoes dos annotations
        """
        logging.debug("Método parse_annotations")
        for annoatition in self.annotations_dict.keys():
            if annoatition in text:
                text = str(text).replace(annoatition, self.annotations_dict[annoatition])
        return text

    def clean_if_need(self):
        """
        Limpa o diretório temporário se necessário
        :return:
        """
        logging.debug("Método clean_if_need")
        self.dirs.drop_imp_temp_directory()