#!/bin/bash
# N Number
N=9
# Check connectivity to A,B,C,D,E,F,X
function check {
 M="Machine $1"
 IP=$2
 ping -w 1 -n 3 $IP >/dev/null 2>/dev/null
 if [ "$?" != "0" ]; then
	echo "$M Ping failed"
 else
  ssh root@$IP hostname >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "$M SSH failed"
  else
    echo "$M SSH ok"
  fi
 fi
}
# Check connectivity from A to E
function froma {
 M="Machine $1" 
 IP=$2
 ssh root@100.64.0.$N ping -W 1 -c 3 -i 0.1 $IP  >/dev/null 2>/dev/null
 # shellcheck disable=SC2181
 if [ "$?" != "0" ]; then
	echo "$M Ping failed"
 else
  ssh root@100.64.0.$N nmap -sS -p 22 10.21.32.2 | grep open > /dev/null
  if [ "$?" != "0" ]; then
    echo "$M SSH failed"
  else
    echo "$M SSH ok"
  fi
 fi
}
# Check connectivity
check A 100.64.0.$N
check B 100.64.$N.2
check C 100.64.$N.3
check D 100.64.$N.4
froma E 10.21.32.2
check F 100.64.$N.6
check X 100.64.$N.7
# Check DNS on B
NS=`dig +time=1 +tries=1 @100.64.$N.2 www.dundermifflin.com | grep ^www.dundermifflin.com | grep CNAME | wc -l`
if [ "$NS" == "1" ]; then
 echo "Machine B DNS Okay"
else
 echo "Machine B DNS Failed"
fi
# Check Apache on c
NS=`curl --silent --connect-timeout 1 --resolv www.dundermifflin.com:80:100.64.$N.3 http://www.dundermifflin.com/index.html | grep scranton | wc -l`
if [ "$WC" == "18" ]; then
 echo "Machine C WEB OK"
else
 echo "Machine B WEB Failed"
fi