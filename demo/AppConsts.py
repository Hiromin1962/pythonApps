# -*- coding: utf-8 -*-
'''
Created on 2016/02/19
エラーメッセージやログ用メッセージなどに用いる文字列や定数などはこのクラスに追加して管理する。

@author: hiromi
'''

class AppConst(object):
    '''
    classdocs
    '''
    ERR_CONVERT_JSON = 'Convert response to dict error...when get version informations. skip download. sorry.' 
    FILE_NO_VERSION = 'File don\'t have version' 
    DOWN_LOAD_FILEIS = 'Download file is '  
    CUR_FOLDER_IS = 'Current folder is '
    CREATED_FOLDER = 'Created Folder is'
    ROOT_OWNER_IS = 'The root folder is owned by: {0}'
    FOLDER_WALKING = 'Call folder walking...next folder name is '
    NO_VER_INFOS = 'No version informations..'
    SEARCH_MATCH = 'Searching...matched item name:%s, id:%s '
    START_FOLDER_ID_IS = 'Start folder id is [%s]'
    NO_PARAM_CLIENT = "必須パラメータ（ClientIdもしくはClientSecret）が足りません"
    NO_PARAM_MAXNUM = "オプションパラメータ（MaxSearchNums）が足りません。デフォルト値をセットします。"
    NO_PARAN_DEFAULT_HOME = "オプションパラメータ（DefaultHome）が足りません。デフォルト値をセットします。"
    NO_PARAN_OUTFOLDER = "オプションパラメータ（OutputFolder）が足りません。デフォルト値をセットします。"
    ENDED = 'Generation File DownLoader ended!'
    FOLDER_ITEM_LIMITS = 'There is the first [%s] items in this folder:[%s]'
    INIT_PARAMS = 'DEFAULT HOME:%s. BASE_OUTPUT_FOLDER:%s. START_FOLDER:%s, MAX_SEARCH_NUM:%s, CLIENT_ID:%s, CLIENT_SECRET:%s, OTHER_PORT:%s'
    
    def __init__(self):
        '''
        Constructor
        '''
