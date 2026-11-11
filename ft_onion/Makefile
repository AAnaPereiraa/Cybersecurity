IMAGE := ft-onion
CONTAINER := ft-onion

.PHONY: all build run stop logs address clean fclean

all: build

build:
	docker build -t $(IMAGE) .

run: build
	-docker rm -f $(CONTAINER) >/dev/null 2>&1
	docker run -d --name $(CONTAINER) -p 80:80 -p 4242:4242 $(IMAGE)
	@echo "ft_onion container created successfully."
	@i=0; while [ $$i -lt 30 ] && ! docker exec $(CONTAINER) test -s /var/lib/tor/ft_onion/hostname; do i=$$((i + 1)); sleep 1; done; \
	if address=$$(docker exec $(CONTAINER) cat /var/lib/tor/ft_onion/hostname 2>/dev/null); then \
		echo "Onion address: $$address"; \
		echo "Website: http://$$address"; \
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

fclean: clean
	-docker rmi -f $(IMAGE) >/dev/null 2>&1
	@echo "ft_onion project cleaned successfully."
