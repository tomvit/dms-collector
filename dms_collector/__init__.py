# -*- coding: utf-8 -*-
# @author: Tomas Vitvar, https://vitvar.com, tomas.vitvar@oracle.com

from .dms import (
    DmsCollector,
    TBML_VERSIONS,
    dms_version,
    DataParserError,
    TableNotExistError,
    LoginError,
    DataVersionError,
)

from importlib.metadata import version, PackageNotFoundError


def __getattr__(name):
    """
    Return the version number of the package as a lazy attribute.
    """
    if name == "__version__":
        return dms_version()
    raise AttributeError(f"module {__name__} has no attribute {name}")
