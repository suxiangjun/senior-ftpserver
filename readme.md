## 项目名称：ftp工具

*本软件只在python3环境下运行。*

#### 实现功能

- 1.用户加密认证
- 2.多用户同时登陆
- 3.每个用户有自己的家目录且只能访问自己的家目录
- 4.对用户进行磁盘配额
- 5.用户可以登陆server后，可切换目录
- 6.查看当前目录下文件
- 7.上传下载文件，保证文件一致性
- 8.传输过程中现实进度条

#### 程序架构

```php+HTML
├──ftp-client                # 客户端
│      └──ftp_client.py          #  ftp客户端执行程序     
│                   
│
├──ftp-server                #服务端
│      │──bin                       
│      │   ├──myftp.py      #  ftp服务端执行程序   
│      │   └──__init__.py
│      │──conf                       
│      │   ├──setting.py      #  ftp服务端配置   
│      │   └──__init__.py

│      └──data               # 用户数据存储的地方
│      │    ├──password.bak  # 存所有用户的账户数据基本数据
│      │	├──password.dat
│      │    └──password.dir
│      │──home               # 用户家目录
│      └──log                # 日志目录
│          ├──ftp.log        # 用户登入和操作日志
│          └──__init__.py
│──README
```


`注意事项：`下载/上传的文件，和客户端程序所在目录相同

[博客地址]: http://www.cnblogs.com/xiangjun555

