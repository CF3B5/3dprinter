# Klipper 支持系统命令的扩展

让Klipper的Gcode增加支持运行系统命令的功能

复制 `shell_command.py` 到 `klipper/klippy/extras`

在klipper的配置文件`printer.cfg`中加入需要运行的命令，例如
```ini
[shell_command my_command]
command: date
```

重启klipper服务
`service klipper restart`

重启成功后，在控制台输入
```
SHELL_COMMAND NAME=my_command
```
就回执行系统date这个命令，并且命令的返回结果会回显在控制台中。
