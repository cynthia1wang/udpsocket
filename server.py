#coding:gbk
'''
Created on 2017年8月7日
@author: cynthia
''' 
import struct
import binascii
from socket import socket, AF_INET, SOCK_DGRAM
sock_recv = socket(AF_INET, SOCK_DGRAM) 
address = ('127.0.0.1', 20000) 
sock_recv.bind(address)

while True:  
    data, addr = sock_recv.recvfrom(2048)  
    print ('recv = ',binascii.hexlify(data))
    if not data:  
        print("client has exist")  
        break  
    #0x7e 消息ID（2） 流水号（2B） 消息长度(2B)  消息内容（变长） 0x7e
    msg_id = struct.unpack('!H',data[1:3])[0]
    serial_number = struct.unpack('!H',data[3:5])[0]
    if msg_id == 0x8E00:
        fromat = '!B H H H %ds H' % len(b'session start')
        data = struct.pack(fromat,0x7E,0x8E01,serial_number+1,len(b'session_start'),b'session_start',0x7e)
    elif msg_id == 0x8E0A:
        fromat = '!B H H H %ds H' % len(b'session end')
        data = struct.pack(fromat,0x7E,0x8E0B,serial_number+1,len(b'session_end'),b'session_end',0x7e)
    elif msg_id == 0x8E08:
        fromat = '!B H H H %ds H' % len(b'heart beat')
        data = struct.pack(fromat,0x7E,0x8E09,serial_number+1,len(b'session_end'),b'session_end',0x7e)
    else:
        print('message is invalid')
        fromat = '!B H H H %ds H' % len(b'message id is error')
        data = struct.pack(fromat,0x7E,0x8EFF,serial_number+1,len(b'message id is error'),b'message id is error',0x7e)
        continue
    sock_recv.sendto(data,addr)  
sock_recv.close()  