# Jetson Nano Cooler Monitor (JetCoolerMon) 

## **OverView**
---
Jetson Nano Cooler Monitor </br>
 Create 2021.08</br>
 Author  : GENROKU@Karakuri-musha</br>
 License : See the license file for the license.</br>
 Python ver : Python 3.6.9 (conda)</br>
 Hardware : Ubuntu 18.04.5 LTS (Jetson Nano Developer Kit) </br>
 
このツールはJetson Nano Developer Kitに搭載できる4ピンの空冷ファンの回転制御を、Pythonで実装したものです。</br>
Jetson Nano ボードの温度によって空冷ファンの回転数を変更します。</br>

This tool is a Python implementation of the rotation control of a 4-pin air cooling fan that can be installed in the Jetson Nano Developer Kit. </br>
The rotation speed of the air cooling fan is changed according to the temperature of the Jetson Nano board.</br>
 </br>

以下のブログでこのツールを紹介しています。参考にしてください。（日本語）</br>
[【Jetson Nano】そうやってすぐ熱くなるし・・クールに行こうぜ！（CPU温度による冷却ファン制御）</br>https://karakuri-musha.com/uncategorized/jetson-nano-how-to-use-fan01/](https://karakuri-musha.com/uncategorized/jetson-nano-how-to-use-fan01/)

</br>

## **Tool file structure**
---
ツールのファイル構成は次の通りです。</br>
Target OS：Ubuntu18.04 LTS (Jetson Nano) 
</br>

|ファイル名  |形式  |説明  |
|---------|---------|---------|
|JetCoolerMon.py|Python3(.py)| ツール 本体です。Jetson Nano Developper Kitに4ピン対応の空冷ファンを接続した環境で実行してください。</br>Run in an environment with a 4-pin bay air cooling fan connected to the Jetson Nano Developper Kit.|
|JetCoolerMonSetting.json|json(.json)| ツールの動作設定用ファイルです。</br>This is a file for setting the operation of the tool.|
</br>


## **Run-time option specification**
---
ツール実行時に指定できるオプションは次の通りです。

[Execution example(for cmd)]</br>
`JetCoolerMon.py -o Datalist.csv -j JetCoolerMonSetting.json`

|option|Description|
|---------|---------|
| -o [Output file name] | 測定値出力ファイルを指定します。（必須）</br> Specify the measured value output file. (Required) |
| -j [Operation settings file name] | 動作設定用ファイル名を指定します。（必須）</br> Specify the file name for the operation settings. (Required) |

 </br>
 </br>

## **Operation setting (entry in json file)**
---
動作設定ファイル（IoTCNTconfig.json）は次のような構成になっています。

[IoTCNTconfig.json]</br>
`{
    "temp_th1"   : "30",
    "temp_th2"   : "40",
    "temp_th3"   : "50",
    "temp_th4"   : "60",
    "pwm_th1"    : "40",
    "pwm_th2"    : "90",
    "pwm_th3"    : "140",
    "pwm_th4"    : "190",
    "pwm_over"   : "240",
    "max_log_cnt"   : "10",
    "csv_output"    : "1"
}`

|item|default|Description|
|---------|---------|---------|
|temp_th1| *30* | 温度閾値です。　計測温度（temp）＜＝temp_th1　</br> The temperature threshold. [Measured temperature (temp)] ＜＝[temp_th1]|
|temp_th2| *40* | 温度閾値です。　temp_th1＜計測温度（temp）＜＝temp_th2</br> The temperature threshold. [temp_th1]＜[Measured temperature (temp)] ＜＝[temp_th2]|
|temp_th3| *50* | 温度閾値です。　temp_th2＜計測温度（temp）＜＝temp_th3</br> The temperature threshold. [temp_th2]＜[Measured temperature (temp)] ＜＝[temp_th3]|
|temp_th4| *60* | 温度閾値です。　temp_th3＜計測温度（temp）＜＝temp_th4</br> The temperature threshold. [temp_th3]＜[Measured temperature (temp)] ＜＝[temp_th4]|
|pwm_th1| *40*      | 空冷ファンの回転数制御値です。測定温度がtemp_th1以下の場合に適用されます。  </br>This is the rotation speed control value of the air cooling fan. Applies when the measured temperature when temp_th1 or less.|
|pwm_th2| *90*            | 空冷ファンの回転数制御値です。測定温度がtemp_th2以下の場合に適用されます。  </br>This is the rotation speed control value of the air cooling fan. Applies when the measured temperature when temp_th2 or less.|
|pwm_th3| *140*  | 空冷ファンの回転数制御値です。測定温度がtemp_th3以下の場合に適用されます。  </br>This is the rotation speed control value of the air cooling fan. Applies when the measured temperature when temp_th3 or less.|
|pwm_th4| *190*  | 空冷ファンの回転数制御値です。測定温度がtemp_th4以下の場合に適用されます。  </br>This is the rotation speed control value of the air cooling fan. Applies when the measured temperature when temp_th4 or less.|
|pwm_over| *240*        | 空冷ファンの回転数制御値です。測定温度がtemp_th4よりも大きい場合に適用されます。  </br>This is the rotation speed control value of the air cooling fan. Applies when the measured temperature is greater than temp_th4.|
|max_log_cnt| *10*    | ログファイルの最大保存数です。 </br>The maximum number of log files that can be saved.|
|csv_output| *1*    | CSVファイル出力のスイッチです。(1：ON、0:OFF) </br>It is a switch for CSV file output. (1: ON, 0: OFF)|





## **How to Log management**
---
本ツール実行時には、ツール格納先フォルダ配下に「Log」ディレクトリが作成され、本ツール実行時のログが格納されます。</br>
ログはツールの実行毎に出力されるため、動作設定ファイル内でログの最大保存数を設定することを推奨します。</br>
ツール実行時に最大補完数と同数のログがある場合に更新日付の古いモノから削除されます。

When this tool is executed, a "Log" directory is created under the tool storage folder, and the log when this tool is executed is stored. </br>
Since the log is output each time the tool is executed, it is recommended to set the maximum number of logs to be saved in the operation setting file. </br>
If there are as many logs as the maximum number of completions when the tool is executed, the ones with the oldest update date will be deleted.

 </br>
また、CSVファイルへのデータ書き出しは、標準で有効（指定値：1）になっているため長期間運用する場合は、</br>
無効（指定値：0）にすることでディスクリソースの消費を軽減することができます。動作設定ファイル内で設定することができます。 </br>
In addition, since data writing to a CSV file is enabled by default (specified value: 1), it should be disabled (specified value: 0) for long-term operation to reduce disk resource consumption. I can. It can be set in the operation setting file.</br>
 </br>
 </br>
 

## **How to use**
---



１．ツール配置用のディレクトリをJetson Nano OS上に作成します。</br>
```
sudo mkdir /opt/JetCoolerMon
```
２．作成したディレクトリにツールをコピーします。</br>
```
cd /opt/JetCoolerMon
sudo git clone https://github.com/karakuri-musha/JetCoolerMon.git
```
３．「JetCoolerMon.py」を実行するシェルを記載します。</br>
```
sudo vi /usr/local/bin/JetCooler_mon.sh
```
シェルの内容
```
#!/bin/sh
python3 /opt/JetCoolerMon/JetCoolerMon.py -o output.csv -j JetCoolerMonSetting.json
```

４．シェルに実行権限を付与します。
```
sudo chmod +x /usr/local/bin/JetCooler_mon.sh
```

５．「crontab」をエディタモードで開いてスケジュールを追加します。
```
sudo crontab -e
```
ファイルの最後に以下のスケジュールを記述し、保存します。（例は1分間隔で実行する）
```
* * * * * sh /usr/local/bin/JetCooler_mon.sh
```
６．「cron」を再起動します。</br>
```
sudo /etc/init.d/cron restart
```

７．スケジュールで起動された後、ツールのディレクトリに「Log」ディレクトリが作成されます。 </br>
　　フォルダ内に実行時のログが保存されることを確認してください。
【ログ内容：例】
```
2021-08-27 13:51:01,471@ __main__ [INFO] <module>: Start the Jetson Nano Cooler Monitor (JetCoolerMon) tool.
2021-08-27 13:51:01,475@ __main__ [INFO] <module>: Input file is [output.csv] I checked the name. The process will start.
2021-08-27 13:51:01,475@ __main__ [INFO] <module>: Input file is [JetCoolerMonSetting.json] I checked the configuration file. The process will start.
2021-08-27 13:51:01,475@ __main__ [INFO] <module>: System Enviroment Check Process Begin
2021-08-27 13:51:01,480@ __main__ [INFO] <module>: The operating system is [Linux]
2021-08-27 13:51:01,485@ __main__ [INFO] <module>: The model name is [NVIDIA Jetson Nano Developer Kit]
2021-08-27 13:51:01,485@ __main__ [INFO] <module>: Jetson Nano temperature measurement started.
2021-08-27 13:51:01,486@ __main__ [INFO] <module>: Zone0: 33.5
2021-08-27 13:51:01,486@ __main__ [INFO] <module>: Zone1: 27.0
2021-08-27 13:51:01,486@ __main__ [INFO] <module>: Zone2: 28.5
2021-08-27 13:51:01,486@ __main__ [INFO] <module>: avarage temp: 29.7
2021-08-27 13:51:01,487@ __main__ [INFO] <module>: PWM Set Value : 40
2021-08-27 13:51:01,487@ __main__ [INFO] update_file: ---- Update file ----
2021-08-27 13:51:01,487@ __main__ [INFO] update_file: ---- Success update file ----
2021-08-27 13:51:01,487@ __main__ [INFO] <module>: Exit the Jetson Nano Cooler Monitor (JetCoolerMon) tool.
```

以下のブログでこのツールを紹介しています。参考にしてください。（日本語）</br>
[【Jetson Nano】そうやってすぐ熱くなるし・・クールに行こうぜ！（CPU温度による冷却ファン制御）</br>https://karakuri-musha.com/uncategorized/jetson-nano-how-to-use-fan01/](https://karakuri-musha.com/uncategorized/jetson-nano-how-to-use-fan01/)

</br>