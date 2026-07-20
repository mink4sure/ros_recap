.PHONY: build up shell down clean

build:
	docker compose build

up:
	docker compose up -d

shell:
	docker compose exec ros2_practice bash

down:
	docker compose down

# Wipe colcon build artifacts without touching your source code.
clean:
	rm -rf ros2_ws/build ros2_ws/install ros2_ws/log
