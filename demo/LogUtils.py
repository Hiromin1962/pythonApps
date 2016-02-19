# -*- coding: utf-8 -*-
'''
Created on 2014/02/14
ログを扱うメソッドを提供している
Ecilpse上からの起動とターミナルからの起動ではdefault-encodingが異なるケースがあり、
その際には一部のログは記録されない...
terminalから起動->ascii
eclipseから起動->utf_8
@author: okada
'''
import datetime
import codecs

class LogUtils:
    '''
    環境変数名を定数として宣言しておく。
    '''
    BASE_FILENAME="BoxGenDownloader.log"
    STRING_CODE = 'UTF_8' # コンソールに印字する文字列の文字コードを指定する

    def __init__(self):
        '''
        Constructor
        '''
        self.logflie = self.BASE_FILENAME
        self.f = None
        #print sys.getdefaultencoding()

    '''
    ファイルや標準出力で扱う文字列の文字コードを調べて返す
    macから実行するとサーバーから返されるエラーメッセージの文字コードがutf-8であるが、
    windowsから実行したところ、shift-jisでしたので。
    '''
    def getEncoding(self, message):
        for encoding in ['utf-8', 'shift-jis', 'euc-jp']:
            try:
                message.decode(encoding)
                return encoding
            except:
                pass
        return None

    '''
    印字メッセージの形式がstrであればunicode型に変換する。その判定を返す
    '''
    def checkOKType(self, message):
        valtype = type(message)
        # trueを返す値はUnicodeに変換して文字化けを防ぐ
        if valtype is unicode:
            return False
        elif valtype is str:
            return True
        elif valtype is list:
            return False
        else:
            return False

    '''
    印字フル機能メソッド。
    tag:ログファイルに出力するモジュールのタグ名
    message:出力するメッセージ
    logOnly:ログファイルだけに印字する:True、さもなければFalseを指定する
    '''
    def basePrint(self, tag, message, logOnly):
        # メッセージの文字コードを取得する
        message_encoding = self.getEncoding(message)
        if self.checkOKType(message) == True:
            try:
                #unicode型に変換します。
                uniStr = message.decode(message_encoding)
                if logOnly == False:
                    print uniStr
                #ログファイルに書きます
                self.writeLog(tag, uniStr)
            except Exception as e:
                print e
        else:
            if logOnly == False:
                print message
            self.writeLog(tag, message)
    '''
    標準出力とファイルにメッセージを書き込みます
    tag：ログの時刻の横に追記されるモジュール名
    message:ログもしくは標準出力に印字されるメッセージ
    '''
    def printx(self, tag, message):
        self.basePrint(tag, message, logOnly=False)

    '''
    ログファイルにだけ出力します。標準出力には表示しません
    '''
    def printlog(self, tag, message):
        self.basePrint(tag, message, logOnly=True)

    '''
    ログファイルを開く
    '''
    def openLog(self):
        #　カレントパスログファイルを生成する
        try:
            if self.f == None:
                # ログファイルはShift_JISで書き出す
                #self.f = codecs.open(self.logflie, 'w', 'shift_jis')
                self.f = codecs.open(self.logflie, 'w', 'utf-8')
            return True
        except Exception as e:
            print u"ログファイルのオープンに失敗しました:" + e.message # Errorのケースを確認してみる必要がある。e.msgが存在するかどうか？
            return False

    '''
    ログファイルを閉じる
    '''
    def closeLog(self):
        # ログファイルを閉じる
        try:
            if self.f != None:
                self.f.close()
            return True
        except Exception as e:
            print u"ログファイルのクローズに失敗しました:" + e.message
            return False

    '''
    ログファイルに書き込む
    '''
    def writeLog(self, tag, message):
        if self.f == None:
            self.openLog()
        # ファイルにログを書き込む
        now = datetime.datetime.today()
        lineTop = '[%s/%02d/%02d %02d:%02d:%02d.%06d]%s:' % (now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond, tag)
        try:
            self.f.write(lineTop)
            # タイプに応じてunicode変換する必要がある
            if self.checkOKType(message) == True:
                # messageをUnicodeに変換後、writeではShiftJisで書き込む
                self.f.write(message.decode('utf-8'))
            else:
                self.f.write(message)

            # windowsだと\nだけではメモ帳などでは改行してくれない。
            self.f.write('\r\n')
            self.f.flush()
            return True
        except Exception as e:
            print u"下記の原因でログファイルの書き込みに失敗しました。"
            print e
            return False