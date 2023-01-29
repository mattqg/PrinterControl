import serial
import serial.tools.list_ports
from time import sleep
from utils.utils import logger, docs


class Ender():
    def __init__(self, hwid = '1A86:7523', verbose=True):
        self._verbose = verbose
        port = self._get_port(hwid)
        self._connect(port)

    def _get_port(self, hwid):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if hwid in p.hwid:
                logger.info(f'Ender 3 found on {p.device}')
        return p.device

    def _connect(self, ser_port):
        self.ser = serial.Serial(port=ser_port, baudrate='115200', bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE)
        logger.info(f'Connected to Ender 3')
        sleep(6)


    def _wait_for_read(self):
        while True:
            line=self.ser.readline()
            # logger.info(f'reading: {line}')
            if line == b'ok\n':
                logger.info(f'Response: {str(line)}')
                sleep(1)
                break

    def write(self, cmd):
        if isinstance(cmd, list):
            for i,single_cmd in enumerate(cmd):
                # logger.info(f'Writing cmd: {single_cmd}, {i/len(cmd)}% of full cmd')
                self._log_docs(cmd)
                self.ser.write((single_cmd+"\r\n").encode('ascii'))
                self._wait_for_read()
        elif isinstance(cmd, str):
            # logger.info(f'''Writing cmd: {cmd.encode('ascii')}''')
            self._log_docs(cmd)
            self.ser.write((cmd+"\r\n").encode('ascii'))
            self._wait_for_read()
        else:
            logger.error('Write input must be a string or list')
            raise TypeError

    def home(self):
        self.write('G28')

    def begin_stdin(self):
        while True:
            raw_input = input(">> ")
            if 'q' in raw_input:
                return
            if raw_input:
                self.write(raw_input.strip())

    def _log_docs(self, cmd):
        split_cmd = cmd.split(" ")[0]
        if split_cmd in docs.keys():
            info = docs[split_cmd]
            logger.info(f'''{info['brief'].strip()}''')
        else:
            logger.warning(f'Docs not found for {split_cmd}')