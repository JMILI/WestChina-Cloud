#!/bin/bash
# 本机部署：用 127.0.0.1 连接 Nacos（无需改 /etc/hosts）
cd "$(dirname "$0")"
export JAVA_HOME="${JAVA_HOME:-$HOME/tools/jdk8}"
export PATH="$JAVA_HOME/bin:$PATH"

JAVA_OPTS="-Xms128m -Xmx384m"
JAVA_OPTS="$JAVA_OPTS -Dspring.cloud.nacos.discovery.server-addr=127.0.0.1:8848"
JAVA_OPTS="$JAVA_OPTS -Dspring.cloud.nacos.config.server-addr=127.0.0.1:8848"
JAVA_OPTS="$JAVA_OPTS -Dspring.cloud.sentinel.transport.dashboard=127.0.0.1:8718"

mkdir -p logs

start_jar() {
  local name="$1"
  local jar="$2"
  local port="$3"
  if pgrep -f "java.*${jar}" >/dev/null 2>&1 && ss -tlnp | grep -q ":${port} "; then
    echo "$name 已在运行 (端口 ${port})"
    return 0
  fi
  pkill -f "java.*${jar}" 2>/dev/null || true
  sleep 1
  echo "启动 $name ..."
  nohup "$JAVA_HOME/bin/java" $JAVA_OPTS -jar "$jar" >> "logs/${name}.log" 2>&1 &
  for _ in $(seq 1 20); do
    ss -tlnp | grep -q ":${port} " && echo "$name 已就绪 (端口 ${port})" && return 0
    sleep 3
  done
  echo "警告: $name 启动超时，请查看 logs/${name}.log"
  return 1
}

case "$1" in
  start)
    case "$2" in
      core|"")
        start_jar gateway westChina-gateway.jar 8080
        start_jar auth westChina-auth.jar 9200
        start_jar system westChina-modules-system.jar 9600
        start_jar tenant westChina-modules-tenant.jar 9700
        ;;
      ct)
        start_jar file westChina-modules-file.jar 9300
        start_jar ct westChina-modules-ct.jar 9800
        ;;
      all)
        start_jar gateway westChina-gateway.jar 8080
        start_jar auth westChina-auth.jar 9200
        start_jar system westChina-modules-system.jar 9600
        start_jar ct westChina-modules-ct.jar 9800
        start_jar file westChina-modules-file.jar 9300
        start_jar tenant westChina-modules-tenant.jar 9700
        # gen 代码生成：租户系统已屏蔽「系统工具」，无需启动
        start_jar job westChina-modules-job.jar 9500
        start_jar monitor westChina-visual-monitor.jar 9100
        ;;
      *)
        echo "未知模式: $2 (core|all)"
        exit 1
        ;;
    esac
    ;;
  stop)
    pkill -f 'westChina-.*\.jar' 2>/dev/null || true
    echo "已停止"
    ;;
  status)
    pgrep -af 'westChina-.*\.jar' || echo "无运行中的服务"
    ;;
  *)
    echo "用法: $0 {start core|start ct|start all|stop|status}"
    exit 1
    ;;
esac
