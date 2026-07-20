# ROS 2 Practice Workspace — Quick Start

Docker-based ROS 2 **Jazzy Jalisco** (LTS, Ubuntu 24.04) workspace for the
exercises in `TASKS.md`. Check your work against `SOLUTIONS.md` once you've
had a real attempt — not before.

## 1. Build the image

```
docker compose build
```

## 2. Let the container use your display (needed for turtlesim)

Linux:
```
xhost +local:docker
```

macOS / Windows: see "GUI notes" below.

## 3. Start the container and open a shell

```
docker compose up -d
docker compose exec ros2_practice bash
```

You land in `/root/ros2_ws` with ROS 2 already sourced (see `~/.bashrc` in the
container). `ros2_ws/` is bind-mounted from this folder, so anything you build
persists across `docker compose down` / restarts, and you can edit files with
your normal host editor if you prefer.

## 4. Build your workspace

Once you've created packages under `ros2_ws/src/` (that's Task 0.2):

```
colcon build --symlink-install
source install/setup.bash
```

## 5. Stop the container

```
docker compose down
```

## GUI notes (turtlesim)

- **Linux**: run `xhost +local:docker` before `docker compose up`. Revoke
  afterwards with `xhost -local:docker`.
- **macOS**: install [XQuartz](https://www.xquartz.org/), enable "Allow
  connections from network clients" in its preferences, run
  `xhost + 127.0.0.1`, and set `DISPLAY=host.docker.internal:0` in
  `docker-compose.yml`. Drop `network_mode: host` (it's Linux-only) and expose
  ports if you need them.
- **Windows**: easiest path is WSL2 with WSLg — GUI apps display natively from
  a WSL2 terminal with no extra setup. Alternatively install VcXsrv and set
  `DISPLAY` to your host IP (`<host-ip>:0.0`).
- **No GUI available?** Every task can be verified from the CLI (`ros2 topic
  echo`, `ros2 node list`, `ros2 action list`, log output, `ros2 topic pub`,
  etc.). A visible turtlesim window is a nice-to-have for these exercises, not
  a requirement for any of them.

## Layout

```
docker/Dockerfile        <- image definition (ROS 2 Jazzy + dev tools)
docker-compose.yml
ros2_ws/src/              <- your packages go here (via `ros2 pkg create`)
TASKS.md                  <- start here
SOLUTIONS.md               <- reference solutions, module by module
```
