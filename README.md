# camera_rpil_ros

ROS 2 camera node for libcamera-supported cameras, tested with a Raspberry Pi 4
and a Raspberry Pi Camera Module v2 (IMX219) on Ubuntu 26.04 with ROS 2 Lyrical
and `ros-lyrical-libcamera` 0.7.2.

This package is derived from
[camera_ros](https://github.com/christianrauch/camera_ros) 0.7.0 by Christian
Rauch (upstream commit `8f792e27a6dbc81e4943a75765fc1b7b7d37b301`, MIT licence,
see `LICENSE`). Topics, parameters and the node itself are the same.

## Differences from camera_ros

| Item | camera_ros | camera_rpil_ros |
| --- | --- | --- |
| Package name | `camera_ros` | `camera_rpil_ros` |
| Library target | `camera_component` | `camera_rpil_component` |
| `Camera::start()` in `src/CameraNode.cpp` | passes the initial control list | called without a control list |
| Extra launch file | - | `launch/imx219.launch.py` |

Why the `start()` change: on the test Pi, the node found the camera but never
published an image. The Raspberry Pi IPA worker process aborted right after
capture started with `A list of V4L2 controls requires a ControlInfoMap`, while
the libcamera `cam` tool streamed fine. Calling `start()` without the initial
control list fixed it. The cause inside libcamera has not been identified.
Parameter values are still applied: `process()` merges them into the reused
requests.

## Raspberry Pi 4 setup (`/boot/firmware/config.txt`)

Under `[all]`:

```
camera_auto_detect=0
dtoverlay=imx219
```

Keep `dtoverlay=vc4-kms-v3d`, then reboot.

## Build

```
mkdir -p ~/ros2_ws/src
cp -r camera_rpil_ros ~/ros2_ws/src/        # or untar it there
cd ~/ros2_ws
source /opt/ros/lyrical/setup.bash
rosdep install -y --from-paths src --ignore-src
colcon build --packages-select camera_rpil_ros --parallel-workers 1 --event-handlers console_direct+
source install/setup.bash
```

`--parallel-workers 1` keeps memory use low on a Pi 4. If rosdep tries to
install a libcamera you do not want, add `--skip-keys=libcamera` (the package
then needs a libcamera that `pkg-config` can find).

## Run

```
ros2 run camera_rpil_ros camera_node --ros-args -p width:=640 -p height:=480 -p format:=BGR888
ros2 launch camera_rpil_ros imx219.launch.py
ros2 launch camera_rpil_ros camera.launch.py      # composable node + image_view
```

Check it:

```
ros2 topic hz /camera/image_raw
ros2 run rqt_image_view rqt_image_view
```

Only one process can own the camera at a time. Stop any other `camera_node`
(`pkill -f camera_node`) before starting a new one.

## Status

Verified on the test Pi: a build of upstream `camera_ros` with the same one-line
change published 30 Hz images. This renamed package itself has not been built
yet, so a first `colcon build` is the real check.
