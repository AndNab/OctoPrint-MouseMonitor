# coding=utf-8
from __future__ import absolute_import
from flask import jsonify

from threading import Timer, Thread, Lock
import math
import struct

import octoprint.plugin
from octoprint.events import Events
from time import sleep


class MouseMonitorPlugin(octoprint.plugin.StartupPlugin,
                             octoprint.plugin.EventHandlerPlugin,
                             octoprint.plugin.TemplatePlugin,
                             octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self._is_print_running = False
        self._is_filament_active = False
        self._prev_x = 200
        self._prev_y = 200
        self._accumulated_distance = 0
        self._distance_lock = Lock()

        self._mouse_file = None

    def __del__(self):
        if self._mouse_file is not None:
            self._mouse_file.close()

    @property
    def monitoring_interval_sec(self):
        return int(self._settings.get(["monitoring_interval_sec"]))

    @property
    def initial_delay_sec(self):
        return int(self._settings.get(["initial_delay_sec"]))

    @property
    def min_distance_pixel(self):
        return int(self._settings.get(["min_distance_pixel"]))

    @property
    def no_movement_gcode(self):
        return str(self._settings.get(["no_movement_gcode"])).splitlines()

    @property
    def pause_print(self):
        return self._settings.get_boolean(["pause_print"])

    @staticmethod
    def calculate_distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                                 
    def start_filament_checker(self):
        # Reset the accumulated distance when starting a print
        with self._distance_lock:
            self._accumulated_distance = 0

        self._mouse_controller.position = (self._prev_x, self._prev_y)
        self._is_print_running = True

                                 
    def on_after_startup(self):
        self._logger.info("Spool Sensor started")
        self.start_tracking()
        self.start_timer()

                                 
    def get_settings_defaults(self):
        return({
            'monitoring_interval_sec':10,       # Spool movement is checked every N seconds
            'initial_delay_sec':30,             # When starting a print the movement is checked after an initial delay of N seconds
            'min_distance_pixel':2,             # Number of pixels within a check interval to consider a valid spool movement.
            'no_movement_gcode':'',             # gcode to be excecuted 
            'pause_print':True,
        })

                                 
    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self._setup_sensor()

                                 
    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

                                 
    def on_event(self, event, _):
        # Enable sensor
        if event in (
            Events.PRINT_STARTED,
            Events.PRINT_RESUMED
        ):
            self._logger.info("%s: Enabling MouseMonitor sensor..." % (event))
            t = Timer(self.initial_delay_sec, self.start_filament_checker)
            t.start()
        
        # Disable sensor
        elif event in (
            Events.PRINT_DONE,
            Events.PRINT_FAILED,
            Events.PRINT_CANCELLED,
            Events.PRINT_PAUSED,
            Events.ERROR
        ):
            self._logger.info("%s: Disabling spool sensor..." % (event))
            self._logger.info("Mouse events disabled")
            self._is_print_running = False

                                 
    @octoprint.plugin.BlueprintPlugin.route("/status", methods=["GET"])
    def check_status(self):
        status = "-1"
        # Probably want to change this
        return jsonify( status = status )


    def start_mouse_movement_listener(self):
        event = self._mouse_file.read(3)
        while event:
            mx, my = struct.unpack( "bb", event[1:] )

            current_mouse_distance = SpoolSensorPlugin.calculate_distance(mx, my, 0, 0)
            with self._distance_lock:
                self._accumulated_distance += current_mouse_distance
            event = self._mouse_file.read(3)

                                 
    def on_exit(self):
        print("Exit filament activity detection.")

                                 
    def check_if_filament_is_inactive(self):
        while True:
            accumulated_dist = 0
            with self._distance_lock:
                accumulated_dist = self._accumulated_distance
                self._accumulated_distance = 0

            if accumulated_dist >= self.min_distance_pixel:
                self._is_filament_active = True
            else:
                self._is_filament_active = False
            self._logger.debug("Spool sensor movement: %d" % accumulated_dist)

            if self._is_print_running is True:
                if self._is_filament_active is True:
                    self._logger.info("Filament activity detected!")
                else:
                    self._logger.info("No spool movement detected!")
                    if self.pause_print:
                        self._logger.info("Pausing print...")
                        self._printer.pause_print()
                    if self.no_movement_gcode:
                        self._logger.info("Sending no movement GCODE...")
                        self._printer.commands(self.no_movement_gcode)
            sleep(self.monitoring_interval_sec)

                                 
    def start_timer(self):
        timer_thread = Thread(target=self.check_if_filament_is_inactive)
        timer_thread.start()

                                 
    def start_tracking(self):
        infile_path = "/dev/input/mice"
        #open file in binary mode
        self._mouse_file = open(infile_path, "rb")
        thread = Thread(target=self.start_mouse_movement_listener)
        thread.start()

                                 
    def calc_distance(self, pE):
        deltaDistance = float(pE)
        self._logger.debug( f"Relative Extrusion = { round(deltaDistance,3) }" )

                                 
    def distance_detection(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if(gcode == "G0" or gcode == "G1" or gcode == "G2" or gcode == "G3"):
            commands = cmd.split(" ")

            for command in commands:
                if command.startswith("E"):
                    extruder = command[1:]
                    self.calc_distance(float(extruder))
                    # self._logger.debug("E: " + extruder)
        return cmd


__plugin_name__ = "MouseMonitor"
__plugin_version__ = "1.0.4"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = MouseMonitorPlugin()


def __plugin_load__():
    global __plugin_hooks__
    __plugin_hooks__ = {
      "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.distance_detection
}
