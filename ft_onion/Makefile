IMAGE := ft-onion
CONTAINER := ft-onion

GREEN = \033[0;32m
RESET = \033[0m

.PHONY: all build run stop logs address clean fclean

all: build

build:
	docker build -t $(IMAGE) .

run: build
	-docker rm -f $(CONTAINER) >/dev/null 2>&1
	docker run -d --name $(CONTAINER) $(IMAGE)
	@echo "\nStatus: $(GREEN)ft_onion container created successfully.$(RESET)\n"

	@i=0; while [ $$i -lt 30 ] && ! docker exec $(CONTAINER) test -s /var/lib/tor/ft_onion/hostname; do i=$$((i + 1)); sleep 1; done; \
	if address=$$(docker exec $(CONTAINER) cat /var/lib/tor/ft_onion/hostname 2>/dev/null); then \
		echo "Website: $(GREEN)http://$$address$(RESET)\n"; \
	else \
		echo "Tor has not generated the onion address yet. Run 'make address' later."; \
	fi

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
