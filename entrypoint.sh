# copy config if not exists (this can be mounted)
cp -nr /config_org/* /config

# trying to ssh if remote src
if [[ -z "${REMOTE_SRC_HOST}" ]]; then
    echo "No remote src host is defined, assuming src-host is local"
else
    echo "Remote src host, is ${REMOTE_SRC_HOST}, trying to ssh (must be able to ssh without pass)"
    remote_with_port=$(echo "${REMOTE_SRC_HOST}" | sed "s/:/ -p/")  # from <uname>@<ip>:<port> to <uname>@<ip> -p<port>
    echo "Executing ssh -oBatchMode=yes ${remote_with_port}"
    ssh -oBatchMode=yes ${remote_with_port} || exit 1
fi

echo "------- Starting by running sannity tests -------"
PYTHONPATH=/src/:/config/ pytest -vvr /tests/test_backup_manager/* || exit 1
echo "------- Done running tests -------"

echo "------- removing all old crontabs -------"
crontab -r

echo "------- add our cron script using crontab -------"
crontab /config/backup_manager_crontab

echo "------- listen to crond -------"
crond -f -l 0 -d 0
