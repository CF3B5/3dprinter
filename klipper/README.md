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

安装klipper环境的python的传感器支持库
```shell
~/klippy-env/bin/pip install sensor smbus spidev
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
[gcode_macro QUERY_ENCLOSURE]
gcode:
    {% set sensor = printer["htu21d_host enclosure"] %}
    {action_respond_info(
        "Temperature: %.2f C\n"
        "Humidity: %.2f%%" % (
            sensor.temperature,
            sensor.humidity))}
```


