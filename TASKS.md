# ROS 2 Refresher — Practice Tasks

## Goal

You're rebuilding fluency with ROS 2 project structure and the day-to-day
mechanics of `rclpy` / `rclcpp` after roughly a year away from it, ahead of a
live coding/problem-solving session. By the end of these modules you will have
built, from scratch, a small multi-package ROS 2 workspace containing:

- Python **and** C++ packages that talk to each other over topics, services,
  and actions
- A custom interface package (your own `.msg` / `.srv` / `.action` types)
- Launch files that wire parameters and multiple nodes together
- A small capstone that drives two `turtlesim` turtles around using
  everything above

No physical robot or heavy simulator is used — `turtlesim` is the only
"simulation," and only where it makes the exercise more concrete and fun.
Everything else is verifiable purely from the CLI (`ros2 topic echo`,
`ros2 node list`, log output, etc.), so a GUI window is never required to
finish a task.

**Distro / environment:** ROS 2 Jazzy Jalisco, running inside the provided
Docker container. See the project `README.md` for how to build and enter it.

**Estimated total time:** ~12–15 hours across Modules 0–6 and 8. Module 7
(automated tests) is a clearly-marked stretch module — treat it as a bonus if
you have time left, not a checkpoint you need to hit.

**How to use `SOLUTIONS.md`:** genuinely attempt each task first. `ros2 --help`,
`ros2 <verb> --help`, and `ros2 pkg create --help` will answer most "what's the
flag again?" questions faster than the solutions file will. Use the solutions
to unblock yourself or to check your approach afterward, not as the first
move.

---

## Workspace layout you're building toward

```
ros2_ws/src/
├── practice_interfaces/   # custom msg / srv / action definitions (ament_cmake)
├── practice_py/           # Python nodes (ament_python)
├── practice_cpp/          # C++ nodes (ament_cmake)
└── practice_bringup/      # launch files + params (ament_cmake)
```

You will create each of these packages yourself with `ros2 pkg create` as you
reach the relevant module — none of them are pre-generated for you. Only the
Docker setup and the empty `ros2_ws/src/` directory are provided.

---

## Module 0 — Environment & CLI warm-up (~30–45 min)

**0.1 — Sanity-check the container**
- [ ] Build the image and start the container (see `README.md`).
- [ ] Inside the container, confirm ROS 2 is sourced: `printenv ROS_DISTRO`
      should print `jazzy`.
- [ ] Run `ros2 doctor --report` and skim the output for anything alarming.
- [ ] Run `ros2 pkg list | grep turtlesim` to confirm turtlesim is installed.

**0.2 — Create the colcon workspace**
- [ ] Confirm `ros2_ws/src/` exists (it's already mounted into the
      container).
- [ ] From `ros2_ws/`, run `colcon build`. It should succeed even with an
      empty `src/` (colcon just builds nothing).
- [ ] `source install/setup.bash` and confirm no errors.

**0.3 — CLI muscle memory with turtlesim**
- [ ] Launch `ros2 run turtlesim turtlesim_node`.
- [ ] In another shell in the same container (`docker compose exec
      ros2_practice bash`), run:
  - `ros2 node list`, `ros2 node info /turtlesim`
  - `ros2 topic list`, `ros2 topic info /turtle1/cmd_vel`, `ros2 topic echo
    /turtle1/pose`
  - `ros2 topic pub -r 5 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear:
    {x: 2.0}, angular: {z: 1.8}}"` — watch it spiral (or check via `pose`
    echo if you have no display).
  - `ros2 service list` and `ros2 service call /clear std_srvs/srv/Empty`

This module is purely about re-loading the CLI verbs into muscle memory. If
none of this feels rusty, you can move fast.

---

## Module 1 — Python package basics (~1.5–2 h)

Create an `ament_python` package: `ros2 pkg create --build-type ament_python
practice_py --dependencies rclpy std_msgs`.

**1.1 — Talker node**
- [ ] Write `practice_py/practice_py/talker.py`: a node named `talker` that
      publishes `std_msgs/msg/String` on topic `chatter`, using a **timer
      callback** (not a blocking loop).
- [ ] Declare a `publish_rate` parameter (double, default `2.0` Hz) that
      controls the timer period.
- [ ] Log each message you publish with `self.get_logger().info(...)`.

**1.2 — Listener node**
- [ ] Write `practice_py/practice_py/listener.py`: a node named `listener`
      that subscribes to `chatter` and logs whatever it receives.

**1.3 — Wire up entry points**
- [ ] Register both nodes as `console_scripts` in `setup.py` (`talker` and
      `listener`).
- [ ] `colcon build --packages-select practice_py`, source, and run both
      nodes in separate shells. Confirm the listener logs what the talker
      sends.

**1.4 — Parameter override**
- [ ] Re-run `talker` with `--ros-args -p publish_rate:=5.0` and confirm
      (via timestamps in the log, or `ros2 topic hz chatter`) that it's
      actually publishing faster.

*Acceptance check:* `ros2 topic hz /chatter` reports a rate close to whatever
`publish_rate` you set.

---

## Module 2 — C++ package basics (~2–2.5 h)

Create an `ament_cmake` package: `ros2 pkg create --build-type ament_cmake
practice_cpp --dependencies rclcpp std_msgs`.

**2.1 — Talker node (C++)**
- [ ] Write `practice_cpp/src/talker.cpp`: a `rclcpp::Node` subclass named
      `talker` publishing `std_msgs::msg::String` on `chatter` via a wall
      timer. Same `publish_rate` parameter idea as Module 1.

**2.2 — Listener node (C++)**
- [ ] Write `practice_cpp/src/listener.cpp`: subscribes to `chatter`, logs
      via `RCLCPP_INFO`.

**2.3 — CMakeLists.txt**
- [ ] Add both as `add_executable(...)` targets.
- [ ] Add `ament_target_dependencies(...)` for `rclcpp` and `std_msgs`.
- [ ] Add an `install(TARGETS ... DESTINATION lib/${PROJECT_NAME})` block —
      this is the step people most often forget, and without it `ros2 run`
      won't find your executable.

**2.4 — Build & verify**
- [ ] `colcon build --packages-select practice_cpp`, source, run both.
- [ ] Cross-check: run the **Python** `listener` from Module 1 against the
      **C++** `talker` (both use the same `chatter` topic / `String` type),
      to confirm ROS 2 doesn't care which language published what.

*Acceptance check:* the same `ros2 topic hz`/`echo` checks as Module 1, but
against the C++ nodes, plus one cross-language pairing working.

---

## Module 3 — Custom interfaces (~1.5–2 h)

Create an interface-only package: `ros2 pkg create --build-type ament_cmake
practice_interfaces`.

You'll define three interfaces used by later modules:

**3.1 — `msg/RobotStatus.msg`**
A status message with at least: a `std_msgs/Header header`, a `string
robot_name`, a `float32 battery_percent`, a `string status`, and `float32 x`,
`y`, `theta` fields.
- [ ] Write the `.msg` file.

**3.2 — `srv/SetSpeed.srv`**
Request: a single `float32 speed`. Response: `bool success` and `string
message`.
- [ ] Write the `.srv` file.

**3.3 — `action/Patrol.action`**
Goal: `int32 laps`. Result: `float32 total_distance`, `float32 elapsed_time`.
Feedback: `int32 current_lap`, `float32 distance_so_far`.
- [ ] Write the `.action` file, remembering the three `---`-separated
      sections (goal / result / feedback).

**3.4 — Build configuration**
- [ ] Edit `CMakeLists.txt`: find `rosidl_default_generators`, call
      `rosidl_generate_interfaces()` listing all three files, and declare
      `DEPENDENCIES std_msgs` (needed for `Header`).
- [ ] Edit `package.xml`: add a `build_depend` on
      `rosidl_default_generators`, an `exec_depend` on
      `rosidl_default_runtime`, a `depend` on `std_msgs`, and the
      `<member_of_group>rosidl_interface_packages</member_of_group>` tag.

**3.5 — Verify**
- [ ] `colcon build --packages-select practice_interfaces`
- [ ] `ros2 interface show practice_interfaces/msg/RobotStatus`
- [ ] `ros2 interface show practice_interfaces/srv/SetSpeed`
- [ ] `ros2 interface show practice_interfaces/action/Patrol`

*Acceptance check:* all three `ros2 interface show` commands print the fields
you defined, with no build errors.

---

## Module 4 — Services across languages (~1.5 h)

Use `SetSpeed` from Module 3. This time, deliberately cross languages: server
in Python, client in C++.

**4.1 — Python service server**
- [ ] `practice_py/practice_py/speed_service_server.py`: a node that offers
      `set_speed` (type `practice_interfaces/srv/SetSpeed`), rejects negative
      speeds (`success=False`), otherwise stores the value and returns
      `success=True` with a confirmation message.
- [ ] Add `practice_interfaces` as a dependency in `practice_py`'s
      `package.xml`, register the new entry point in `setup.py`.

**4.2 — C++ service client**
- [ ] `practice_cpp/src/speed_service_client.cpp`: takes a speed as a
      command-line argument, calls `set_speed` **asynchronously**, waits on
      the future with `rclcpp::spin_until_future_complete`, and logs the
      response.
- [ ] Add `practice_interfaces` to `practice_cpp`'s `CMakeLists.txt` /
      `package.xml`, add the new executable + install rule.

**4.3 — Verify**
- [ ] Run the Python server, then call it a few times from the C++ client
      with different speeds (including a negative one, to see the rejection
      path).

*Acceptance check:* the C++ client prints `success: true` for valid speeds
and `success: false` with your rejection message for a negative one.

---

## Module 5 — Actions + turtlesim (~2–2.5 h)

This is the first module where the turtle actually moves. Build a `Patrol`
action server that drives `turtle1` around a small square, `laps` times.

**Design notes before you start:** `turtlesim` integrates whatever
`geometry_msgs/msg/Twist` you publish directly (no physics engine), so
driving for a fixed **duration** at a fixed linear/angular speed is a
reliable way to trace a square — no need to do closed-loop control against
`pose` for this exercise. Use `/turtle1/pose` only to *measure* distance
traveled for feedback/result reporting, not to steer.

**5.1 — Action server (Python)**
- [ ] `practice_py/practice_py/patrol_action_server.py`. A `Patrol` action
      server node that:
  - declares a `turtle_name` parameter (default `turtle1`) and builds its
    topic/action names from it — this will matter in Module 8, when you'll
    run two of these at once for two different turtles
  - publishes `Twist` on `/<turtle_name>/cmd_vel`
  - subscribes to `/<turtle_name>/pose` purely to accumulate distance
    traveled (sum of the Euclidean distance between consecutive poses)
  - for each of the `laps` requested: drives forward for a fixed duration,
    turns ~90°, four times per lap; publishes feedback after each completed
    lap (`current_lap`, `distance_so_far`)
  - handles cancellation requests (stop the turtle, return a canceled
    result)
  - returns a final result with total distance and elapsed time

  You'll need a `ReentrantCallbackGroup` + `MultiThreadedExecutor` so the
  pose subscription keeps being serviced while `execute_callback` is
  mid-flight (which will be sleeping/blocking in a loop while driving).

**5.2 — Action client (C++)**
- [ ] `practice_cpp/src/patrol_action_client.cpp`: sends a `Patrol` goal
      (laps from argv, action name from argv so you can point it at
      different turtles later), prints feedback as it streams in, prints
      the final result, then shuts down.

**5.3 — Run it**
- [ ] Launch `turtlesim_node`, the action server, and the action client (3
      shells, or jump ahead and write the launch file from Module 6 first —
      your call).
- [ ] Try canceling a goal mid-patrol (`ros2 action list`, then send a
      cancel — either via a second small script, or `Ctrl+C` on the client
      and checking the server logged a cancellation).

*Acceptance check:* the client prints increasing `current_lap` feedback,
then a final result; canceling stops the turtle instead of leaving it
spinning.

---

## Module 6 — Launch files & parameters (~1–1.5 h)

Create `practice_bringup`: `ros2 pkg create --build-type ament_cmake
practice_bringup`. Remember to `install(DIRECTORY launch DESTINATION
share/${PROJECT_NAME})` in its `CMakeLists.txt`.

**6.1 — Talker/listener launch file**
- [ ] `practice_bringup/launch/talker_listener.launch.py`: launches the
      Python `talker` and C++ `listener` together, exposing `publish_rate`
      as a **launch argument** (`DeclareLaunchArgument`) that gets passed
      through to the talker's `publish_rate` parameter.
- [ ] Run it with `ros2 launch practice_bringup talker_listener.launch.py
      publish_rate:=10.0` and confirm the rate actually changed.

**6.2 — Patrol demo launch file**
- [ ] `practice_bringup/launch/patrol_demo.launch.py`: launches
      `turtlesim_node`, the `patrol_action_server`, and the
      `patrol_action_client`, with `laps` as a launch argument.

*Acceptance check:* one `ros2 launch` command brings up the full single-turtle
patrol demo with a configurable lap count.

---

## Module 7 — Automated tests (stretch / optional, ~1–1.5 h)

Not required to reach the capstone, but worth doing if you have the time —
being asked "how would you test this" is common in exactly the kind of
session you're prepping for.

**7.1 — Python unit test**
- [ ] Pull the "how many seconds to drive forward/turn for a given side
      length and speed" arithmetic out of `patrol_action_server.py` into a
      small standalone function, and write a `pytest` test for it under
      `practice_py/test/`.

**7.2 — C++ unit test**
- [ ] Do the same for one small pure function in `practice_cpp` using
      `ament_add_gtest` in `CMakeLists.txt`.

**7.3 — Lint**
- [ ] `colcon test --packages-select practice_py practice_cpp` and read
      through the results — `ros2 pkg create` already wires up
      `ament_flake8` / `ament_pep257` / `ament_lint_auto` for you.

---

## Module 8 — Capstone: two-turtle patrol (~1.5–2 h)

Open-ended on purpose — this is the closest thing here to an interview-style
"design and build" problem. Requirements, not a prescribed architecture:

- [ ] A **second turtle** (`turtle2`) gets spawned at startup at a distinct
      pose, using turtlesim's `/spawn` service.
- [ ] A **battery monitor** node publishes a `RobotStatus` message per turtle
      (on some reasonable topic naming scheme) every second, with battery
      draining over time, and exposes a service to reset both turtles'
      battery back to 100% (`std_srvs/srv/Trigger` is a reasonable fit — no
      need for a new custom interface here).
- [ ] **Both turtles patrol independently and simultaneously.** This is
      where Module 5's `turtle_name` parameter pays off: you need two
      running instances of your `patrol_action_server`, each bound to a
      different turtle, without them colliding on topic or action names.
      Think about what has to be unique between the two instances (node
      name? action name? both?).
- [ ] A **mission control** node (or reuse/extend your action client) that
      sends a `Patrol` goal to *each* turtle and reports when both are done.
- [ ] One `capstone.launch.py` that brings the whole thing up: turtlesim,
      spawner, battery monitor, both patrol action servers, and mission
      control.

Before you write code, sketch (on paper or in a comment block) which nodes
exist, what topics/services/actions connect them, and what's namespaced or
parameterized to allow two turtles to coexist. That design step is most of
the value of this exercise.

*Acceptance check:* one `ros2 launch` command results in both turtles
patrolling (visibly, if you have a display; via `ros2 topic echo` on both
`pose` topics otherwise), status messages logging decreasing battery for
both, and a reset service call that visibly brings both batteries back to
100.

---

## If you finish early

A few extra ideas, roughly in increasing difficulty, if you want to keep
going beyond the capstone:

- Add a `tf2` broadcaster publishing each turtle's pose as a transform, and
  a static transform for a shared "world" frame.
- Make the patrol shape configurable (square vs. triangle vs. pentagon) via
  a parameter, instead of hard-coding "4 sides, 90°."
- Add a `rclpy` component / `rclcpp_components` version of one of your
  nodes so it can be loaded into a component container instead of running
  as a standalone process.
- Write a `QoS` profile explicitly for the `RobotStatus` publisher (e.g.
  `TRANSIENT_LOCAL` durability) and reason about why the default might or
  might not be appropriate there.
