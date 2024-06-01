from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, main, DataActuatorType, \
    DataActuator  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand  # object used to send info back to the main thread
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_redpitaya.utils import Config
from pymodaq_plugins_redpitaya.hardware.redpitaya_scpi import scpi as RedPitayaScpi


class DAQ_Move_RedPitayaRFGenerator(DAQ_Move_base):
    """ Instrument plugin class for an actuator.

    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of controllers and actuators that should be compatible with this instrument plugin.
        * With which instrument and controller it has been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    # TODO add your particular attributes here if any

    """
    plugin_config = Config()
    _controller_units = 'Hz'
    is_multiaxes = False
    _axis_names = ['Frequency']
    _epsilon = 0.1
    data_actuator_type = DataActuatorType['DataActuator']

    params = [
                 {'title': 'IP Address:', 'name': 'ip_address', 'type': 'str', 'value': plugin_config('ip_address')},
                 {'title': 'Port:', 'name': 'port', 'type': 'int', 'value': plugin_config('port')},
                 {'title': 'Board name:', 'name': 'bname', 'type': 'str', 'readonly': True},
                 {'title': 'Amplitude:', 'name': 'amplitude (V)', 'type': 'float', 'value': 1},
             ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    # _epsilon is the initial default value for the epsilon parameter allowing pymodaq to know if the controller reached
    # the target value. It is the developer responsibility to put here a meaningful value

    def ini_attributes(self):
        self.controller: RedPitayaScpi = None

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = DataActuator(data=float(self.controller.txrx_txt('SOUR1:FREQ:FIX?')))
        pos = self.get_position_with_scaling(pos)
        return pos

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        #  self.controller.your_method_to_terminate_the_communication()  # when writing your own plugin replace this line

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
            self.controller.your_method_to_apply_this_param_change()
        else:
            pass

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.controller = self.ini_stage_init(old_controller=controller,
                                              new_controller=RedPitayaScpi(
                                                  host=self.settings["ip_address"],
                                                  port=5000))

        info = "The connection with the RedPitaya should be established."
        initialized = True
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)  # if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one

        self.controller.sour_set(1,"sine", 1, value.value())
        self.emit_status(ThreadCommand('Update_Status', ['The RF frequency has been modified.']))

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)

        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_set_a_relative_value(
            value.value())  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def move_home(self):
        """Call the reference method of the controller"""

        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_get_to_a_known_reference()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""

        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_stop_positioning()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))


if __name__ == '__main__':
    main(__file__)