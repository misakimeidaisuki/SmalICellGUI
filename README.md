# Small Cell GUI
簡化ITRI UDCell開機程式，一按鍵執行開機所需ssh/bash程式

## 功能
1. 自動開啟與執行 ITRI UDCell開機所需程式與終端視窗
2. 顯示連接UE的MME ID與IP
3. 可在GUI介面上設定LWA Ratio與MCS
4. 保留所有執行期間Log
5. 自動擷取流量圖

## 需求
1. ITRI UDCell所需執行程式與EPC程式需自備
2. 建議 Python 版本 >= 3.7.4
3. 套件需求與建議版本
	```
	numpy 		1.17.4
	matplotlib 	3.1.2
	configparser 	3.7.1
	pexpect 	4.7.0
	paramiko	2.7.1
	```

## 設定
設定檔案路徑 config/config.conf

### 基礎設定
```ini
[Setting]
#本機UDcell執行檔位置
UDcell_basedir=~/itriUDcell_2019mmddreleased
#ITRI UDcell L1目錄
SmallCell_basedir=/home/root/images_UMA15_FP_8cores
#ITRI UDcell 關機指令
cell_shutdown_command=poweroff
#自動輸入指令間隔秒數
command_delay=2
#Screen/虛擬終端數量
screen_number=7
#設定工具佔用的ssh與bash視窗位置
sys_ssh=SSH
sys_bash=Bash
```

### SSH與Bash設定
```ini
[Bash]
#bash路徑
bash=/bin/bash

[SSHClient]
#ITRI UDcell ssh IP,Port,登入帳號與密碼
ip=192.168.10.1
port=22
username=root
password=
```

### Screen 設定
Screen 數量要先在 [Setting] 中決定
```ini
[S1]
#screen名稱
name=S1
#screen類型 bash 或 ssh
type=ssh

...
...
[S7]
name=SSH
type=ssh
```

### 開機指令
```ini
#名稱以 [Command_編號] 命名
[Command_1]
#指令要輸入的 screen 目標
target=S1
#如需要切換目錄,請輸入目錄位置否則留空即可
dir=/home/root/images_UMA15_FP_8cores
#執行只另
run=./s1_run_8core_fp_gtpu.sh
...
...
[Command_N]
target=S4
dir=
run=a
```

### 工具指令
```ini
#以 [tools_command_名稱] 命名, 設定方式同上
[tools_command_uploadL1]
#screen目標可以使用 sys_bash 或 sys_ssh 代表系統佔用的ssh與bash
target=sys_bash
dir=
run=scp ./images/images_UMA15_FP_8cores/* root@192.168.10.1:/home/root/images_UMA15_FP_8cores/

[tools_command_lwaratio]
target=sys_ssh
dir=
run=/home/root/images_UMA15_FP_8cores/lwaratio -l %%d -w %%d
```

## 執行程式
該程式執行時需要使用root權限
```bash
sudo python3 -m main
```
或在 root 下
```bash
python3 -m main
```

##### CYUT M209.1 LAB
