echo "starting openbox"
openbox --replace 2>/tmp/openbox_stderr.log &

# Wait for openbox to start
timeout=30
while [ $timeout -gt 0 ]; do
    if xdotool search --class "openbox" >/dev/null 2>&1 || pgrep -x openbox >/dev/null 2>&1; then
        break
    fi
    sleep 1
    ((timeout--))
done

if [ $timeout -eq 0 ]; then
    echo "openbox stderr output:" >&2
    cat /tmp/openbox_stderr.log >&2
    exit 1
fi

rm /tmp/openbox_stderr.log
