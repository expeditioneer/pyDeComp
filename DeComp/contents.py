"""
contents.py

Utility class to hold and handle all possible contents
listing of compressed files using native linux utilities.

If you have other contents definitions,
please send them along for inclusion in the main repo.

Maintained in full by:
    Brian Dolbec <dolsen@gentoo.org>

"""

from __future__ import print_function

import logging
import os
from subprocess import Popen, PIPE

from DeComp import log
from DeComp.definitions import (CONTENTS_SEARCH_ORDER, DEFINITION_FIELDS,
                                EXTENSION_SEPARATOR, COMPRESSOR_PROGRAM_OPTIONS,
                                DECOMPRESSOR_PROGRAM_OPTIONS,
                                LIST_XATTRS_OPTIONS
                                )
from DeComp.utils import create_classes, check_available


class ContentsMap:
    """Class to encompass all known commands to list
    the contents of an archive"""

    # fields: list of ordered field names for the contents functions
    # use ContentsMap.fields for the value legend
    fields = list(DEFINITION_FIELDS)

    def __init__(self, definitions: dict = None, env: dict = None, default_mode: str = None,
                 separator: str = EXTENSION_SEPARATOR, search_order: list[str] = None,
                 logger: logging.Logger | None = None,
                 comp_prog=COMPRESSOR_PROGRAM_OPTIONS['linux'],
                 decomp_opt=DECOMPRESSOR_PROGRAM_OPTIONS['linux'],
                 list_xattrs_opt=LIST_XATTRS_OPTIONS['linux']):
        """Class init

        :param definitions: dictionary of
            Key:[function, cmd, cmd_args, Print/id string, extensions]
        :param env: environment to pass to the subprocess
        :param default_mode: one of the defintions keys
        :param separator: filename extension separator
        :param search_order: optional mode search order
        :param logger: optional logging module instance,
                       default: pyDecomp logging namespace instance
        """
        if definitions is None:
            definitions = {}
        self.env = env or {}
        self._map = {}
        self.extension_separator = separator
        # set some defaults depending on what is being loaded
        self.mode = default_mode or 'auto'
        self.search_order = search_order or CONTENTS_SEARCH_ORDER
        if isinstance(self.search_order, str):
            self.search_order = self.search_order.split()
        self.logger = logger or log
        self.comp_prog = comp_prog
        self.decomp_opt = decomp_opt
        self.list_xattrs_opt = list_xattrs_opt
        self.logger.info("ContentsMap: __init__(), search_order = %s",
                         str(self.search_order))
        # create the contents definitions namedtuple classes
        self._map = create_classes(definitions, self.fields)
        binaries = set()
        for mode in self.search_order:
            binaries.update(self._map[mode].binaries)
        self.available = check_available(binaries)

    def contents(self, source: str, destination: str, mode: str = "auto",
                 verbose: bool = False) -> str:
        """Generate the contents list of the archive

        :param source: optional path to the directory
        :param destination: optional path to the directory
        :param mode: optional mode to use to (de)compress with
        :param verbose: toggle
        :returns: string, list of the contents
        """
        if mode in ['auto']:
            mode = self.determine_mode(source)
        # see if it is an internal function name (string)
        # or an external function pointer
        if isinstance(self._map[mode].func, str):
            func = getattr(self, f"{self._map[mode].func}")
        else:
            func = self._map[mode].func
        return func(source, destination,
                    self._map[mode].cmd, self._map[mode].args, verbose)

    @staticmethod
    def get_extension(source: str) -> str:
        """Extracts the file extension string from the source file

        :param source: path to the archive
        :returns: string: file type extension of the source file
        """
        return os.path.splitext(source)[1]

    def determine_mode(self, source: str) -> str:
        """Uses the search_order spec parameter and compares the contents
        file extension strings with the source file and returns the mode to
        use for contents generation.

        :param source: file path of the file to determine
        :returns: string: the contents generation mode to use on the source file
        """
        self.logger.debug("ContentsMap: determine_mode(), source = %s", source)
        result = None
        for mode in self.search_order:
            self.logger.debug("ContentsMap: determine_mode(), mode = %s, %s",
                              mode, self.search_order)
            for ext in self._map[mode].extensions:
                if source.endswith(ext) and \
                        self._map[mode].enabled(self.available):
                    result = mode
                    break
            if result:
                break
        if not result:
            self.logger.debug("ContentsMap: determine_mode(), failed to "
                              "find a mode to use for: %s", source)
        return result

    def _common(self, source: str, destination: str, cmd: str, args: list, verbose: bool) -> str:
        """General purpose controller to generate the contents listing

        :param source: optional path to the directory
        :param destination: optional path to the directory
        :param cmd: definition command to use to generate the contents with
        :param args: optional command arguments
        :param verbose: toggle
        :returns: string, list of the contents
        """
        _cmd = [cmd]
        _cmd.extend((' '.join(args)
                     % {'source': source, "destination": destination,
                        'comp_prog': self.comp_prog,
                        'decomp_opt': self.decomp_opt,
                        'list_xattrs_opt': self.list_xattrs_opt,
                        }
                     ).split()
                    )
        try:
            with Popen(_cmd, stdout=PIPE, stderr=PIPE) as proc:
                results = proc.communicate()
                stdout = results[0].decode('UTF-8')
                stderr = results[1].decode('UTF-8')
                result = "\n".join([stdout, stderr])
        except OSError as error:
            result = ''
            self.logger.error("ContentsMap: _common(); OSError: %s, %s",
                              str(error), ' '.join(_cmd))
        if verbose:
            self.logger.info(result)
        return result

    @staticmethod
    def _mountable(_source: str, _destination: str, _cmd: str, _args: list, _verbose: bool) -> str:
        """Control module to mount/umount a mountable filesystem

        :param source: optional path to the directory
        :param destination: optional path to the directory
        :param cmd: definition command to use to generate the contents with
        :param args: optional command arguments
        :param verbose: toggle
        :returns: string, list of the contents
        """
        return 'NOT IMPLEMENTED!!!!!!'
