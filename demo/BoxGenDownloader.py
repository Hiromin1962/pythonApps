# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os
from boxsdk import Client
from auth import authenticate
from demo import LogUtils
from demo import ConfigLoader
from demo import AppConsts
import io
import json

"""
BOXにログインして、特定のフォルダの中にあるversionを持つファイルにて、直近のversionのファイルだけを
ローカルフォルダにダウンロードするアプリです。versionを持たないファイルはダウンロードされません。
BoxSDK for Python ver1.4.1のFileクラスを拡張してありますので、実行する際には、boxsdkをインストール後に
Fileクラスに幾つかのメソッドを追加する必要があります。

2016/2/18 created by H.Okada@futurevision-llc.com
"""
TAG = 'BoxGenDownloader'
test_count=0

# instantiate log & config manager agent
log_agent = LogUtils.LogUtils()
app_consts = AppConsts.AppConst()
config_agent = None

# store initial values to global vars.
"""
各初期設定の意味は次のとおりです。
MAX_SEARCH_NUMS：各フォルダ内にてチェックするファイルの最大数
DEFAULT_HOME：探索開始フォルダを省略した場合に、Localに作成されるRootフォルダの名前
BASE_OUTPUT：ダウンロードしたファイルを保存するベースフォルダ名
START_FOLDER：BOX内にて探索を開始するフォルダ名。
CLIENT_ID：BOX APPのClient ID
CLIENT_SECRET：BOX APPのClient Secret
これらの設定はsettings.iniファイルから読み込みます。このファイル内に日本語を含む場合はUTF-8で記述してください。
"""
MAX_SEARCH_NUMS=None
DEFAULT_HOME=None
BASE_OUTPUT=None
START_FOLDER=None
CLIENT_ID=None
CLIENT_SECRET=None
OTHER_PORT=None

"""
    print log to logfile and stdout.
    引数：メッセージ文字列
    戻り値：なし
"""
def printlog(message):
    global TAG
    global log_agent
    try:
        log_agent.printx(TAG, message)
    except Exception as e:
        print(e)
    
"""
    Version情報を取得します。存在する場合は直近のversion情報だけを返します。
    引数：client :Box Client
    引数：file_id :情報を取得したいfileのID
    戻り値；versionが存在する場合は、直近のversion情報、さもなければNone
"""
def get_version(client, file_id):
    # idからファイルインスタンスを生成する
    target_file = client.file(file_id=file_id)
    # get version informations.
    response = target_file.get_versions()

    try:
        #convert json to dict.
        resp_dict = json.loads(response)
        # please check total count. if the value equal 0 then, this file don't have other version.
        count = int(resp_dict['total_count'])
        if count > 0:
            return resp_dict['entries'][0] #return most recently version file information.
        else:
            return None
        
    except ValueError:
        printlog(response)
        printlog(app_consts.ERR_CONVERT_JSON)
        return None

"""
    settings.iniファイルにMaxSearchNumが指定されていない場合にはAPIにおけるデフォルトの100を返す。
    引数：なし
    戻り値：MAX_SEAECH_NUMSの値
"""
def check_max_search_muns():
    if MAX_SEARCH_NUMS:
        return MAX_SEARCH_NUMS
    else:
        return 100
    
"""
    引数として渡された名前のフォルダを探して、idを返す。
    引数：client：Box Client
    引数: folder_name：検索するフォルダ名
    戻り値：フォルダのID、存在しない場合ば0(ログインユーザのRootフォルダのIDを返す)
"""
def search_folder(client, folder_name):
    search_results = client.search(
        folder_name,
        limit=check_max_search_muns(),
        offset=0,
        content_types='folder',
    )
    for item in search_results:
        item_with_name = item.get(fields=['name'])
        printlog(app_consts.SEARCH_MATCH % (item_with_name.name, item_with_name.id))
        # get version list..OK!
        if item_with_name.name == START_FOLDER:
            return item_with_name.id
    # if you cannot find start folder, then start from root folder.
    return '0'

"""
    ローカルフォルダに指定されたIDのファイルを作成する（一世代前のファイルを作成する）
    引数：client：Box Client
    引数：file_id：作成するファイルのID(一世代前）
    戻り値：なし
"""
def create_previousfile(client, file_id):
    # get recently file information. OK!
    recent_ver_info = get_version(client, file_id)
    
    if recent_ver_info is None:
        printlog(app_consts.NO_VER_INFOS)
    else:
        printlog(str(recent_ver_info))
        
    # download recent version file...
    if recent_ver_info is not None:
        target_id = recent_ver_info['id']
        save_file = client.file(file_id=file_id)

        file_name = recent_ver_info['name']
        printlog(app_consts.DOWN_LOAD_FILEIS+file_name)
        
        # wbモードでopenしないとtype errorで失敗する。
        with io.open(file_name, 'wb') as dlfile:
            save_file.download_to_version(dlfile, target_id)
    else:
        printlog(app_consts.FILE_NO_VERSION)

"""
    もし存在しなければ、指定された名前のフォルダをローカルに作成します。
    引数：folder_name：フォルダ名
    戻り値：なし
"""              
def create_folder(folder_name):
    #フォルダがなけれな作成します。
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        printlog(app_consts.CREATED_FOLDER + folder_name)

"""
    引数で渡された起点からフォルダ階層を探索して、versionを持つファイルだけをダウンロードします。
    引数：client：Box Client
    引数：start_folder_id：探索の起点であるフォルダのID
    戻り値：なし
"""
def check_folder_structures(client, start_folder_id):
    # test_countはglobal変数を更新するので、global宣言を追加する。
    global test_count

    printlog(app_consts.CUR_FOLDER_IS + os.getcwd())
    # ローカルなフォルダを作成する必要がある。
    root_folder = client.folder(folder_id=start_folder_id).get()
    printlog(app_consts.ROOT_OWNER_IS.format(root_folder.owned_by['login']))
    
    # これは各フォルダ毎にmax #件 となる。...
    items = root_folder.get_items(limit=check_max_search_muns(), offset=0)
        
    printlog(app_consts.FOLDER_ITEM_LIMITS % (str(MAX_SEARCH_NUMS),root_folder.name))
    for item in items:
        test_count += 1
        printlog(str(test_count) + " " + item.name)
        # フォルダなら深くダイブする。ファイルならversionの有無をチェックしてDLスル。
        if item.type == 'folder':
            printlog(app_consts.FOLDER_WALKING + item.name)
            # もしフォルダが存在しなければ作成する
            create_folder(item.name)
            os.chdir(item.name)
            check_folder_structures(client, item.id)
        elif item.type == 'file':
            # get recently file information. and download the previous file.
            create_previousfile(client, item.id)
        else:
            pass
    os.chdir('..')
    printlog(app_consts.CUR_FOLDER_IS + os.getcwd())

"""
    探索開始フォルダの名前を取得してから、ローカルに同名のフォルダを作成する
    引数：client：Box Client
    引数：start_folder_id：開始フォルダのID
    戻り値：なし
"""
def create_start_folder(client, start_folder_id):
    folder_name = ''
    # startFolderが'0'の場合は、HOMEが探索起点と成る。その際、localにはDEFALUT_HOMEで指定したフォルダを作成する。
    if start_folder_id == '0':
        folder_name = DEFAULT_HOME
    else:
        root_folder = client.folder(folder_id=start_folder_id).get()
        folder_name = root_folder.name
    # もしLocalに開始フォルダが存在しなければ作成する
    try:
        os.chdir(BASE_OUTPUT)
        create_folder(folder_name)
        os.chdir(folder_name)
    except Exception as e:
        print(e)

"""
    指定された起点フォルダのIDを検索して返します。
    引数：client：BoxClient
    戻り値：探索の起点となるフォルダのID
"""            
def define_start_folder(client):
    if START_FOLDER:
        # folder名を受け取り、folder_idを返す。
        return search_folder(client, START_FOLDER)
    else:
        return '0'

"""
    一括ダウンロードサンプルを起動します。
    引数：認証情報
    戻り値：なし
"""    
def run_examples(oauth):
    # create client instance.
    client = Client(oauth)
    # start folderを探索してそのIDを返します。もし存在しない場合は"0"が返されます。HOMEです。
    start_folder_id = define_start_folder(client)
    printlog(app_consts.START_FOLDER_ID_IS % (start_folder_id))

    # 探索開始フォルダ名を取得して、localにフォルダを作成する。見つからない場合はdocRootを作成して移動する。
    create_start_folder(client, start_folder_id)

    # 探索開始
    check_folder_structures(client, start_folder_id)   

"""
    エラーチェック：必要となるパラメータが不足している場合はエラーとします。それ以外はデフォルト値をセットします。
    引数：なし
    戻り値：値を変更したかどうかを返す。
"""
def validate_parameters():
    # When you update global var, you have to define the global <varname>
    global MAX_SEARCH_NUMS,DEFAULT_HOME,BASE_OUTPUT
    
    change_value = False
    
    if not CLIENT_ID or not CLIENT_SECRET:
        printlog(app_consts.NO_PARAM_CLIENT)
        raise Exception(app_consts.NO_PARAM_CLIENT)
    
    if not MAX_SEARCH_NUMS:
        printlog(app_consts.NO_PARAM_MAXNUM)
        MAX_SEARCH_NUMS=100
        change_value = True
        
    if not DEFAULT_HOME:
        printlog(app_consts.NO_PARAN_DEFAULT_HOME)
        DEFAULT_HOME='rootFolder'
        change_value = True

    if not BASE_OUTPUT:
        printlog(app_consts.NO_PARAN_OUTFOLDER)
        BASE_OUTPUT=os.getcwd()
        change_value = True
        
    return change_value

"""
    初期設定をsettings.iniファイルから読み込む
    引数：なし
    戻り値：なし
"""
def read_config():
    # When you update global var, you have to define the global <varname>
    global config_agent
    global MAX_SEARCH_NUMS,DEFAULT_HOME,BASE_OUTPUT,START_FOLDER,CLIENT_ID,CLIENT_SECRET,OTHER_PORT
    
    config_agent=ConfigLoader.ConfigLoader()
    
    # settings.iniファイルからreadした属性項目をグローバル変数にセットする。
    DEFAULT_HOME=config_agent.DefaultHome
    BASE_OUTPUT=config_agent.OutputFolder
    START_FOLDER=config_agent.StartFolder
    MAX_SEARCH_NUMS=config_agent.MaxSearchNum
    CLIENT_ID=config_agent.ClientId
    CLIENT_SECRET=config_agent.ClientSecret
    OTHER_PORT=config_agent.OtherPort
    
    printlog(app_consts.INIT_PARAMS 
             % (DEFAULT_HOME,BASE_OUTPUT,START_FOLDER,MAX_SEARCH_NUMS,CLIENT_ID,CLIENT_SECRET,OTHER_PORT))
    # call parameter check...
    changed = validate_parameters()
    # 変更があった（未指定のためデフォルト値をセットしたケース）場合はログに残す。
    if changed:
        printlog(app_consts.INIT_PARAMS 
             % (DEFAULT_HOME,BASE_OUTPUT,START_FOLDER,MAX_SEARCH_NUMS,CLIENT_ID,CLIENT_SECRET,OTHER_PORT))
        
def main():
    # read configuration from file.
    read_config()
    
    # Execute app authentication. Must be set CLIENT_ID and CLIENT_SECRET into settings.ini.
    if OTHER_PORT:
        oauth, _, _ = authenticate(CLIENT_ID, CLIENT_SECRET, use_port=OTHER_PORT)
    else:
        oauth, _, _ = authenticate(CLIENT_ID, CLIENT_SECRET)

    # execute restore files.
    run_examples(oauth)
    printlog(app_consts.ENDED)
    
    os._exit(0)

if __name__ == '__main__':
    main()
