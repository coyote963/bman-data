from configparser import ConfigParser, RawConfigParser

parser = ConfigParser()
parser.read('bmsettings.ini')

ip = parser.get('bm', 'ip')
password = parser.get('bm', 'password')

blocking = parser.getboolean('bm', 'blocking')

def get_port(gamemode):
    return int(parser.get('bm', gamemode))

p = RawConfigParser()
p.read('bmsettings.ini')
uri = p.get('bm', 'uri')