This directory contains all the backends for Leatherman.

Each file is just a standard module with some expected attributes. These attributes are listed below:

name
The name of the backend. Must be present for the module to load.

description
A description of this backend to be used in tooltip strings.

config
An instance of simpleconf.Section which holds the configuration values for this backend.

on_init
A method which is called with the instance of Backend created from the module. The backend loading code sets backend in the module to be this instance, so you do not need to save it yourself, but it might be useful to instantiate menus ETC at this point.
