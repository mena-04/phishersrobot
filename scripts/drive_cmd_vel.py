#!/usr/bin/env python3
"""
drive_cmd_vel.py  --  Criterion 3.3 helper (direct velocity override).

Publishes geometry_msgs/Twist on /cmd_vel to move the robot open-loop, bypassing
move_base obstacle avoidance. This is how you intentionally drive into the
excavator object (25 cm, visible to LiDAR) when the planner would otherwise avoid
it. Network vector (full points); no physical access required.

SAFETY: open-loop, NO obstacle avoidance. Clear all people/hands/feet from the
arena. Use short bursts and low speeds. Always have a stop ready:
    python3 drive_cmd_vel.py --stop
and the hard kill: rostopic pub -1 /motor_power std_msgs/Bool "data: false"

Usage:
  python3 drive_cmd_vel.py --linear 0.08 --angular 0.0 --duration 2.0 [--rate 10]
  python3 drive_cmd_vel.py --stop
"""
import argparse
import sys
import time

MAX_LIN = 0.15   # m/s  cap for safety
MAX_ANG = 0.8    # rad/s cap for safety


def main():
    ap = argparse.ArgumentParser(description="Open-loop /cmd_vel driver (Criterion 3.3)")
    ap.add_argument("--linear", type=float, default=0.0, help="m/s forward (+)/back (-)")
    ap.add_argument("--angular", type=float, default=0.0, help="rad/s yaw")
    ap.add_argument("--duration", type=float, default=1.0, help="seconds to publish")
    ap.add_argument("--rate", type=float, default=10.0)
    ap.add_argument("--topic", default="/cmd_vel")
    ap.add_argument("--stop", action="store_true", help="publish a single zero Twist and exit")
    args = ap.parse_args()

    lin = max(-MAX_LIN, min(MAX_LIN, args.linear))
    ang = max(-MAX_ANG, min(MAX_ANG, args.angular))
    if lin != args.linear or ang != args.angular:
        print("NOTE: clamped to safety caps lin<=%.2f ang<=%.2f" % (MAX_LIN, MAX_ANG))

    import rospy
    from geometry_msgs.msg import Twist

    rospy.init_node("phishers_cmd_vel", anonymous=True)
    pub = rospy.Publisher(args.topic, Twist, queue_size=10)
    time.sleep(0.5)

    t = Twist()
    if args.stop:
        pub.publish(t)
        time.sleep(0.2)
        pub.publish(t)
        print("stop sent (zero Twist on %s)" % args.topic)
        return

    t.linear.x = lin
    t.angular.z = ang
    print("driving %s: lin=%.3f ang=%.3f for %.1fs" % (args.topic, lin, ang, args.duration))
    r = rospy.Rate(args.rate)
    end = time.time() + args.duration
    try:
        while time.time() < end and not rospy.is_shutdown():
            pub.publish(t)
            r.sleep()
    finally:
        stop = Twist()
        pub.publish(stop)
        time.sleep(0.2)
        pub.publish(stop)
        print("auto-stop sent.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # best-effort stop on Ctrl+C
        try:
            import rospy
            from geometry_msgs.msg import Twist
            rospy.Publisher("/cmd_vel", Twist, queue_size=1).publish(Twist())
        except Exception:
            pass
        sys.exit(130)
