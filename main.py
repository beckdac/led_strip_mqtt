#!/usr/bin/env python

import socket
import sys
import paho.mqtt.client as mqtt
import time
import datetime


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("/led_strip/#")
    client.subscribe("/led_strip/reset")
    client.subscribe("/led_strip/RGB")
    client.subscribe("/led_strip/R")
    client.subscribe("/led_strip/G")
    client.subscribe("/led_strip/B")
    client.subscribe("/led_strip/RUN")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == "/led_strip/reset":
        print("received reset command")
    elif msg.topic == "/led_strip/RGB":
        print("setting RGB to " + str(msg.payload))
    elif msg.topic == "/led_strip/R":
        print("setting R to " + str(msg.payload))
    elif msg.topic == "/led_strip/G":
        print("setting G to " + str(msg.payload))
    elif msg.topic == "/led_strip/B":
        print("setting B to " + str(msg.payload))
    elif msg.topic == "/led_strip/RUN":
        print("setting RUN state to " + str(msg.payload))
    else:
        print("unexpected command: "+msg.topic+" := "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.lan", 1883, 60)
client.publish("/node", '{ "node": "led_strip", "features": [ "reset", "LHZ", "RGB", "R", "G", "B", "RUN" ] }');
# run the mqtt client in background thread
client.loop_start()

# TCP pieces
def readlines(sock, recv_buffer=4096, delim='\n'):
    buffer = ''
    data = True
    while data:
        #print "readlines while data"
        data = sock.recv(recv_buffer)
        buffer += data

        while buffer.find(delim) != -1:
            line, buffer = buffer.split('\n', 1)
            yield line
    return

# loop and query then update
i = 0
while True:
    print i
    i = i + 1
    print datetime.datetime.now()

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('led_strip.lan', 23)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    try:
        # Send data
        message = 'LHZ\n'
        print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message)
        print "sent"

        for line in readlines(sock):
            print line
            # do something
            resp = line.split()[0]
            if (resp == "OK"):
                print line
                break
            elif (resp == "ERROR"):
                print line
                break
            elif (resp == "light" and line.split()[1] == "frequency:"):
                client.publish("/led_strip/LHZ", line.split()[2]);
                print "published"
                break

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()

    time.sleep(50)
