pid=""

cleanup() {
  kill $(cat pid)
  kill $(cat kpid)
}
trap cleanup EXIT SIGINT

hashit() {
    find . -type f \( -iname "*.py" \) -exec md5sum {} \; | md5sum | awk '{print $1}'
}

h="`hashit`"
while sleep 5; do
    h2="`hashit`"
    if [ "x$h" != "x$h2" ]; then
        # restart python server
        echo "======="
        echo "hash changed, restarting"
        echo "$h"
        echo "$h2"
        echo "======="
        kill `cat pid`
        h="$h2"
    fi
done &
kpid=$!
echo $kpid > kpid

while sleep 1; do
    python3 server.py &
    pid=$!
    echo $pid > pid
    sleep $[60*60*8] && kill `cat pid` && "killed proc" &
    wait $pid
done

time find . -type f \( -iname "*.py" \) -exec md5sum {} \;

#gunicorn --certfile=bodygen_re.crt --keyfile=bodygen_re.key --bind 0.0.0.0:8081 server:app
