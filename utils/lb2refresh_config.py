# coding=utf-8
import logging
import datetime

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
                self.sid = config['destino']['sid']
                self.ip = config['destino']['ip']
                self.user = config['destino']['user']
                self.senha = config['destino']['senha']
                self.directory = config['destino']['directory']
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
                # Variáveis opcionais
                if 'datapump_options' in config:
                    if 'remap_tablespace' in config['datapump_options']:
                        self.remap_tablespace = config['datapump_options']['remap_tablespace']
                    if 'remap_schema' in config['datapump_options']:
                        self.remap_schema = config['datapump_options']['remap_schema']
            except (KeyError, NameError):
                logging.error("Falha ao ler um dos parametros."
                              " Verifique o JSON de configuração")
                exit(2)

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
