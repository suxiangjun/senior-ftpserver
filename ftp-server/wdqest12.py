#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author = "susu"

a="cd ../"
b=a.split()
print(b[1])
if b[1]=="../":
    print("ok")

a="/home/su/s/d"
print("/".join(a.split("/")[:-2]) )