#!/usr/bin/python3
#-----------------------------------------------------------------------------
#   Jetson Nano Cooler Monitor (JetCoolerMon)             Create 2021.08
#    
#   このツールはJetson Nano Developer Kitに搭載できる4ピンの空冷ファンの回転制御を
# 　Pythonで実装したものです。Jetson Nano ボードの温度によって空冷ファンの回転数を
# 　変更します。
#
#   オプション指定  
#     -o [file name] : 温度、回転数制御値を保存するCSVファイル名を指定します。
#     -j [Json name] : 動作設定用jsonファイルを指定します。
#
#   処理結果出力　
#   　出力：処理結果は、ツール実行フォルダの配下に「result_files」フォルダを生成し
# 　　　　　出力されます。生成ファイル名は、実行時に[-o] オプションで指定した名前です。
# 　　ログ：ツール実行フォルダの配下に「Log」というフォルダを作成し出力されます。
# 　　　　　ログファイルは指定したファイル数に達すると古いものから削除されます。
#
#   Author  : GENROKU@Karakuri-musha
#   License : See the license file for the license.
#       
#-----------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
# ライブラリインポート部 
# -------------------------------------------------------------------------------------------
# 共通ライブラリ
import sys
import os
from datetime import datetime
import subprocess
import json
import platform
import logging
from logging import FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET
from argparse import ArgumentParser


# -------------------------------------------------------------------------------------------
# 変数/定数　定義部 
# -------------------------------------------------------------------------------------------
CMD_TEXT =  'systeminfo'

SYSTEM_LABEL_RASPI          = 1
SYSTEM_LABEL_JETSON         = 2
SYSTEM_LABEL_LINUX          = 3
SYSTEM_LABEL_LINUX_OTHER    = 4
SYSTEM_LABEL_WIN10          = 5
SYSTEM_LABEL_WIN_OTHER      = 6

MSG_GET_OPTIONS_OUTPUT_HELP       = "Specify the output file name (.csv format) of the processing result. "
MSG_GET_OPTIONS_JSON_HELP         = "Specify the file (.json format) to be processed. "
MSG_TOOL_RUN                      = "Start the Jetson Nano Cooler Monitor (JetCoolerMon) tool."
MSG_TOOL_END                      = "Exit the Jetson Nano Cooler Monitor (JetCoolerMon) tool."
MSG_TOOL_ENV_ERROR                = "This tool is not available in your environment."

MSG_CSV_COL_NAME                  = "datetime,zone0,zone1,zone2,avarage,pwm_value\n"
# -------------------------------------------------------------------------------------------
# 関数　定義部
# -------------------------------------------------------------------------------------------

# Windows向け　外部コマンドの実行処理用の関数　Function for executing external commands.
# Windowsはロケールによってコマンドプロンプトの言語設定が違うため、英語出力に変更して出力する
def win_call_subprocess_run(origin_cmd):
    try:
        # コマンドプロンプトの言語コードを確認し、変数chcp_originに格納
        pre_p = subprocess.Popen("chcp",
                            shell=True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        chcp_res, _ = pre_p.communicate()
        chcp_origin = chcp_res.split(':')

        # コマンドプロンプト起動時に言語コードを英語に変更して起動し、systeminfoを実行
        res = subprocess.Popen("cmd.exe /k \"chcp 437\"",
                            shell=True,
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        res.stdin.write(origin_cmd + "\n")
        stdout_t, _ = res.communicate()

        # コマンドプロンプトの言語コードをorigin_chcpに戻す
        cmd = "chcp " + str(chcp_origin[1])
        after_p = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        after_res, _ = after_p.communicate()
  
        for line in stdout_t.splitlines():
            yield line

    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + origin_cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function

# Linux/Raspberry Pi OS用の外部コマンド実行関数(1)
# 通常外部コマンドの実行処理用の関数　Function for executing external commands.
def call_subprocess_run(cmd):
    try:
        res = subprocess.run(cmd, 
                            shell=True, 
                            check=False,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            )
        for line in res.stdout.splitlines():
            yield line
    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function



# Linux/Raspberry Pi OS用の外部コマンド実行関数(2)
# Sudo系コマンドの実行処理用の関数　Function for executing external commands.
def call_subprocess_run_sudo(cmd, p_passphrase):
    try:
        res = subprocess.run(cmd, 
                            shell=True, 
                            check=True,
                            input=p_passphrase + '\n',
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            )
        for line in res.stdout.splitlines():
            yield line
    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function

# システム情報の取得
# Rassbery PiとJetson以外のLinuxで実行された場合に実行環境を取得するための処理
def get_system_data(p_passphrase):
    lshw_cmd = ['sudo', 'lshw', '-json']
    proc = subprocess.Popen(lshw_cmd, 
                            stdin=p_passphrase + '/n',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return proc.communicate()[0]
# End Function

# Rassbery PiとJetson以外のLinuxで実行された場合に実行環境を読み込むための処理
def read_data(proc_output, class_='system'):
    proc_result = []
    proc_json = json.loads(proc_output)
    for entry in proc_json:
        proc_result.append(entry.get('product', ''))
    return proc_result
# End Function

# オプションの構成
def get_option():
    argparser = ArgumentParser()
    argparser.add_argument("-o", "--output", help=MSG_GET_OPTIONS_OUTPUT_HELP)
    argparser.add_argument("-j", "--json", help=MSG_GET_OPTIONS_JSON_HELP)
    return argparser.parse_args()
# End Function

# 外部ファイルの更新処理用の関数（先頭行追加）　Function for updating external files.
def update_file(p_file_d, p_data, p_dir_path):
    try:
        mk_dir_name = os.path.join(p_dir_path,'result_files')
        p_file_namepath = os.path.join(mk_dir_name, p_file_d)
        # --出力用ライブラリの所在確認と作成
        if not os.path.isdir(mk_dir_name):
            os.makedirs(mk_dir_name, exist_ok = True)
        
        if not os.path.exists(p_file_namepath):
            logger.info('---- Make output file ----')
            with open(p_file_namepath, "a") as fs:
                fs.write(MSG_CSV_COL_NAME)
            logger.info('---- Success make file ----')

        logger.info('---- Update file ----')
        with open(p_file_namepath, "a") as fs:
            for line in p_data:
                fs.write(line)
        logger.info('---- Success update file ----')
        return 0
    except OSError as e:
        logger.error(e)
        fs.close
        return 1
# End Function

#---------------------------------------------
# json function
#---------------------------------------------
# json read to dict
def read_json_entry(p_input_file_name):

    # jsonファイルを開く
    json_file_path = os.path.join(dir_path, p_input_file_name)
    json_open = open(json_file_path, 'r', encoding="utf-8")
    p_json_data_dict = json.load(json_open)

    return p_json_data_dict
# End Function

# Read dict(from json) 
def read_json_dict_entry(p_json_data_dict:dict, p_dict_entry_name:str):
    p_entry_data = p_json_data_dict.get(p_dict_entry_name, "")
    
    return p_entry_data
# End Function

def read_parameters(p_input_file_name):

    # jsonファイルを開く
    json_data_dict = read_json_entry(p_input_file_name)

    r_temp_th1      = read_json_dict_entry(json_data_dict,'temp_th1')
    r_temp_th2      = read_json_dict_entry(json_data_dict,'temp_th2')
    r_temp_th3      = read_json_dict_entry(json_data_dict,'temp_th3')
    r_temp_th4      = read_json_dict_entry(json_data_dict,'temp_th4')
    r_pwm_th1       = read_json_dict_entry(json_data_dict,'pwm_th1')
    r_pwm_th2       = read_json_dict_entry(json_data_dict,'pwm_th2') 
    r_pwm_th3       = read_json_dict_entry(json_data_dict,'pwm_th3')
    r_pwm_th4       = read_json_dict_entry(json_data_dict,'pwm_th4')
    r_pwm_over      = read_json_dict_entry(json_data_dict,'pwm_over')
    r_max_log_cnt   = read_json_dict_entry(json_data_dict,'max_log_cnt')
    r_csv_output   = read_json_dict_entry(json_data_dict,'csv_output')

    return r_temp_th1, r_temp_th2, r_temp_th3, r_temp_th4, r_pwm_th1, r_pwm_th2, r_pwm_th3, r_pwm_th4, r_pwm_over, r_max_log_cnt, r_csv_output
# End Function


# -----------------------------------------------------------------------------
# main処理（main.pyが起動された場合に処理される内容）
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    # ----------------------------------------------------------
    # Get Current path process
    # ----------------------------------------------------------
    # Current Path の取得
    # 実行方式（実行形式ファイル、または.pyファイル）によりカレントパスの取得方法を分ける
    if getattr(sys, 'frozen', False):
        os_current_path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        os_current_path = os.path.dirname(os.path.abspath(__file__))
    dir_path = os_current_path

    # ----------------------------------------------------------
    # Set Logger process
    # ----------------------------------------------------------
    # ロギングの設定（ログファイルに出力する）
    # --ログ出力用ライブラリの所在確認と作成
    log_path = os.path.join(dir_path, "Log")
    if not os.path.isdir(log_path):
        os.makedirs(log_path, exist_ok = True)

    # --ファイル出力用ハンドラ
    file_handler = FileHandler(
        f"{log_path}/log{datetime.now():%Y%m%d%H%M%S}.log"
    )
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(
        Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s")
    )

    # --ルートロガーの設定
    logging.basicConfig(level=NOTSET, handlers=[file_handler])

    logger = logging.getLogger(__name__)
    logger.info(MSG_TOOL_RUN)

    # ---------------------------------------------------------------
    # Check option and file format. 
    # ---------------------------------------------------------------
    # コマンドで指定されたインストール定義ファイル名の確認
    args = get_option()
    output_file_name    = args.output
    input_json_name     = args.json
    
    p_outputname, p_outext = os.path.splitext(output_file_name)
    if p_outext == '.csv':
        logger.info('Input file is [' + output_file_name + '] I checked the name. The process will start.')
    else:
        logger.error('Input file is [' + output_file_name + '] The extension of the specified file is different. Please specify a .xml format file.')   
        sys.exit() 

    p_filename, p_ext = os.path.splitext(input_json_name)
    if p_ext == '.json':
        logger.info('Input file is [' + input_json_name + '] I checked the configuration file. The process will start.')
    else:
        logger.error('Input file is [' + input_json_name + '] The extension of the specified file is different. Please specify a .json format file.')   
        sys.exit() 


    # ---------------------------------------------------------------
    # Read json file 
    # ---------------------------------------------------------------
    # jsonファイル内の設定情報読み込み
    p_temp_th1, p_temp_th2, p_temp_th3, p_temp_th4, p_pwm_th1, p_pwm_th2, p_pwm_th3, p_pwm_th4, p_pwm_over, max_log_cnt, p_csv_output = read_parameters(input_json_name)

    # ---------------------------------------------------------------
    # Delete Old Log file  
    # ---------------------------------------------------------------
    files = os.listdir(log_path)  # ディレクトリ内のファイルリストを取得
    if len(files) >= int(max_log_cnt) + 1:
        del_files = len(files)-int(max_log_cnt)
        files.sort()                                    # ファイルリストを昇順に並び替え
        for i in range(del_files):
            del_file_name = os.path.join(log_path, files[i])
            logger.info("delete log file : " + del_file_name)
            os.remove(del_file_name)              # 一番古いファイル名から削除

    # ---------------------------------------------------------------
    # Check System environment 
    # ---------------------------------------------------------------
    # システム環境の判別 Determining the system environment.
    logger.info('System Enviroment Check Process Begin')

    system_label = ''
    os_name = platform.system()
    logger.info('The operating system is [' + os_name + ']')
    if os_name == 'Linux':
        # Raspberry Pi / Jetson / other ( have device-tree/model )
        if os.path.exists('/proc/device-tree/model'):
            res = call_subprocess_run('cat /proc/device-tree/model')
            os_info = res.__next__()
            if 'Raspberry Pi' in os_info:
                system_label = SYSTEM_LABEL_RASPI
                logger.info('The model name is [' + os_info + ']')
            elif 'NVIDIA Jetson' in os_info:
                system_label = SYSTEM_LABEL_JETSON
                logger.info('The model name is [' + os_info + ']')
            else:
                system_label = SYSTEM_LABEL_LINUX_OTHER
                logger.error('The model name is [' + os_info + ']')
        # Linux ( Not have device-tree/model )
        else:
            for product in read_data(get_system_data()):
                os_info = SYSTEM_LABEL_LINUX
            logger.error('The model name is [' + os_info + ']')

    elif os_name == 'Windows':
        systeminfo_l = win_call_subprocess_run(CMD_TEXT)
 
        systeminfo_dict = []
        for line in systeminfo_l:
            info_l = line.split(': ')
            for i in range(len(info_l)):
                info_l[i] = info_l[i].strip()
            systeminfo_dict.append(info_l)
        
        if 'Microsoft Windows 10' in systeminfo_dict[5][1]:
            system_label = SYSTEM_LABEL_WIN10
            logger.info('The model name is [' + systeminfo_dict[5][1] + ']')
        else:
            system_label = SYSTEM_LABEL_WIN_OTHER
            logger.error('The model name is [' + systeminfo_dict[5][1] + ']')

    # ---------------------------------------------------------------
    # Tool main 処理部 
    # ---------------------------------------------------------------
    # 対象システムの指定
    if system_label == SYSTEM_LABEL_JETSON:
        try:
            logger.info('Jetson Nano temperature measurement started.')
            temp_value = 0
            Zone_cnt = 3
            
            now = datetime.now()
            p_data = now.strftime("%Y/%m/%d %H:%M:%S") + ","

            for zone in range(Zone_cnt):
                path = "/sys/devices/virtual/thermal/thermal_zone" + str(zone) + "/temp" 
                with open(path, "r") as fs:
                    for line in fs: 
                        temp_value = temp_value + int(line)
                        p_data = p_data + str(int(line)/1000) + ","
                        logger.info('Zone'+ str(zone) + ': ' + str(int(line)/1000) )
            ave_temp = (temp_value / Zone_cnt) / 1000
            p_data = p_data + f'{ave_temp:.1f}' + ","
            logger.info('avarage temp: '+ f'{ave_temp:.1f}')

            if ave_temp <= float(p_temp_th1):
                pwm_set_val = p_pwm_th1
            elif ave_temp <= float(p_temp_th2):
                pwm_set_val = p_pwm_th2
            elif ave_temp <= float(p_temp_th3):
                pwm_set_val = p_pwm_th3
            elif ave_temp <= float(p_temp_th4):
                pwm_set_val =p_pwm_th4
            else:
                pwm_set_val = p_pwm_over
            
            logger.info('PWM Set Value : '+ pwm_set_val)
            p_data = p_data + pwm_set_val + "\n"
            if p_csv_output == "1":
                update_file(output_file_name, p_data, dir_path)
            
            with open("/sys/devices/pwm-fan/target_pwm", "w") as fs:
                fs.write(f"{pwm_set_val}")

        except OSError as e:
            logger.error(e)
    else:
        logger.error(MSG_TOOL_ENV_ERROR)
    
    logger.info(MSG_TOOL_END)