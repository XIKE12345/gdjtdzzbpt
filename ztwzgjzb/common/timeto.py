#coding:UTF-8
import time

#获取当前时间
times = 1581741663000

time_now = int(times / 1000)
print(time_now)
#转换成localtime
time_local = time.localtime(time_now)
#转换成新的时间格式(2016-05-09 18:59:20)
dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)

print(dt)