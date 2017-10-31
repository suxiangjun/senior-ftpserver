import socketserver
import json,os,time
import hashlib
import socket,os,shelve,sys,time,logging
basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
user_basedir=basedir+'/home/'
sys.path.append(basedir)
class MyTCPHandler(socketserver.BaseRequestHandler):
    #用户登陆控制
    user_now_dir="/"
    def user_login(self):
        self.username=self.request.recv(1024).decode()
        f=shelve.open(basedir+'/data/password')
        if self.username not in f:
            a="%s不存在，请注册"%self.username
            self.request.send(str([a,1]).encode())
            self.username_password=eval(self.request.recv(1024).decode())
            self.username=self.username_password[0]
            self.password=self.username_password[1]
            os.mkdir(basedir+"/home/"+self.username)
            self.dirhome=basedir+ "/home/"+self.username
            # self.username_password.append(self)  #[username,password,self]
            f[self.username_password[0]]=self.username_password
            f.close()
            self.request.send("恭喜你注册成功，请重新登陆。".encode())
            self.log("新注册%s用户"%self.username)
        else:
            self.request.send(str(["欢迎回来",f[self.username][1]]).encode())
            print("\33[32m{}\33[0m {}成功登陆".format(time.asctime(),self.username))
            self.log("%s用户成功登陆" % self.username)
            f.close()
    #上传文件
    def put(self,*args):
        '''接收客户端文件'''
        cmd_dic = args[0]
        filename = cmd_dic["filename"]
        filesize = cmd_dic["size"]
        user_dir=user_basedir+cmd_dic["username"]+self.user_now_dir+"/"
        if os.path.isfile(user_dir+filename):
            f = open(user_dir+filename + ".new","wb")
        else:
            f = open(user_dir+filename , "wb")
        self.request.send(b"200 ok")
        received_size = 0
        while received_size < filesize:
            data = self.request.recv(1024)
            f.write(data)
            received_size += len(data)
        else:
            print("file [%s] has uploaded..." % filename)
            self.log("{}成功上传{}文件".format(cmd_dic["username"], filename))
    #下载文件
    def get(self,*args):
        cmd_dic = args[0]
        filename = cmd_dic["filename"]
        username=cmd_dic["username"]
        user_dir=user_basedir+cmd_dic["username"]+self.user_now_dir+"/"
        print("{0}下载文件:".format(self.client_address[0]))
        self.log("{}用户下载{}文件".format(username, filename))
        if os.path.isfile(user_dir + filename):
            m = hashlib.md5()  # 生成MD5的对象
            self.request.send("y".encode())
            self.request.recv(1024)
            with open(user_dir+filename, "rb") as f:
                file_size = os.stat(user_dir+filename).st_size
                self.request.send(str(file_size).encode())  # send file size
                self.request.recv(1024)
                for line in f:
                    m.update(line)  # 计算md5值
                    self.request.send(line)
                print("file md5", m.hexdigest())
            self.request.recv(1024)  # 等待客户确认发送MD5值
            self.request.send(m.hexdigest().encode())  # 生成MD5值并且发送给客户端
        else:
            self.request.send("n".encode())

    def pwd(self,*args):
        self.request.send(self.user_now_dir.encode())

    def ls(self,*args):
        '''查看家目录文件'''
        cmd_dic = args[0]
        user_dir=user_basedir+cmd_dic["username"]+self.user_now_dir
        filenames=str(os.listdir(user_dir))
        self.request.send(filenames.encode())

    def cd(self,*args):
        cmd_dic = args[0]
        dir= cmd_dic["dir"].strip()
        if self.user_now_dir!="/":
            dir1="/"+dir
        else:
            dir1=dir
        print(dir)
        if dir == "../":
            print("before:",self.user_now_dir)
            if len(self.user_now_dir.split("/"))==2:
                self.user_now_dir="/"
                print("修改的目录：",self.user_now_dir)
            else:
                self.user_now_dir = "/".join(self.user_now_dir.split("/")[:-1])
                print("修改的目录：", self.user_now_dir)
        elif dir == "../../":
            if len(self.user_now_dir.split("/")) == 3:
                self.user_now_dir="/"
            elif len(self.user_now_dir.split("/")) > 3:
                self.user_now_dir = "/".join(self.user_now_dir.split("/")[:-2])
        else:
            self.user_now_dir+=dir1

    def handle(self):
        self.user_login()
        while True:
            try:
                self.data = self.request.recv(1024).strip()
                print("{} wrote:".format(self.client_address[0]))
                cmd_dic = json.loads(self.data.decode())
                action = cmd_dic["action"]
                if hasattr(self,action):
                    func = getattr(self,action)
                    func(cmd_dic)
            except ConnectionResetError as e:
                print("err",e)
                break

    @staticmethod
    def log(info):
        logging.basicConfig(filename=basedir + "/log/" + "ftp.log",
                            level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')
        logging.info(info)
if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    # Create the server, binding to localhost on port 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()