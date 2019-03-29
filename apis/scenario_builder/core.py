import json

from . import openbach_functions


class Scenario:
    """Interface between Python code and JSON scenario definition.

    This class aims at reducing the boilerplate necessary when
    defining configuration files for OpenBach scenarios. Instances
    of this class represents a configuration file for a given
    scenario.
    """

    def __init__(self, name, description=None):
        """Construct an empty scenario with the given metadata"""

        if description is None:
            description = name

        self.name = name
        self.description = description
        self.arguments = {}
        self.constants = {}
        self.openbach_functions = []

    def add_argument(self, name, description):
        """Add an argument for this scenario"""

        self.arguments[name] = description

    def remove_argument(self, name):
        """Remove the given argument from this scenario"""

        try:
            del self.arguments[name]
        except KeyError:
            pass

    def add_constant(self, name, value):
        """Associate a value to a constant for this scenario"""

        self.constants[name] = value

    def remove_constants(self, name):
        """Remove the given constant from this scenario"""

        try:
            del self.contants[name]
        except KeyError:
            pass

    def add_function(self, name, wait_delay=0, wait_launched=None, wait_finished=None, label=None):
        """Add an openbach function to this scenario.

        The function will be started after all other functions in
        `wait_launched` are started and all other functions in
        `wait_finished` are completed. After these conditions are
        met (if any), an additional delay of `wait_delay` will be
        applied before the function starts.
        """

        wait_launched = check_and_build_waiting_list(wait_launched)
        wait_finished = check_and_build_waiting_list(wait_finished)

        factory = get_function_factory(name)
        function = factory(wait_launched, wait_finished, wait_delay, label)
        self.openbach_functions.append(function)
        return function

    def remove_function(self, function):
        """Remove the given function from this scenario.

        The function should be an object returned by
        `self.add_function(...)`.
        """

        try:
            self.openbach_functions.remove(function)
        except ValueError:
            pass

    def build(self):
        """Construct a dictionary representing this scenario.

        This dictionary is suitable to be written in a file as
        JSON data.
        """
        return {
            'name': self.name,
            'description': self.description,
            'arguments': self.arguments.copy(),
            'constants': self.constants.copy(),
            'openbach_functions': [
                f.build(self.openbach_functions, id)
                for id, f in enumerate(self.openbach_functions)
            ],
        }

    def write(self, filename):
        """Write the JSON representation of this scenario in
        the requested file.
        """

        with open(filename, 'w') as fp:
            json.dump(self.build(), fp)

    def __str__(self):
        return self.name

    @property
    def subscenarios(self):
        for function in self.openbach_functions:
            if isinstance(function, openbach_functions.StartScenarioInstance):
                scenario = function.scenario_name
                if isinstance(scenario, Scenario):
                    yield from scenario.subscenarios
                    yield scenario
        yield self


def check_and_build_waiting_list(wait_on=None):
    """Check that each element container in the `wait_on` iterable
    is a proper openbach function. Raise `TypeError` otherwise.

    Return the `wait_on` iterable converted to a list.
    """

    wait_on = [] if wait_on is None else list(wait_on)
    if not all(isinstance(obj, openbach_functions.OpenBachFunction) for obj in wait_on):
        raise TypeError('can only wait on iterables of openbach functions')
    return wait_on


def get_function_factory(name):
    """Convert a name to the appropriate openbach function"""

    n = ''.join(name.title().split('_'))
    try:
        cls = getattr(openbach_functions, n)
    except AttributeError:
        cls = getattr(openbach_functions, name)
    assert issubclass(cls, openbach_functions.OpenBachFunction)
    return cls