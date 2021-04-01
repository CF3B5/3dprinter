# coding=utf-8
# 命令行指令
# [shell_command test]
# command: ls
import logging
import subprocess


class ShellCommand:
    def __init__(self, config):
        # 获取printer 对象
        self.printer = config.get_printer()
        name = config.get_name().split()[1]
        self.command = config.get('command')
        logging.info("run shell command %s", self.command)
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_mux_command("SHELL_COMMAND", "NAME", name, self.run_cmd,
                                        desc="Run shell command.")
        pass

    def run_cmd(self, gcmd):
        args = gcmd.get('ARGS', '')
        logging.info("args => %s", args)
        script = self.command + " " + args
        result = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result_message = result.stdout.read().decode('utf-8')
        logging.info("run shell script %s => %s", script, result_message)
        gcmd.respond_info("result => " + result_message)
        pass


def load_config_prefix(config):
    return ShellCommand(config)
