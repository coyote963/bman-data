from configparser import ConfigParser

parser = ConfigParser()
parser.read('bmsettings.ini')

ip = parser.get('bm', 'ip')
port = parser.get('bm', 'port')
password = parser.get('bm', 'password')

blocking = parser.getboolean('bm', 'blocking')