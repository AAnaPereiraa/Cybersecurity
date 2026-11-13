FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install --no-install-recommends -y nginx openssh-server tor sudo\
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd /var/www/html /var/lib/tor/ft_onion \
    && chown -R debian-tor:debian-tor /var/lib/tor/ft_onion \
    && usermod --shell /bin/sh debian-tor \
    && usermod -aG sudo debian-tor

COPY index.html /var/www/html/index.html
COPY nginx.conf /etc/nginx/nginx.conf
COPY sshd_config /etc/ssh/sshd_config
COPY torrc /etc/tor/torrc
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod 755 /usr/local/bin/docker-entrypoint.sh \
    && chmod 600 /etc/ssh/sshd_config \
    && chmod 644 /etc/tor/torrc /etc/nginx/nginx.conf /var/www/html/index.html \
    && chmod 700 /var/lib/tor/ft_onion

EXPOSE 80 4242

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
