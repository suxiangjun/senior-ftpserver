#!/usr/bin/env python
#-*- coding:utf-8 -*-
import socket,os,json
import socket, hashlib,os,sys,time
__author = "susu"
class FtpClient(object):
    def __init__(self):
        self.client=socket.socket()
        self.now_dir=None
    def help(self):
        msg='''
ls           #查看文件
pwd          #查看当前迷路
cd ../       #返回上一层目录
get filename #下载文件
put filename #上传文件
q            #退出程序  
        '''
        print(msg)

    def connect(self,ip,port):
        self.client.connect((ip, port))
        while True:
            self.username=input("FTP账号：")
            self.client.send(self.username.encode())
            received1=eval(self.client.recv(1024).decode())
            if received1[1]==1:
                print(received1[0])
                self.username=input("新账号名：")
                for i in range(3):
                    self.password1=input("密码：")
                    if not self.password1:continue
                    self.password2=input("请再输入一次：")
                    if not self.password2: continue
                    if self.password1==self.password2:
                        d=str([self.username,self.password1])
                        self.client.send(d.encode())   #发送用户名和密码到服务端
                        print(self.client.recv(1024).decode())
                        self.help()
                        self.interactive()
                else:
                    print("输错3次，再见")
                    sys.exit()
            else:
                print(received1[0])
                for i in range(3):
                    password=input("密码：")
                    if not password:continue
                    if password==received1[1]:
                        self.help()
                        self.interactive()
                else:
                    print("输错3次，再见")
                    sys.exit()

    #上传文件
    def cmd_put(self,*args):
        cmd_split=args[0].split()
        if len(cmd_split)>1:
            filename=cmd_split[1]
            if os.path.isfile(filename):
                filesize=os.stat(filename).st_size
                msg_dic={
                    "action":"put",
                    "filename":filename,
                    "username":self.username,
                    "size":filesize,
                    "overridden":True
                }
                self.client.send(str(json.dumps(msg_dic)).encode("utf-8"))
                server_response=self.client.recv(1024)
                if server_response.decode().startswith("sorry"):
                    print(server_response.decode())
                else:
                    total=0
                    f=open(filename,"rb")
                    for line in f:
                        self.client.send(line)
                        total+=len(line)
                        sys.stdout.write("\r{}>%{}".format("="*int(total/filesize*100),int(total/filesize*100)))
                        sys.stdout.flush()
                    else:
                        print("file upload done")
                        f.close()
    #下载文件
    def cmd_get(self,*args):
        cmd_split=args[0].split()
        if len(cmd_split)>1:
            filename=cmd_split[1]
            msg_dic={
                    "action":"get",
                    "filename":filename,
                    "username":self.username,
                    "overridden":True
                }
            self.client.send(str(json.dumps(msg_dic)).encode("utf-8"))
            y_n=self.client.recv(1024).decode()
            if y_n=="y":
                self.client.send(b"ack")
                server_respose = self.client.recv(1024)
                print("文件大小: %s bytes"%server_respose.decode() )
                self.client.send("ready to recv file".encode())
                file_total_size = int(server_respose.decode())
                revived_size = 0
                m = hashlib.md5()  # 生成MD5对象
                with open(filename, "wb") as f:
                    while revived_size < file_total_size:
                        data = self.client.recv(1024)
                        revived_size += len(data)
                        m.update(data)  # 计算数据接收的MD5值
                        f.write(data)
                        sys.stdout.write("\r{}>%{}".format("="*int(revived_size/file_total_size*100),int(revived_size*100/file_total_size)))
                        sys.stdout.flush()
                    else:
                        client_md5_vaule = m.hexdigest()  # 生成接收数据的MD5值16进制形式
                        self.client.send("ready to recv file md5 value".encode())
                        server_md5_value = self.client.recv(1024)  # 接收客户端的MD5值
                        if client_md5_vaule == server_md5_value.decode():  # 客户端和服务端的MD5值做比较
                            print("file recv done")
                        else:
                            print(client_md5_vaule, server_md5_value.decode())
            else:
                print("文件不存在")
    #查看文件
    def cmd_ls(self,*args):
        msg_dic = {
            "action": "ls",
            "username": self.username
        }
        self.client.send(str(json.dumps(msg_dic)).encode("utf-8"))
        allfile=eval(self.client.recv(1024).decode())
        if allfile[0]:
            if len(allfile[0])>1:
                for j in allfile[0]:
                    print("\33[31m%s\33[0m" % j)
            else:
                print("\33[31m%s\33[0m" % allfile[0][0])
        if allfile[1]:
            if len(allfile[1])>1:
                for k in allfile[1]:
                    print(k)
            else:
                print(allfile[1][0])
    #切换目录
    def cmd_cd(self,*args):
        cmd_split=args[0].split()
        msg_dic = {
            "action": "cd",
            "dir": cmd_split[1]
        }
        self.client.send(str(json.dumps(msg_dic)).encode("utf-8"))
        self.cmd_ls()

    def cmd_pwd(self,*args):
        msg_dic = {
            "action": "pwd",
            "username": self.username
        }
        self.client.send(str(json.dumps(msg_dic)).encode("utf-8"))
        print(self.client.recv(1024).decode())

    #交互界面
    def interactive(self):
        while True:
            cmd=input(">>").strip()
            if len(cmd)==0 or cmd=="cd":continue
            elif cmd=="q":sys.exit()
            cmd_str=cmd.split()[0]
            if hasattr(self,"cmd_%s"%cmd_str):
                func=getattr(self,"cmd_%s"%cmd_str)
                func(cmd)
            else:
                self.help()
c=FtpClient()
c.connect("localhost",9999)