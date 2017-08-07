#coding:gbk
'''
Created on 2017��8��7��
@author: cynthia
''' 
__author__ = 'wangyan' 

from socket import socket, AF_INET, SOCK_DGRAM
import struct
import binascii
import functools
import types
import os
from functools import reduce


class SomeCustomError(Exception):
    def __init__(self,message):
        super(SomeCustomError,self).__init__()
        self.message = message

#����װ����
def send_session_start():
    def decorator(func):
        def wrapper(self,*args, **kw):
            print("send session start")
            self.serial_number = 1
            #ƴ�ӱ���
            #��ϢID��2B�� ��ˮ�ţ�2B�� ��Ϣ����(2B)  ��Ϣ���ݣ�b'session_start'��
            format= "!H H H %ds" % len(b'session start')
            data = struct.pack(format,0x8E00,self.serial_number,len(b'session start'),b'session start')
            self.send_packet(data)
            #���ý��ճ�ʱΪ1s
            self.sock.settimeout(1)
            #���ձ���
            data = self.recv_packet()
            #������ϢID�Ƿ�Ϸ�
            msg_id = struct.unpack("!H",data[0:2])[0]
            if msg_id != 0x8E01:
                raise SomeCustomError('when send session start, msg_id is error')
            return func(self)
        return wrapper
    return decorator

def send_session_end():
    def decorator(func):
        def wrapper(self,*args, **kw):
            msg = func(self)
            print("send session end")
            #��ϢID��2�� ��ˮ�ţ�2B�� ��Ϣ����(2B)  ��Ϣ���ݣ�'session end'��
            format = "!H H H %ds" % len(b'session end')
            data = struct.pack(format,0x8E0A,self.serial_number,len(b'session end'),b'session end')
            #������Ϣ
            self.send_packet(data)
            #���ý��ճ�ʱΪ1s
            self.sock.settimeout(1)
            data = self.recv_packet()
            msg_id = struct.unpack('!H',data[0:2])[0]
            if msg_id != 0x8E0B:
                raise SomeCustomError('when send session end, msg_id is error')
            return msg
        return wrapper
    return decorator

class MySock(object):
    __slots__ = ('__serial_number','sock','__serverIp','__serverPort')
    def __init__(self,serverIp,serverPort):
        self.__serial_number = 1
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.__serverIp = serverIp
        self.__serverPort = serverPort
    def __str__(self):
        return 'MySock object (serial_number:%d,serverIp:%s,serverPort:%d)' % (self.__serial_number,self.__serverIp,self.__serverPort)
    __repr__ = __str__
    @property
    def serial_number(self):
        return self.__serial_number
    @serial_number.setter
    def serial_number(self,value):
        self.__serial_number = value
       
    #������Ϣ��0x7e msg ehecksum 0x7e  
    #eg:0x7e ��ϢID��2�� ��ˮ�ţ�2B�� ��Ϣ����(2B)  ��Ϣ���ݣ��䳤�� У���루2B��0x7e
    def send_packet(self,data):
        #ƴ����Ϣͷ 0x7e
        format = 'B %ds B' % len(data)
        packet = struct.pack(format,0x7E,data,0x7E)
        self.sock.sendto(packet, (self.__serverIp,self.__serverPort))
        #������ˮ��
        self.serial_number = self.serial_number + 1    

    #�հ�0x7e ��ϢID��2�� ��ˮ�ţ�2B�� ��Ϣ����(2B)  ��Ϣ���ݣ��䳤�� 0x7e
    def recv_packet(self):
        data,addr = self.sock.recvfrom(2048) 
        #��ӡ�յ�����Ϣ
        print ('recv = ',binascii.hexlify(data))
        #������ˮ��
        pack_index = struct.unpack("!H",data[3:5])[0]
        if pack_index + 1 > self.serial_number:
            self.serial_number = pack_index + 1
        return data[1:len(data) - 1]

    #��������״̬
    @send_session_start()
    @send_session_end()  
    def send_heartbeat(self):
        print("send heart beat")
        #��ϢID��2�� ��ˮ�ţ�2B�� ��Ϣ����(2B)  ��Ϣ���ݣ�1��
        format = "!H H H %ds" % len(b'heart beat')
        data = struct.pack(format,0x8E08,self.serial_number,len(b'heart beat'),b'heart beat')
        self.send_packet(data)
        data = self.recv_packet()
        msg_id = struct.unpack('!H',data[0:2])[0]
        if msg_id != 0x8E09:
            raise SomeCustomError('when send heart beat, msg_id is error')
    
    def close(self):
        self.sock.close()
        
if __name__ == '__main__': 
    sock = MySock('127.0.0.1',20000)
    try:
        sock.send_heartbeat()
    except IOError:
        print("sock timeout")
    except SomeCustomError as x:
        print(x.message)
    sock.close()