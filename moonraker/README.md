# Moonraker 的Power支持系统命令
把power.py代码覆盖掉原来moonraker/moonraker/components文件夹中的power.py

```ini
# moonraker.conf
[power device_name]
type: shell_command
#   类型为shell_command
on: 
#   打开电源的系统命令
off: 
#   关闭电源的系统命令
```


