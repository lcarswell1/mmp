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

BackendPanel
A subclass of wx.Panel to be instantiated with the backend instance as the first argument, then standard arguments for wx.Panel, giving the splitter frame as a parent and used as the user interface for this backend.
The instance can be accessed with backend.panel.

on_search
A method which is called with the text of a search from the default search field of the default backend panel (leatherman.ui.panels.backend_panel.BackendPanel).
This method should return a list of Track instances which can be loaded into the results view. It will be called as a job (in a separate thread), so no attempt should be made to make this method non-blocking. Also, be aware of any thread-safety concerns, particularly when interacting with wx.
