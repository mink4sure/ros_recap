# ROS 2 Jazzy Jalisco (LTS, supported until 2029) on Ubuntu 24.04.
# "desktop-full" already includes turtlesim, rviz2, rqt, and the demo nodes.
FROM osrf/ros:jazzy-desktop-full AS ros_basic

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# rosdep is already initialized on the base image in most cases; guard against
# re-running `rosdep init` on a rebuild, which would otherwise fail loudly.
RUN if [ ! -d /etc/ros/rosdep/sources.list.d ] || [ -z "$(ls -A /etc/ros/rosdep/sources.list.d 2>/dev/null)" ]; then \
      rosdep init; \
    fi && rosdep update

ENV ROS_WS=/root/ros2_ws
RUN mkdir -p ${ROS_WS}/src
WORKDIR ${ROS_WS}

# Auto-source ROS 2 and the workspace overlay (once built) in every new shell.
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo "if [ -f ${ROS_WS}/install/setup.bash ]; then source ${ROS_WS}/install/setup.bash; fi" >> /root/.bashrc

ENV DEBIAN_FRONTEND=


FROM ros_basic as tooling

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nano \
    vim \
    tmux \
    && rm -rf /var/lib/apt/lists/*

CMD ["bash"]
