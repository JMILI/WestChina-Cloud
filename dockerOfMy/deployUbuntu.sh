#!/bin/sh

# 使用说明，用来提示输入参数
usage() {
	echo "Usage: sh 执行脚本.sh [port|base|modules|monitor|stop|rm]"
	exit 1
}

# 开启所需端口
port(){
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  8848 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  9849 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  6379 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  15672 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  4369 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  5672 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  25672 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  3306 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  9000 -j  ACCEPT
	sudo iptables  -A  INPUT  -p tcp  -m  multiport --dports  9001 -j  ACCEPT
	iptables-save
	sudo netfilter-persistent save
  sudo netfilter-persistent reload
}

# 启动基础环境（必须）
base(){
	docker-compose up --build -d westChina-mysql westChina-redis westChina-rabbit westChina-minio westChina-nacos
}
nacos(){
	docker-compose up --build -d westChina-nacos
}
# 启动程序模块（必须）
modules(){
	docker-compose up -d westChina-gateway westChina-auth westChina-modules-system westChina-modules-tenant westChina-nginx
}

# 启动程序模块 | 次要 | 根据需求启动
monitor(){
	docker-compose up -d westChina-modules-file westChina-modules-gen westChina-modules-job westChina-visual-monitor
}

# 关闭所有环境/模块
stop(){
	docker-compose stop
}

# 删除所有环境/模块
rm(){
	docker-compose rm
}

# 根据输入参数，选择执行对应方法，不输入则执行使用说明
case "$1" in
"port")
	port
;;
"base")
	base
;;
"nacos")
	nacos
;;
"modules")
	modules
;;
"monitor")
	monitor
;;
"stop")
	stop
;;
"rm")
	rm
;;
*)
	usage
;;
esac
