IMAGE := ft-onion
CONTAINER := ft-onion
SSH_PUBLIC_KEY ?= $(HOME)/.ssh/id_ed25519.pub

GREEN = \033[0;32m
RESET = \033[0m

.PHONY: all build run ssh stop logs address clean fclean

all: build

build:
	docker build -t $(IMAGE) .

run: build
	-docker rm -f $(CONTAINER) >/dev/null 2>&1
	docker run -d --name $(CONTAINER) $(IMAGE)
	@echo "\nStatus: $(GREEN)ft_onion container created successfully.$(RESET)\n"

	@i=0; while [ $$i -lt 30 ] && ! docker exec $(CONTAINER) test -s /var/lib/tor/ft_onion/hostname; do i=$$((i + 1)); sleep 1; done; \
	address=$$(docker exec $(CONTAINER) cat /var/lib/tor/ft_onion/hostname 2>/dev/null); \
	echo "Website: $(GREEN)http://$$address$(RESET)\n"
ssh:
	@if [ ! -r "$(SSH_PUBLIC_KEY)" ]; then \
		mkdir -p "$$(dirname "$(SSH_PUBLIC_KEY)")"; \
		if [ -r "$(SSH_PUBLIC_KEY:.pub=)" ]; then \
			ssh-keygen -y -f "$(SSH_PUBLIC_KEY:.pub=)" > "$(SSH_PUBLIC_KEY)"; \
			chmod 644 "$(SSH_PUBLIC_KEY)"; \
		else \
			ssh-keygen -q -t ed25519 -N "" -f "$(SSH_PUBLIC_KEY:.pub=)"; \
		fi; \
	fi
	@if ! docker ps --format '{{.Names}}' | grep -qx '$(CONTAINER)'; then \
		echo "Container $(CONTAINER) is not running. Run 'make run' first." >&2; \
		exit 1; \
	fi
	docker exec -i $(CONTAINER) sh -c \
		'mkdir -p /var/lib/tor/.ssh && \
		 chown debian-tor:debian-tor /var/lib/tor/.ssh && \
		 chmod 700 /var/lib/tor/.ssh && \
		 cat > /var/lib/tor/.ssh/authorized_keys && \
		 chown debian-tor:debian-tor /var/lib/tor/.ssh/authorized_keys && \
		 chmod 600 /var/lib/tor/.ssh/authorized_keys' \
		< "$(SSH_PUBLIC_KEY)"
	@address=$$(docker exec $(CONTAINER) cat /var/lib/tor/ft_onion/hostname); \
	echo "\ncommand: $(GREEN)ssh -o 'ProxyCommand=nc -X 5 -x 127.0.0.1:9150 %h %p' -p 4242 debian-tor@$$address"
stop:
	-docker stop $(CONTAINER) >/dev/null 2>&1

logs:
	docker logs -f $(CONTAINER)

address:
	docker exec $(CONTAINER) cat /var/lib/tor/ft_onion/hostname

clean:
	-docker rm -f $(CONTAINER) >/dev/null 2>&1
	@echo "$(GREEN)ft_onion project container removed successfully.$(RESET)"

fclean: clean
	-docker rmi -f $(IMAGE) >/dev/null 2>&1
	@echo "$(GREEN)ft_onion project image removed successfully.$(RESET)"
