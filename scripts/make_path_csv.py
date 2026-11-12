#!/usr/bin/env python3
"""
make_path_csv.py  --  Criterion 3 helper (saved-path overwrite route).

Generates lines in the organizer node's scan_positions.csv format:
    x,y,z,qx,qy,qz,qw
one per waypoint. Use when you have file access to the robot (from Criterion 1/2):
replace saved_path/scan_positions.csv on the robot with your route, then publish
std_msgs/Empty to /start_journey to replay it.

Always back up the original first:
    cp .../saved_path/scan_positions.csv /tmp/scan_positions.bak.csv

Usage:
  python3 make_path_csv.py --wp X Y YAW_DEG [--wp ...] > my_path.csv
"""
import argparse
import math
import sys


def yaw_to_quat(yaw_deg):
    y = math.radians(yaw_deg)
    return (0.0, 0.0, math.sin(y / 2.0), math.cos(y / 2.0))


def main():
    ap = argparse.ArgumentParser(description="Generate scan_positions.csv lines")
    ap.add_argument("--wp", nargs=3, metavar=("X", "Y", "YAW_DEG"), action="append",
                    type=float, required=True, help="waypoint, repeatable")
    args = ap.parse_args()
    for (x, y, yaw) in args.wp:
        qx, qy, qz, qw = yaw_to_quat(yaw)
        sys.stdout.write("%r,%r,%r,%r,%r,%r,%r\n" % (x, y, 0.0, qx, qy, qz, qw))


if __name__ == "__main__":
    main()
