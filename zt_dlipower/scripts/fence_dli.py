#!/usr/bin/python
# Copyright (c) 2009-2015, Dwight Hubbard
# Copyrights licensed under the New BSD License
# See the accompanying LICENSE.txt file for terms.
"""
Stonith Agent for Digital Loggers Network Power Switches
for Linux HA Clusters

This agent has been tested against the following Digital Loggers Power
network power switches:
  WebPowerSwitch II
  WebPowerSwitch III
  WebPowerSwitch IV
  WebPowerSwitch V
  Ethernet Power Controller III

It may work for other models of Digital Loggers power switches as well
"""
from __future__ import print_function

import sys

import zt_dlipower

# This fencing driver uses the dlipower python module to manage the power switch
# the dlipower package installs a dlipower.py script that provides a command line
# interface to manage the switch.
RELEASE_VERSION = "0.0.5"

device_opt = [
    "help",
    "version",
    "agent",
    "action",
    "ipaddr",
    "login",
    "passwd",
    "port",
    "nodename",
    "timeout",
    "cycletime",
]


def main():
    # Parse the input into a dict named options
    options = {}
    unknown_options = []
    for line in sys.stdin.readlines():
        temp = line.strip().split("=")
        if len(temp) == 2:
            key = temp[0].strip()
            value = temp[1].strip()
            if line[0] != "#" and len(key):
                if key in device_opt:
                    options[key] = value
                else:
                    unknown_options.append(key)

        # Print a warning about unknown options that where passed
        if unknown_options:
            print(
                "Unknown options, ignoring: ",
                " ".join(unknown_options),
                file=sys.stderr,
            )

    # Make sure we got all the needed options to do the action requested
    if not set(["ipaddr", "login", "passwd", "action"]).issubset(set(options)):
        print(
            "Did not receive all required options, missing",
            " ".join(
                list(
                    set(["ipaddr", "login", "passwd", "action"]).difference(
                        set(options)
                    )
                )
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    if "port" not in options.keys() and options["action"] in [
        "off",
        "on",
        "reboot",
        "status",
    ]:
        print("Cannot execute action, no port specified")
        sys.exit(1)

        # The dlipower powerswitch object uses the default values if options have a value of None
        # so we set these options to the passed value or None if they weren't passed which
        # will cause the dlipower module to use it's internal defaults.
        # The dlipower module will store default settings in the ~/.dlipower.conf file of the
        # user running the command.  For clarity it's a good idea to pass the options when
        # using a cluster.
    if "cycletime" not in options.keys():
        options["cycletime"] = None

    if "timeout" not in options.keys():
        options["timeout"] = None

    switch = zt_dlipower.PowerSwitch(
        hostname=options["ipaddr"],
        userid=options["login"],
        password=options["passwd"],
        timeout=options["timeout"],
        cycletime=options["cycletime"],
    )
    if options["action"].lower() in ["off"]:
        sys.exit(switch.off(int(options["port"])))
    if options["action"].lower() in ["on"]:
        sys.exit(switch.on(int(options["port"])))
    if options["action"].lower() in ["reboot"]:
        sys.exit(switch.cycle(int(options["port"])))
    if options["action"].lower() in ["status"]:
        status = switch.status(int(options["port"]))
        if status == "ON":
            sys.exit(0)
        if status == "Unknown":
            sys.exit(1)
        if status == "OFF":
            sys.exit(2)
    if options["action"].lower() in ["list", "monitor"]:
        sys.exit(switch.printstatus())
