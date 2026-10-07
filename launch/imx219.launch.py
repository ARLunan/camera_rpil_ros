"""Launch camera_rpil_ros for a Raspberry Pi Camera Module v2 (IMX219).

Run from a workspace that contains the camera_rpil_ros package:

    source /opt/ros/lyrical/setup.bash
    source <your_workspace>/install/setup.bash
    ros2 launch camera_rpil_ros imx219.launch.py

Override any setting on the command line, for example:

    ros2 launch camera_rpil_ros imx219.launch.py width:=1280 height:=720 jpeg_quality:=80
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    arguments = [
        DeclareLaunchArgument(
            "camera_name",
            default_value="camera",
            description="Node name; topics appear under /<camera_name>/",
        ),
        DeclareLaunchArgument(
            "width", default_value="640", description="Image width in pixels"
        ),
        DeclareLaunchArgument(
            "height", default_value="480", description="Image height in pixels"
        ),
        DeclareLaunchArgument(
            "format",
            default_value="BGR888",
            description="Pixel format (BGR888, RGB888, XRGB8888, YUYV, ...)",
        ),
        DeclareLaunchArgument(
            "frame_id",
            default_value="camera",
            description="frame_id written into message headers",
        ),
        DeclareLaunchArgument(
            "jpeg_quality",
            default_value="95",
            description="JPEG quality (1-100) for /image_raw/compressed",
        ),
        DeclareLaunchArgument(
            "camera_info_url",
            default_value="",
            description="file:// URL of a calibration YAML (empty = default location)",
        ),
    ]

    camera_node = Node(
        package="camera_rpil_ros",
        executable="camera_node",
        name=LaunchConfiguration("camera_name"),
        output="screen",
        parameters=[
            {
                "width": ParameterValue(LaunchConfiguration("width"), value_type=int),
                "height": ParameterValue(LaunchConfiguration("height"), value_type=int),
                "format": ParameterValue(LaunchConfiguration("format"), value_type=str),
                "frame_id": ParameterValue(
                    LaunchConfiguration("frame_id"), value_type=str
                ),
                "jpeg_quality": ParameterValue(
                    LaunchConfiguration("jpeg_quality"), value_type=int
                ),
                "camera_info_url": ParameterValue(
                    LaunchConfiguration("camera_info_url"), value_type=str
                ),
            }
        ],
    )

    return LaunchDescription(arguments + [camera_node])
