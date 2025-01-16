"""
Utility functions
"""

from __future__ import print_function

import sys
from collections import namedtuple
from subprocess import Popen, PIPE

from DeComp import log

BASH_CMD = "/bin/bash"


def _is_available(self, available_binaries: set) -> bool:
    """Private function for the named tuple classes

    :param available_binaries: the confirmed installed binaries
    """
    return self.binaries.issubset(available_binaries)


def create_classes(definitions: dict, fields: list) -> dict:
    """This function dynamically creates the namedtuple classes which are
    used for the information they contain in a consistent manner.

    :param definitions: (de)compressor definitions
        see DEFINITION_FIELDS defined in this library.
    :param fields: list of the field names to create
    :returns: class_map: dictionary of key: namedtuple class instance
    """
    class_map = {}
    for name in list(definitions):
        # create the namedtuple class instance
        obj = namedtuple(name, fields)
        # reduce memory used by limiting it to the predefined fields variables
        obj.__slots__ = ()
        obj.enabled = _is_available
        # now add the instance to our map
        class_map[name] = obj._make(definitions[name])
    del obj
    return class_map


def subcmd(command: str, exc: str = "", env: dict = None, debug: bool | None = False) -> bool:
    """General purpose function to run a command in a subprocess

    :param command: command string to run
    :param exc: command name being run (used for the log)
    :param env: the environment to run the command in
    :param debug: optional default: False
    """
    env = env or {}
    sys.stdout.flush()
    args = [BASH_CMD]
    if debug:
        args.append("-x")
    args.append("-c")
    args.append(command)
    log.debug("subcmd(); args = %s", args)
    try:
        proc = Popen(args, env=env)
    except:
        raise
    if proc.wait() != 0:
        log.debug("subcmd() NON-zero return value from: %s", exc)
        return False
    return True


def check_available(commands: list) -> set[str]:
    """Checks for the available binaries

    :param commands: the binaries to check for their existence
    :returns: set of the installed binaries available
    """
    cmd = ["which"]
    cmd.extend(commands)
    proc = None
    try:
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        results = proc.communicate()
        stdout = results[0].decode('UTF-8')
    except OSError as error:
        stdout = u''
        log.error("utils: check_available(); OSError: %s, %s",
                  str(error), ' '.join(cmd))
    finally:
        if proc:
            for pipe in [proc.stdout, proc.stderr]:
                if pipe:
                    pipe.close()
    available = set([x.rsplit('/', 1)[1] for x in stdout.split('\n') if x])
    return available
