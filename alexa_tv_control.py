import logging
import os
from urllib import request as urrequest
from time import sleep
import socket
from flask import Flask
from flask_ask import Ask, session, question, statement

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
 
STATUSON = ["encendido", "enciende", "encienda" ] 
STATUSOFF = ["apagado", "apaga", "apague" ]
ACCIONESTV = ["se calle", "se apague", "ponga", "baje el volumen", "suba el volumen", "se encienda", "salga de netflix"]
CANALES = ["la1", "la2", "etb1", "etb2", "tele5", "antena3", "cuatro", "la6", "neox", "fdf", "efedefe", "discovery", "gol", "telebilbao", "tdt", "kodi", "satelite"]


def discover(timeout=0.05, mx=10):
    group = ("239.255.255.250", 1900)
    message = "\r\n".join([
        'M-SEARCH * HTTP/1.1',
        'HOST: {0}:{1}',
        'MAN: "ssdp:discover"',
        'ST: {st}','MX: {mx}','',''])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(timeout)
    message_bytes = message.format(*group, st="urn:dial-multiscreen-org:service:dial:1", mx=mx).encode('utf-8')
    sock.sendto(message_bytes, group)
    while True:
        try:
            response=str(sock.recv(1024))
            startofurl=response.find("LOCATION: ")
            endofurl=response.find("/dd.xml")
            ip_port=response[startofurl+10:endofurl]
            separator=ip_port.find(":",7)
            ip=ip_port[7:separator]
            port=ip_port[separator+1:]
            sock.close()
            req =urrequest.Request('http://'+str(ip)+':'+str(port)+'/dd.xml') 
            resp=urrequest.urlopen(req)
            info=dict(resp.info())
            return info['Application-URL']
        except socket.timeout:
            return "not_found"
            break
            
keyboard = {
    "volup" : 1016,
    "voldown" : 1017,
    "mute" : 1013,
    "source" : 1056,
    "power" : 1012,
    "0" : 1000,
    "1" : 1001,
    "2" : 1002,
    "3" : 1003,
    "4" : 1004,
    "5" : 1005,
    "6" : 1006,
    "7" : 1007,
    "8" : 1008,
    "9" : 1009
    }

channellist = {
    "la1" : 1,
    "la2" : 2,
    "etb1" : 3,
    "etb2" : 4,
    "tele5" : 5,
    "antena3" : 6,
    "cuatro" : 7,
    "la6" : 8,
    "neox" : 9,
    "fdf" : 10,
    "discovery" : 11,
    "gol" : 12,
    "telebilbao" : 13,
    }
        
def setchannel(url, channel):
    data ='<?xml version="1.0" ?><setcurrentchannel><channel rsn="'+str(channel)+'"/></setcurrentchannel>'
    data = data.encode('utf-8')
    req =  urrequest.Request(url+'vr/remote', data=data)
    urrequest.urlopen(req)

def sendkey(url, key ):
    data ='<?xml version="1.0" ?><remote><key code="'+str(key)+'"/></remote>'
    data = data.encode('utf-8')
    req =  urrequest.Request(url+'vr/remote', data=data)
    urrequest.urlopen(req)

def setnetflix(url):
    data ='<?xml version="1.0" ?><browserseturl><load url=http://www.portaltv.tv/swf/netflix/netflix.swf/></browserseturl>'
    data = data.encode('utf-8')
    req =  urrequest.Request(url+'vr/browserseturl', data=data)
    urrequest.urlopen(req)
    
@ask.launch
def launch():
    speech_text = 'Bienvenido al control de la television'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)
 
@ask.intent('intentluz', mapping = {'estado':'estado'})
def Gpio_Intent(estado):
    if estado in STATUSON:
        os.system('enciendeluces')
        return statement('Luces encendidas')
    elif estado in STATUSOFF:
        os.system('apagaluces')
        return statement('Luces apagadas')
    else:
        return statement('Lo siento , no has elegido un estado correcto para las luces')

@ask.intent('tv', mapping = {'acciontv':'acciontv', 'canal':'canal'})
def tv_Intent(acciontv,canal):
    if acciontv in ACCIONESTV:
        url=discover()
        if url == "not_found":
            return statement('La tele no está encendida o no la encuentro.')
        if acciontv == "ponga":
            if canal in CANALES:
                if canal == "tdt" :
                    sendkey(url,keyboard["source"])
                    sleep(0.02)
                    sendkey(url,keyboard["1"])
                    return statement('he puesto la te de te.')
                elif canal == "kodi" :
                    sendkey(url,keyboard["source"])
                    sleep(0.02)
                    sendkey(url,keyboard["4"])
                    return statement('he puesto'+str(canal)+'.')
                elif canal == "satelite" :
                    sendkey(url,keyboard["source"])
                    sleep(0.02)
                    sendkey(url,keyboard["5"])
                    return statement('he puesto'+str(canal)+'.')
                else: 
                    setchannel(url,channellist[canal])
                    return statement('he puesto'+str(canal)+'.')

            else:
                return statement('El canal '+ str(canal)+'no existe')
        elif acciontv == "se calle":
            sendkey(url,keyboard["mute"])
            return statement('He callado la tele.')
        elif acciontv == "se apague":
            sendkey(url,keyboard["power"])
            return statement('He apagado la tele.')
        elif acciontv == "se encienda":
            sendkey(url,keyboard["power"])
            return statement('He encendido la tele.')
        elif acciontv == "baje el volumen":
            sendkey(url,keyboard["voldown"])
            sleep(0.02)
            sendkey(url,keyboard["voldown"])
            sleep(0.02)
            sendkey(url,keyboard["voldown"])
            sleep(0.02)
            sendkey(url,keyboard["voldown"])
            return statement('He bajado el volumen.')
        elif acciontv == "suba el volumen":
            sendkey(url,keyboard["volup"])
            sleep(0.02)
            sendkey(url,keyboard["volup"])
            sleep(0.02)
            sendkey(url,keyboard["volup"])
            sleep(0.02)
            sendkey(url,keyboard["volup"])
            return statement('He subido el volumen.')
        elif acciontv == "salga de netflix":
            sendkey(url,keyboard["power"])
            sleep(0.02)
            sendkey(url,keyboard["power"])
            
            return statement('He salido de netflix.')
    else:
        return statement('Perdona no he entendido el comando de la tele.')
        
@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'Hola! puedes pedirme que ponga canales, que suba y baje el volumen, o que apague y encienda la tele.'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)
 
 
@ask.session_ended
def session_ended():
    return "{}", 200
 
 
if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(host='0.0.0.0',debug=True)
 
