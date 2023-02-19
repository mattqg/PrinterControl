import serial
import serial.tools.list_ports
from time import sleep, time
from utils.utils import logger, docs
from gcode import GcodeHelper

class Printer(GcodeHelper):
    # 3D Printer Base Class which handles serial connection and gcode reading/writing methods

    def __init__(self, hwid, name):
        '''
        Parameters:
        hwid : str
            a string which will be compared to each COM port.hwid
        name : str
            the name of the printer for logging purposes i.e. 'Ender 3'
        '''

        self.name = name
        self._connect(hwid)

    def _connect(self, hwid):
        '''
        Parameters:
        hwid : str
            a string which will be compared to each COM port.hwid to find the printer

        Sets:
        self.ser : class 'serial.Serial'
            serial object for the port matching the hwid
        '''

        ## list all ports and set device_port to the first port with specified hwid in the port's hwid
        ports = list(serial.tools.list_ports.comports())
        device_port = None
        for p in ports:
            if hwid in p.hwid:
                logger.info(f'{self.name} found on {p.device}')
                device_port = p.device
                break

        ## attempt to connect to serial with the specified device_port. raise error if connection unsuccessful
        self.ser = serial.Serial(port=device_port, baudrate='115200',bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE)
        if self.ser.isOpen():
            logger.info(f'Connected to {self.name}')
        else:
            logger.error(f'Unable to Connect to {self.name}')
            raise ConnectionError(f'Unable to Connect to {self.name}')

        # sleep to allow initial handshake
        logger.debug(f'Sleeping for initial handshake')
        sleep(10)

    
    def begin_log(self, file_path):
        '''
        Parameters:
        filename : str
            a string which specifies gcode output file path relative to main.py

        Sets:
        self._logging_gcode : bool
            sets attribute which controls whether gcode should be logged to an output file
        self._gcode_file : str
            sets filepath for the gcode output
        '''

        # clear file and set attributes
        open(file_path, "w").close()
        self._logging_gcode = True
        self._gcode_file = file_path
        logger.debug(f'Gcode logging turned on. Output set to {self._gcode_file}')

    def _log_gcode_cmd(self, cmd):
        '''
        Parameters:
        cmd : str
            Gcode command to be written to the output self._gcode_file
        '''

        with open(self._gcode_file, 'w') as f:
            f.write((cmd + '\n'))
            return

    def begin_stdin(self):
        '''
        Begin terminal input to write Gcode line by line. Use q to quit.

        '''

        while True:
            raw_input = input(">> ")
            if 'q' in raw_input:
                return
            if raw_input and self.ser:
                self.write(raw_input.strip())

    def _log_docs(self, cmd):
        '''
        Looks up utils/marlin_gcode_helper.yml for descriptions of written gcode commands

        Parameters:
        cmd : str
            Gcode command to look up documentation from
        '''

        # grab gcode cmd type i.e. G1 X20 -> G1 for lookup
        split_cmds = cmd.split(" ")

        # look to marlin_gcode_helper.yml for brief information and log
        for split_cmd in split_cmds:  
            if split_cmd in docs.keys():
                info = docs[split_cmd]
                logger.info(f'''{cmd}: {info['brief'].strip()}''')

    def _wait_for_read(self):
        '''
        Delay until an 'ok' response is received from the printer. Timeout after 5 seconds if no response received.

        '''

        t = time()

        while True:
            line = self.ser.readline()
            # succesful response
            if line == b'ok\n':
                logger.info(f'Response: {str(line)}')
                sleep(1)
                return

            # timeout
            elapsed = time() - t
            if elapsed > 60:
                logger.warning('Connection timed out. Command not written')
                return

    def write(self, cmd):
        '''
        Can be passed a single command (str) or multiple commands (list[str])
        Sends command logging request, encodes and sends command over serial, and initializes waiting for a response 

        Parameters:
        cmd : str | list[str]
            Gcode command(s) to send to printer. Multiple commands in a list will be sent sequentially.
        '''

        # single command
        if isinstance(cmd, str):
            logger.debug(f'''Writing cmd: {cmd.encode('ascii')}''')
            # logging
            self._log_docs(cmd)
            if self._logging_gcode:
                self._log_gcode_cmd(cmd)
            # writing command
            self.ser.write((cmd+"\r\n").encode('ascii'))
            # wait for read
            self._wait_for_read()
        # multiple commands
        elif isinstance(cmd, list):
            for i, single_cmd in enumerate(cmd):
                logger.debug(f'Writing cmd: {single_cmd}, {i/len(cmd)}% of full cmd')
                # logging
                self._log_docs(cmd)
                if self._logging_gcode:
                    self._log_gcode_cmd(single_cmd)
                # writing command
                self.ser.write((single_cmd+"\r\n").encode('ascii'))
                # wait for read
                self._wait_for_read()
        # incorrect type
        else:
            logger.error('Write input must be a string or list')
            raise TypeError
