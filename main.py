#!/usr/bin/env python

import socket
import sys
import paho.mqtt.client as mqtt
import time
import datetime

import logging


logging.basicConfig(filename='led_strip_mqtt.log', level=logging.INFO)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.debug("Connected with result code "+str(rc))
    #client.subscribe("/led_strip/#")
    client.subscribe("/led_strip/reset")
    client.subscribe("/led_strip/RGB")
    client.subscribe("/led_strip/R")
    client.subscribe("/led_strip/G")
    client.subscribe("/led_strip/B")
    client.subscribe("/led_strip/state")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    doCommand = None

    if msg.topic == "/led_strip/reset":
        logging.info("received reset command")
        doCommand = "RESET\n"
    elif msg.topic == "/led_strip/RGB":
        logging.info("setting RGB to " + str(msg.payload))
    elif msg.topic == "/led_strip/R":
        cV = int(float(str(msg.payload)) * 2.55)
        logging.info("setting R to " + str(cV))
        doCommand = "RED " + str(cV) + "\n"
    elif msg.topic == "/led_strip/G":
        cV = int(float(str(msg.payload)) * 2.55)
        logging.info("setting G to " + str(cV))
        doCommand = "GREEN " + str(cV) + "\n"
    elif msg.topic == "/led_strip/B":
        cV = int(float(str(msg.payload)) * 2.55)
        logging.info("setting B to " + str(cV))
        doCommand = "BLUE " + str(cV) + "\n"
    elif msg.topic == "/led_strip/state":
        logging.info("setting state to " + str(msg.payload))
        doCommand = str(msg.payload) + "\n"
    else:
        logging.info("unexpected command: "+msg.topic+" := "+str(msg.payload))

    if doCommand is None:
        return
    logging.info("doCommand: " + doCommand)

    sock = socketConnect()

    try:
        socketCommand(sock, doCommand)

    finally:
        socketDisconnect(sock)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.lan", 1883, 60)
client.publish("/node", '{ "node": "led_strip", "features": [ "reset", "LHZ", "RGB", "R", "G", "B", "state" ] }');
# run the mqtt client in background thread
client.loop_start()

# TCP pieces
def readlines(sock, recv_buffer=4096, delim='\n'):
    buffer = ''
    data = True
    while data:
        #logging.info "readlines while data"
        data = sock.recv(recv_buffer)
        buffer += data

        while buffer.find(delim) != -1:
            line, buffer = buffer.split('\n', 1)
            yield line
    return


def socketConnect():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('led_strip.lan', 23)
    logging.debug('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    return sock


def socketDisconnect(sock):
    logging.debug('closing socket')
    sock.close()

def socketCommand(sock, command):
        # Send data
        logging.debug('sending "%s"' % command)
        sock.sendall(command)
        logging.debug("sent")

        for line in readlines(sock):
            logging.info(line)
            # do something
            resp = line.split()[0]
            if (resp == "OK"):
                logging.debug(line)
                break
            elif (resp == "ERROR"):
                logging.debug(line)
                break
            elif (resp == "light" and line.split()[1] == "frequency:"):
                client.publish("/led_strip/LHZ", line.split()[2]);
                logging.debug("published")
                break


# loop and query then update
i = 0
while True:
    logging.debug(i)
    i = i + 1
    logging.debug(datetime.datetime.now())

    sock = socketConnect()

    try:
        command = 'LHZ\n'
        socketCommand(sock, command)

    finally:
        socketDisconnect(sock)

    time.sleep(50)
