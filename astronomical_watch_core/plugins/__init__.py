# Plugin registry for astronomical_watch_core

__all__ = ["register_plugin", "get_plugins", "list_plugins"]

_plugins = {}

def register_plugin(name, plugin):
    if name in _plugins:
        raise ValueError(f"Plugin '{name}' already registered.")
    _plugins[name] = plugin

def get_plugins():
    return dict(_plugins)

def list_plugins():
    return list(_plugins.keys())
