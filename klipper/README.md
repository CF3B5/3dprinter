# 走过路过给我加点star，谢谢 :-)


# shell_command.py [Klipper 支持系统命令的扩展]

让Klipper的Gcode增加支持运行系统命令的功能

## 安装方法
复制 `shell_command.py` 到 `klipper/klippy/extras`

## 使用方法
在klipper的配置文件`printer.cfg`中加入需要运行的命令，例如
```ini
[shell_command my_command]
command: date
```

重启klipper服务
```shell
sudo service klipper restart
```

重启成功后，在控制台输入
```
SHELL_COMMAND NAME=my_command
```
Klipper就会执行系统date这个命令，并且将命令的返回结果当前日期显示在控制台中。


# htu21d_host.py [Klipper 增加HTU21D_HOST温湿度传感器支持]

Klipper似乎对i2c总线的设备非常不稳定，一旦i2c总线的设备通讯发生通讯错误，
负责i2c总线通讯的mcu就会彻底崩溃，导致klipper服务发生错误，停止工作，
这对于需要长时间连续工作的3D打印机来说是完全不可接受的， 譬如打印到90%来个i2c timeout的error，
真的想死的心都有了……也不知道为啥klipper团队为啥不解决这个问:-(。
所以，我弄了一个通过树莓派系统原生的获取温湿度的功能的插件，来规避这个问题，当然如果这样子的话，
传感器也就只能接在树莓派的i2c接口上了（树莓派连接HTU21D的方法请自行搜索，网上很多）

## 安装方法
复制 `htu21d_host.py` 到 `klipper/klippy/extras`

修改`klipper/klippy/extras/temperature_sensors.cfg`文件，在其中增加一行
```ini
[htu21d_host]
```

安装klipper环境的python的传感器支持库（国内安装建议使用国内镜像源）
```shell
~/klippy-env/bin/pip install sensor smbus spidev -i https://pypi.tuna.tsinghua.edu.cn/simple
```

最后重启klipper服务
```shell
sudo service klipper restart
```

## 使用方法

在klipper的printer.cfg配置文件中增加传感器的配置段落
```ini
# 传感器配置
[temperature_sensor enclosure]
sensor_type: HTU21D_HOST
#i2c_address: 64

# 查询的温湿度的宏代码
[gcode_macro QUERY_HTU21D]
gcode:
    {% set sensor = printer["htu21d_host enclosure"] %}
    {action_respond_info(
        "Temperature: %.2f C\n"
        "Humidity: %.2f%%" % (
            sensor.temperature,
            sensor.humidity))}
```

# temperature_fan.py [Klipper温度风扇的优化扩展，增加reverse配置项]

Klipper标准的温度风扇temperature_fan默认逻辑是降温逻辑，设置了目标温度后，
达到目标温度才会启动风扇降温，低于温度不会启动风扇，但是一些内循环风扇目的是增温，
运行逻辑与降温风扇正好相反，所以我调整了代码，增加了原本温度风扇的reverse工作模式，
打开reverse工作模式后，低于目标温度时风扇会工作，高于目标温度则会停止风扇

## 安装方法

复制插件`temperature_fan.py` 到 `klipper/klippy/extras` 覆盖原本的温度风扇扩展
（由于是替换原Klipper扩展，所以升级有可能会覆盖，可能需要重新安装，不过我已经将扩展提交klipper官方PR，如果同意后会成为官方配置，就不需要重新安装）

## 使用方法
printer.cfg配置文件中增加传感器的配置段落
```ini
[temperature_fan enclosure_cyclic_fan]
##	循环风扇
pin: PD14
sensor_type: HTU21D_HOST
reverse: True # 主要是这个设置为True，温度风扇工作模式将反转，用于增温，其他配置沿用你自己的配置即可
target_temp: 0.0
min_temp: 0
max_temp: 60.0
max_speed: 0.6
min_speed: 0
# control: watermark
control: pid
pid_Kp: 40
pid_Ki: 2
pid_Kd: 1
```


# xiaomi_blue.py [Klipper 增加小米蓝牙温湿度传感器的温湿度]

小米这个传感器便宜大碗，所以很多人用这个传感器来进行打印机的仓温监控，而且这个传感器的协议坊间也公开的差不多了，
所以就写了个模块用树莓派的蓝牙模块获取这个温度给klipper，不过因为是蓝牙，实效性不是太高就是了，不过用作仓温等应该问题不大

## 安装方法
复制 `xiaomi_blue.py` 到 `klipper/klippy/extras`

安装klipper环境的python的蓝牙bluepy库以及系统支持
```shell
sudo apt install libglib2.0-dev

~/klippy-env/bin/pip install bluepy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

最后重启klipper服务
```shell
sudo service klipper restart
```

## 使用方法

在klipper的printer.cfg配置文件中增加传感器的配置段落
```ini
# 传感器配置

[xiaomi_blue] # 加载模块

[temperature_sensor xiaomi]
sensor_type: XIAOMI_BLUE # 传感器类型
mac_address: A4:C1:38:10:73:D4 # 蓝牙的传感器mac地址，必须参数，具体可以通过米家连接蓝牙传感器后，通过传感器的关于设备菜单中获得
# report_time: 30 # 默认的30秒读取一次数据（蓝牙不要读取的太频密，最小10秒）非必需

# 查询的温湿度的宏代码
[gcode_macro QUERY_XIAOMI]
gcode:
    {% set sensor = printer["xiaomi_blue xiaomi"] %}
    {action_respond_info(
        "Temperature: %.2f C\n"
        "Humidity: %.2f%%" % (
            sensor.temperature,
            sensor.humidity))}

