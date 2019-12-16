from configparser import ConfigParser, RawConfigParser

parser = ConfigParser()
parser.read('bmsettings.ini')

ip = parser.get('bm', 'ip')
password = parser.get('config', 'password')
k = parser.get('config', 'k')
blocking = parser.getboolean('config', 'blocking')

def get_port(gamemode):
    return int(parser.get('bm', gamemode))

p = RawConfigParser()
p.read('bmsettings.ini')
uri = p.get('config', 'uri')