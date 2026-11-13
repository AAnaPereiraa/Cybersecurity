#!/bin/sh
set -eu

ssh-keygen -A
mkdir -p /run/sshd

if [ -r /run/ft_onion_authorized_key ]; then
    install -d -m 700 -o debian-tor -g debian-tor /var/lib/tor/.ssh
    install -m 600 -o debian-tor -g debian-tor \
        /run/ft_onion_authorized_key /var/lib/tor/.ssh/authorized_keys
fi

nginx -t
/usr/sbin/sshd -t
su -s /bin/sh debian-tor -c "tor --verify-config -f /etc/tor/torrc"

/usr/sbin/sshd -D &
sshd_pid=$!
nginx -g "daemon off;" &
nginx_pid=$!

cleanup() {
    kill "$sshd_pid" "$nginx_pid" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

exec su -s /bin/sh debian-tor -c "exec tor -f /etc/tor/torrc"
