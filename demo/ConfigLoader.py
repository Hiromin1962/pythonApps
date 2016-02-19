# -*- coding: utf-8 -*-
'''
Created on 2016/02/18
settings.iniファイルからユーザ設定をLoadする
settings.iniファイルに基本的な情報を記載しておき、
こちらのクラスを用いてデータを受け取る
@author: okada
'''
import ConfigParser

CONFIG_FILE = 'settings.ini'

class ConfigLoader(object):
    '''
    classdocs
    '''
    initItems = {'OutputFolder':'Folder','StartFolder':'Folder','DefaultHome':'Folder',
                 'MaxSearchNum':'Other', 'OtherPort':'Other','ClientId':'Auth','ClientSecret':'Auth'}
    def __init__(self):
        '''
        Constructor
        '''
        conf = ConfigParser.SafeConfigParser()

        try:
            conf.read(CONFIG_FILE)
        except Exception as e:
            print e
            return None

        for key, value in self.initItems.iteritems():
            try:
                exec("self.%s=conf.get('%s', '%s')" % (key,value,key))
            except Exception as e:
                print e
                # propertyがiniファイルに存在しない場合は、''を大入しておく。
                exec("self.%s=''" % (key))
            
    def get_default_home(self):
        return self.__DefaultHome

    def set_default_home(self, value):
        self.__DefaultHome = value

    def del_default_home(self):
        del self.__DefaultHome

    def get_start_folder(self):
        return self.__StartFolder

    def set_start_folder(self, value):
        self.__StartFolder = value

    def del_start_folder(self):
        del self.__StartFolder
 
    def get_output_folder(self):
        return self.__OutputFolder

    def set_output_folder(self, value):
        self.__OutputFolder = value

    def del_output_folder(self):
        del self.__OutputFolder

    def get_max_search_num(self):
        return self.__MaxSearchNum

    def set_max_search_num(self, value):
        self.__MaxSearchNum = value

    def del_max_search_num(self):
        del self.__MaxSearchNum
              
    def get_client_id(self):
        return self.__ClientId

    def set_client_id(self, value):
        self.__ClientId = value

    def del_client_id(self):
        del self.__ClientId

    def get_client_secert(self):
        return self.__ClientSecret

    def set_client_secret(self, value):
        self.__ClientSecret = value

    def del_client_secret(self):
        del self.__ClientSecret

    def get_other_port(self):
        return self.__OtherPort

    def set_other_port(self, value):
        self.__OtherPort = value

    def del_other_port(self):
        del self.__OtherPort
                        
    DefaultHome = property(get_default_home, set_default_home, del_default_home, "Default Doc Home's docstring")
    StartFolder = property(get_start_folder, set_start_folder, del_start_folder, "Start Folder's docstring")
    OutputFolder = property(get_output_folder, set_output_folder, del_output_folder, "Output Folder's docstring")
    MaxSearchNum = property(get_max_search_num, set_max_search_num, del_max_search_num, "Maximun search number's docstring")
    ClientId = property(get_client_id, set_client_id, del_client_id, "Box API Client ID's docstring")
    ClientSecret = property(get_client_secert, set_client_secret, del_client_secret, "Box API Client Secret's docstring")
    OtherPort = property(get_other_port, set_other_port, del_other_port, "Other port's docstring")
