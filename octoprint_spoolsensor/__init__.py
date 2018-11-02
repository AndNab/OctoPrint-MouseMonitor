# coding=utf-8
from __future__ import absolute_import
from flask import jsonify

import octoprint.plugin
from octoprint.events import Events
from time import sleep


class spoolsensorPlugin(octoprint.plugin.StartupPlugin,
                             octoprint.plugin.EventHandlerPlugin,
                             octoprint.plugin.TemplatePlugin,
                             octoprint.plugin.SettingsPlugin):

    def initialize(self):
        #self._logger.info("Running RPi.GPIO version '{0}'".format(GPIO.VERSION))
        #if GPIO.VERSION < "0.6":       # Need at least 0.6 for edge detection
        #    raise Exception("RPi.GPIO must be greater than 0.6")
        #GPIO.setwarnings(False)        # Disable GPIO warnings
        self.spoolsensorPlugin_confirmations_tracking = 0

    @property
    def poll_time(self):
        return int(self._settings.get(["poll_time"]))

    @property
    def confirmations(self):
        return int(self._settings.get(["confirmations"]))

    @property
    def debug_mode(self):
        return int(self._settings.get(["debug_mode"]))

    @property
    def no_movement_gcode(self):
        return str(self._settings.get(["no_movement_gcode"])).splitlines()

    @property
    def pause_print(self):
        return self._settings.get_boolean(["pause_print"])

    def _setup_sensor(self):
        if self.mouse_enabled():
            self._logger.info("Setting up sensor...")
        else:
            self._logger.info("Mouse events not enabled!")

    def on_after_startup(self):
        self._logger.info("Spool Sensor started")
        self._setup_sensor()

    def get_settings_defaults(self):
        return({
            'poll_time':60000,      # Debounce every 60 seconds/60000ms
            'confirmations':2,      # Confirm that we're actually not moving
            'no_movement_gcode':'',
            'debug_mode':0,         # Debug off
            'pause_print':True,
        })
    
    def debug_only_output(self, string):
        if self.debug_mode==1:
            self._logger.info(string)

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self._setup_sensor()

    def mouse_enabled(self):
        #return self.pin != -1
        # Probably want to see if the mouse event can be loaded here
        return True

    def no_movement(self):
        #return GPIO.input(self.pin) != self.switch
        # Here, we need to actually perform some work
        return False

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

    def on_event(self, event, payload):
        # Early abort in case of out ot filament when start printing, as we
        # can't change with a cold nozzle
        if event is Events.PRINT_STARTED and self.no_movement():
            self._logger.info("Printing aborted: no filament detected!")
            self._printer.cancel_print()
        # Enable sensor
        if event in (
            Events.PRINT_STARTED,
            Events.PRINT_RESUMED
        ):
            self._logger.info("%s: Enabling spool sensor..." % (event))
            if self.mouse_enabled():
                #GPIO.remove_event_detect(self.pin)
                #GPIO.add_event_detect(
                #    self.pin, GPIO.BOTH,
                #    callback=self.sensor_callback,
                #    bouncetime=self.poll_time
                #)
                self._logger.info("Mouse events enabled")
        # Disable sensor
        elif event in (
            Events.PRINT_DONE,
            Events.PRINT_FAILED,
            Events.PRINT_CANCELLED,
            Events.ERROR
        ):
            self._logger.info("%s: Disabling spool sensor..." % (event))
            #GPIO.remove_event_detect(self.pin)
            self._logger.info("Mouse events disabled"

    @octoprint.plugin.BlueprintPlugin.route("/status", methods=["GET"])
    def check_status(self):
        status = "-1"
        #if self.pin != -1:
        #    status = str(self.no_movement())
        # Probably want to change this
        return jsonify( status = status )

    def sensor_callback(self, _):
        sleep(self.poll_time/1000)
        #self.debug_only_output('Pin: '+str(GPIO.input(self.pin)))
        if self.no_movement():
            self.spoolsensorPlugin_confirmations_tracking+=1
            self.debug_only_output('Confirmations: '+str(self.spoolsensorPlugin_confirmations_tracking))
            if self.confirmations<=self.spoolsensorPlugin_confirmations_tracking:
                self._logger.info("No spool movement detected!")
                if self.pause_print:
                    self._logger.info("Pausing print...")
                    self._printer.pause_print()
                if self.no_movement_gcode:
                    self._logger.info("Sending no movement GCODE...")
                    self._printer.commands(self.no_movement_gcode)
                self.spoolsensorPlugin_confirmations_tracking = 0
        else:
            self.spoolsensorPlugin_confirmations_tracking = 0

    def get_update_information(self):
        return dict(
            octoprint_spoolsensor=dict(
                displayName="Spool Sensor",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="OutsourcedGuru",
                repo="Octoprint-Spool-Sensor",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/OutsourcedGuru/Octoprint-Spool-Sensor/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "Spool Sensor"
__plugin_version__ = "1.0.1"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = spoolsensorPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}
