#!/usr/bin/env python3
"""
inject_waypoints.py  --  Criterion 3 helper (Hack My Robot 2026, team "The Phishers")

Publishes one or more waypoints to the mission's /addpose topic
(geometry_msgs/PoseWithCovarianceStamped), the same interface the organizer node
`hack_my_robot.py` collects route points on. After injecting, publish
std_msgs/Empty to /path_ready (run once + save) or /start_journey (loop).

AUTHORIZED USE ONLY: the team's assigned competition robot in the organizers'
arena. Prefer running this from your laptop over Bob's Wi-Fi (network vector =
full points). It prints every pose before sending and does not move the robot by
itself -- movement happens only after you trigger /path_ready or /start_journey.

Usage:
  python3 inject_waypoints.py --wp X Y YAW_DEG [--wp X Y YAW_DEG ...] \
      [--addpose /addpose] [--frame map] [--ready] [--dry-run]

  --ready    also publish std_msgs/Empty to /path_ready after the waypoints
  --dry-run  print what would be sent, publish nothing
"""
import argparse
import math
import sys
import time


def yaw_to_quat(yaw_deg):
    y = math.radians(yaw_deg)
    return (0.0, 0.0, math.sin(y / 2.0), math.cos(y / 2.0))


def main():
    ap = argparse.ArgumentParser(description="Inject Criterion 3 waypoints on /addpose")
    ap.add_argument("--wp", nargs=3, metavar=("X", "Y", "YAW_DEG"), action="append",
                    type=float, required=True, help="waypoint, repeatable")
    ap.add_argument("--addpose", default="/addpose")
    ap.add_argument("--frame", default="map")
    ap.add_argument("--ready", action="store_true",
                    help="publish /path_ready (std_msgs/Empty) after the waypoints")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Will publish the following waypoints to %s (frame=%s):" % (args.addpose, args.frame))
    for i, (x, y, yaw) in enumerate(args.wp, 1):
        qx, qy, qz, qw = yaw_to_quat(yaw)
        print("  %d) x=%.3f y=%.3f yaw=%.1f deg -> q=(%.4f, %.4f, %.4f, %.4f)"
              % (i, x, y, yaw, qx, qy, qz, qw))
    if args.ready:
        print("Then publish std_msgs/Empty to /path_ready (runs route once + saves CSV).")
    if args.dry_run:
        print("[dry-run] nothing published.")
        return

    import rospy
    from geometry_msgs.msg import PoseWithCovarianceStamped
    from std_msgs.msg import Empty

    rospy.init_node("phishers_inject_waypoints", anonymous=True)
    pub = rospy.Publisher(args.addpose, PoseWithCovarianceStamped, queue_size=10)
    ready_pub = rospy.Publisher("/path_ready", Empty, queue_size=1)
    time.sleep(1.0)  # let the connection register

    for (x, y, yaw) in args.wp:
        qx, qy, qz, qw = yaw_to_quat(yaw)
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = args.frame
        msg.header.stamp = rospy.Time.now()
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        msg.pose.pose.orientation.x = qx
        msg.pose.pose.orientation.y = qy
        msg.pose.pose.orientation.z = qz
        msg.pose.pose.orientation.w = qw
        pub.publish(msg)
        rospy.loginfo("sent waypoint x=%.3f y=%.3f yaw=%.1f", x, y, yaw)
        time.sleep(0.5)

    if args.ready:
        time.sleep(0.5)
        ready_pub.publish(Empty())
        rospy.loginfo("published /path_ready")
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
