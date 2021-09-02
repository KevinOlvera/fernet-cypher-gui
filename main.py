import logging
import os
import sys
import time

from pathlib import Path

import PySimpleGUI as sg

from cryptography.fernet import Fernet


ROOT_PATH = Path()
DEFAULT_KEY_PATH = ROOT_PATH / 'default.key'


class Handler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        global buffer
        record = f'[{record.asctime}][{record.name}] [{record.levelname}] > \n{record.message}'
        buffer = f'{buffer}\n{record}'.strip()
        window['log'].update(value=buffer)


class FernetCypher:
    """Fernet guarantees that a message encrypted using it cannot be manipulated or read without the key. Fernet is an implementation of symmetric (also known as “secret key”) authenticated cryptography.

    Attributes:
        _key: the key binary used to encrypt/decrypt messages
        _key_path: if exists is the path to the key file
    """
    __slots__ = ['_key', '_key_path', '_status']

    def __init__(self, key_path: Path = None):
        if key_path:
            self.load_key(key_path)
        else:
            logging.info('You must load a key before encrypt or decrypt a message. To load a key, use the method load_key()')
        self._status = True

    def generate_key(self, key_path: Path = DEFAULT_KEY_PATH):
        """This method generate a key file to be used to encrypt and decrypt messages.

        Args:
            key_path (Path): Path of the key file. The default value is DEFAULT_KEY_PATH. The key will be located in the current directory with the name "default.key".
        """
        try:
            logging.debug('Generating the key...')
            self._key = Fernet.generate_key()
            with open(key_path.resolve(), 'wb') as file:
                file.write(self._key)
            logging.debug(f'Key written to {key_path.resolve()}')
            return True
        except Exception as error:
            logging.error(error)
            return False

    def load_key(self, key_path: Path):
        """This method loads a key from a path

        Args:
            key_path (Path): Path of the key file.
        """
        try:
            logging.debug(f'Loading key from {key_path.resolve()}')
            self._key = open(key_path.resolve(), 'rb').read()
        except Exception as error:
            logging.error(error)
            sys.exit(-1)

    def encrypt_message(self, message: str) -> str:
        """This method encrypts a message.

        Args:
            message (str): The message to be encrypted.

        Returns:
            str: The encrypted message.
        """
        try:
            logging.debug('Encrypting message...')
            f = Fernet(self._key)
            return f.encrypt(message.encode()).decode()
        except Exception as error:
            logging.error(error)
            self._status = False
            # sys.exit(-1)

    def decrypt_message(self, encrypted_message: str) -> str:
        """This method decrypts a message.

        Args:
            encrypted_message (str): The message to be decrypted

        Returns:
            str: The decrypted message.
        """
        try:
            logging.debug('Decrypting message...')
            f = Fernet(self._key)
            return f.decrypt(encrypted_message.encode()).decode()
        except Exception as error:
            logging.error(error)
            self._status = False
            # sys.exit(-1)

    @property
    def status(self) -> bool:
        return self._status


def load_message(message_path: Path) -> str:
    try:
        logging.debug(f'Loading message from {message_path.resolve()}')
        return open(message_path.resolve(), 'r').read()
    except Exception as error:
        logging.error(error)
        # sys.exit(-1)

def write_message(message: str, message_path: Path):
    try:
        logging.debug(f'Writing message on {message_path.resolve()}')
        file = open(message_path.resolve(), 'w')
        file.write(message)
        file.close()
    except Exception as error:
        logging.error(error)
        # sys.exit(-1)


if __name__ == '__main__':
    # start to measure the execution time
    # start = time.perf_counter()

    # configure the basic configuration for the logging module
    logging.basicConfig(
        format='[%(asctime)s][%(name)s] %(levelname)s: %(message)s',
        level=logging.DEBUG,
        filename='run.log'
    )

    buffer = ''
    ch = Handler()
    ch.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(ch)

    sg.theme('SystemDefault')

    left_column = [
        [
            sg.Text('Welcome!', font='Helvetica 18', justification='left', expand_x=True)
        ],
        # [sg.HorizontalSeparator()],
        [
            sg.Text('Do you have a key file? if not, please generate a new one.', justification='left', expand_x=True, pad=((5, 5), (30, 5)))
        ],
        [
            sg.Input(enable_events=True, key='-KEY_NAME-', default_text='default.key', expand_x=True),
            sg.Button('Generate', enable_events=True, key='-GENERATE_KEY-', size=(10, 1)),
        ],
        [
            sg.Text('Key File'),
            sg.In(enable_events=True, key='-KEY_FILE-', expand_x=True),
            sg.FileBrowse(size=(10, 1), file_types=(('Key Files', '*.key'),))
        ],
        [
            sg.Text('Message File'),
            sg.In(enable_events=True, key='-MESSAGE_FILE-', expand_x=True),
            sg.FileBrowse(size=(10, 1), file_types=(('ALL Files', '*.*'),))
        ],
        [
            sg.Button('Encrypt Message', enable_events=True, key='-ENCRYPT_MESSAGE-', expand_x=False, size=(15, 1), pad=((5, 5), (20, 5))),
        ],
        [
            sg.Button('Decrypt Message', enable_events=True, key='-DECRYPT_MESSAGE-', expand_x=False, size=(15, 1)),
        ],
        [
            sg.Button('Exit', enable_events=True, key='-EXIT-', expand_x=False, size=(15, 1), button_color=('red'))
        ],
        [
            sg.Text('Author: Kevin Olvera', justification='left', expand_x=True, pad=((5, 5), (20, 5)))
        ]
    ]

    output_column = [
        [sg.Text('Output:')],
        [sg.Multiline(size=(35,20), key='log', autoscroll=True, no_scrollbar=True)]
    ]

    app_layout = [
        [
            sg.Column(left_column, element_justification='right'),
            sg.VSeperator(),
            sg.Column(output_column),
        ]
    ]

    window = sg.Window(
        title='Program 0. FernetCypher', 
        layout=app_layout,
        font="Helvetica 12",
    )

    # run the Event Loop
    while True:
        try:
            event, values = window.read()
            if event == 'Exit' or event == sg.WIN_CLOSED:
                logging.info('Program finished by closing window')
                sys.exit(0)
                # logging.info(sg.theme_list())
                break
            # key file path to be used to encrypt/decrypt messages
            if event == '-KEY_FILE-':
                key_file_path = Path(values['-KEY_FILE-'])
                logging.info(f'Selected key file: {key_file_path.resolve()}')

            if event == '-MESSAGE_FILE-':
                if values['-KEY_FILE-'] != '':
                    message_file_path = Path(values['-MESSAGE_FILE-'])
                    logging.info(f'Selected message file: {message_file_path.resolve()}')
                    message = load_message(message_file_path)
                else:
                    logging.info('Please generate or select a key file')
                    window['-MESSAGE_FILE-'].update('')
                    values['-MESSAGE_FILE-'] = ''

            if event == '-ENCRYPT_MESSAGE-':
                if values['-KEY_FILE-'] != '' and values['-MESSAGE_FILE-'] != '':
                    f_cypher = FernetCypher(key_file_path)
                    encrypted = f_cypher.encrypt_message(message)
                    if f_cypher.status:
                        encrypted_name = message_file_path.stem + '_C' + message_file_path.suffix
                        message_path = ROOT_PATH / encrypted_name
                        write_message(encrypted, message_path)
                    else:
                        logging.info('Encryption failed')
                    window['-KEY_FILE-'].update('')
                    values['-KEY_FILE-'] = ''
                    window['-MESSAGE_FILE-'].update('')
                    values['-MESSAGE_FILE-'] = ''
                    window['-KEY_NAME-'].update('')
                    values['-KEY_NAME-'] = ''
                    key_file_path = None
                    message_file_path = None
                    f_cypher = None
                else:
                    logging.info('Please generate or select a key file')
                    logging.info('No message file selected')

            if event == '-DECRYPT_MESSAGE-':
                if values['-KEY_FILE-'] != '' and values['-MESSAGE_FILE-'] != '':
                    f_cypher = FernetCypher(key_file_path)
                    decrypted = f_cypher.decrypt_message(message)
                    if f_cypher.status:
                        decrypted_name = message_file_path.stem + '_D' + message_file_path.suffix
                        message_path = ROOT_PATH / decrypted_name
                        write_message(decrypted, message_path)
                    else:
                        logging.info('Decryption failed')
                    window['-KEY_FILE-'].update('')
                    values['-KEY_FILE-'] = ''
                    window['-MESSAGE_FILE-'].update('')
                    values['-MESSAGE_FILE-'] = ''
                    window['-KEY_NAME-'].update('')
                    values['-KEY_NAME-'] = ''
                    key_file_path = None
                    message_file_path = None
                    f_cypher = None
                else:
                    logging.info('Please select a key file')
                    logging.info('No encrypted message file selected')

            if event == '-GENERATE_KEY-':
                f_cypher = FernetCypher()
                f_cypher.generate_key(ROOT_PATH / values['-KEY_NAME-'])
                window['-KEY_FILE-'].update('')
                values['-KEY_FILE-'] = ''
                window['-MESSAGE_FILE-'].update('')
                values['-MESSAGE_FILE-'] = ''
                window['-KEY_NAME-'].update('')
                values['-KEY_NAME-'] = ''
                key_file_path = None
                message_file_path = None
                f_cypher = None

            if event == '-EXIT-':
                logging.info('Program finished by exit button')
                break
        except Exception as error:
            logging.error(error)
            sys.exit(-1)

    window.close()

    # end measure of the execution time
    # elapsed = time.perf_counter() - start
    # logging.info(f'Program finished in {elapsed:0.2f} seconds.')
