from printer import Printer

if __name__ == '__main__':
    ender = Printer(hwid='1A86:7523', name='Ender 3')
    ender.begin_log('gcode/output.gcode')
    # ender.home()
    # ender.write('G1 X20')
    ender.begin_stdin()
