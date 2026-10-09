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
| `move_control_values()` in `process()` | merges parameter values into each reused request | **disabled** (commented out) |
| Extra launch file | - | `launch/imx219.launch.py` |

Why these two changes: on the test Pi, the node found the camera but never
published an image. The Raspberry Pi IPA worker process aborted with
`A list of V4L2 controls requires a ControlInfoMap`, while the libcamera `cam`
tool streamed fine. Both changes together fixed it; with only the `start()`
change the crash was still there. The cause inside libcamera has not been
identified.

**Limitation:** with `move_control_values()` disabled, camera parameters
(exposure, gain, ...) set at runtime are not applied. Auto-exposure and
auto-white-balance run normally in the IPA. A real fix needs the libcamera
side understood first.

## Raspberry Pi 4 setup (`/boot/firmware/config.txt`)

Under `[all]`:

```
camera_auto_detect=0
dtoverlay=imx219
```

Keep `dtoverlay=vc4-kms-v3d`, then reboot.

## Build

From GitHub (replace `<your-github-user>` with the account that hosts the repo):

```
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/<your-github-user>/camera_rpil_ros.git
cd ~/ros2_ws
source /opt/ros/lyrical/setup.bash
rosdep install -y --from-paths src --ignore-src
colcon build --packages-select camera_rpil_ros --parallel-workers 1 --event-handlers console_direct+
source install/setup.bash
```

The repository root is the package itself, so clone it into `src/` under the
name `camera_rpil_ros`. Do not keep a second copy of the package, or one under a
different folder name, in the same workspace: colcon stops with "Duplicate
package names not supported".

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

Built and run on a Raspberry Pi 4 with a Camera Module v2 (IMX219), Ubuntu 26.04,
ROS 2 Lyrical, `ros-lyrical-libcamera` 0.7.2: the node publishes a live image
(viewed in `rqt_image_view`). The same two changes on a source build of upstream
`camera_ros` gave 30 Hz with working auto-exposure. Other boards, sensors and
libcamera versions are untested. With only the `start()` change the crash was
still present; both changes are needed here.

## Licence and credit

MIT, see `LICENSE`. This is a modified copy of `camera_ros` by Christian Rauch;
his copyright notice is kept. If the issue is fixed upstream, prefer the
upstream package.
