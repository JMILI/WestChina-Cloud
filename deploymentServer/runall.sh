#! /bin/sh
#1,启动所有jar包:sh runall.sh start all 或者./sh start all
#2,停止所有jar包:sh runall.sh stop all 或者./sh stop all
#3,重启所有jar包:sh runall.sh restart all 或者./sh restart all
#4,重启或者停止单个jar包,只需要将all替换为相应的模块代码就行

#westChina-auth.jar 9200
#westChina-gateway.jar 8080
#westChina-modules-system.jar 9600
#westChina-modules-ct.jar 9800
#westChina-modules-file.jar 9300
#westChina-modules-tenant.jar 9700
#westChina-modules-gen.jar 9400
#westChina-modules-job.jar 9500
#westChina-visual-monitor.jar 9100


# 端口号
PORTS=(8080 9200 9600 9800 9300 9700 9400 9500 9100)
# 系统模块
MODULES=(gateway auth system ct file tenant gen job monitor)
# 系统模块名称
MODULE_NAMES=(网关服务 认证服务 管理系统服务 阅片服务 文件服务 多租户服务 代码生成服务 日志服务 系统监控服务)
# jar包数组
JARS=(westChina-gateway.jar westChina-auth.jar westChina-modules-system.jar westChina-modules-ct.jar westChina-modules-file.jar westChina-modules-tenant.jar westChina-modules-gen.jar westChina-modules-job.jar westChina-visual-monitor.jar)
# jar包路径
#JAR_PATH='/usr/local/beta'
JAR_PATH='./'
# 日志路径
#LOG_PATH='/usr/local/beta'
LOG_PATH='./logs'
mkdir $LOG_PATH
start() {
  local MODULE=
  local MODULE_NAME=
  local JAR_NAME=
  local command="$1"
  local commandOk=0
  local count=0
  local okCount=0
  local port=0
  for((i=0;i<${#MODULES[@]};i++))
  do
    MODULE=${MODULES[$i]}
    MODULE_NAME=${MODULE_NAMES[$i]}
    JAR_NAME=${JARS[$i]}
    PORT=${PORTS[$i]}
    if [ "$command" == "all" ] || [ "$command" == "$MODULE" ];then
      commandOk=1
      count=0
      PID=`ps -ef |grep $(echo $JAR_NAME | awk -F/ '{print $NF}') | grep -v grep | awk '{print $2}'`
      if [ -n "$PID" ];then
        echo "--------------------------------------------$MODULE-----$MODULE_NAME:已经运行,PID=$PID----------------------------------"
      else
    #   exec nohup java -jar $JAR_PATH/$JAR_NAME >> $LOG_PATH/$MODULE.log &
        echo "nohup java -jar $JAR_PATH/$JAR_NAME >> $LOG_PATH/$MODULE.log &"
        nohup java -jar $JAR_PATH/$JAR_NAME >> $LOG_PATH/$MODULE.log &
        PID=`netstat -apn | grep $PORT | awk '{print $7}' | cut -d/ -f 1`
        while [ -z "$PID" ]
        do
          if (($count == 30));then
            echo "$MODULE---$MODULE_NAME:$(expr $count \* 10)秒内未启动,请检查!"
            break
          fi
          count=$(($count+1))
          echo "$MODULE_NAME启动中.................."
          sleep 10s
          PID=`netstat -apn | grep $PORT | awk '{print $7}' | cut -d/ -f 1`
        done
        okCount=$(($okCount+1))
        echo "---------------------------------------------$MODULE---$MODULE_NAME:已经启动成功,PID=$PID----------------------------------"
      fi
    fi
  done
  if(($commandOk == 0));then
    echo "第二个参数请输入:all|auth|gateway|system|ct|file|tenant|gen|job|monitor"
  else
    echo "........................................................本次共启动:$okCount个服务......................................................."
  fi
}

stop() {
  local MODULE=
  local MODULE_NAME=
  local JAR_NAME=
  local command="$1"
  local commandOk=0
  local okCount=0
  for((i=0;i<${#MODULES[@]};i++))
  do
    MODULE=${MODULES[$i]}
    MODULE_NAME=${MODULE_NAMES[$i]}
    JAR_NAME=${JARS[$i]}
    if [ "$command" = "all" ] || [ "$command" = "$MODULE" ];then
      commandOk=1
      PID=`ps -ef |grep $(echo $JAR_NAME | awk -F/ '{print $NF}') | grep -v grep | awk '{print $2}'`
      if [ -n "$PID" ];then
        echo "-----------------------------------------$MODULE---$MODULE_NAME:准备结束,PID=$PID-----------------------------------------"
        kill -9 $PID
        PID=`ps -ef |grep $(echo $JAR_NAME | awk -F/ '{print $NF}') | grep -v grep | awk '{print $2}'`
        while [ -n "$PID" ]
        do
          sleep 3s
          PID=`ps -ef |grep $(echo $JAR_NAME | awk -F/ '{print $NF}') | grep -v grep | awk '{print $2}'`
        done
        echo "-----------------------------------------$MODULE---$MODULE_NAME:成功结束-----------------------------------------"
        okCount=$(($okCount+1))
      else
        echo "-----------------------------------------$MODULE---$MODULE_NAME:未运行-----------------------------------------"
      fi
    fi
  done
  if (($commandOk == 0));then
    echo "第二个参数请输入:all|auth|gateway|system|ct|file|tenant|gen|job|monitor"
  else
    echo "...................................................................本次共停止:$okCount个服务........................................................"
  fi
}


case "$1" in
  start)
    start "$2"
  ;;
  stop)
    stop "$2"
  ;;
  restart)
    stop "$2"
    sleep 3s
    start "$2"
  ;;
  *)
    echo "第一个参数请输入:start|stop|restart"
    exit 1
  ;;
esac