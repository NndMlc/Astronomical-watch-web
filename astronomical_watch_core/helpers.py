"""
Helpers API za proširenja i validaciju dodataka za astronomical_watch_core.
Core se ne menja! Svi helpers koriste samo javni API core-a.
"""
from . import astronomical_time, compute_vernal_equinox
from .plugins import register_plugin, get_plugins, list_plugins

# Primer helper funkcije: formatiranje vremena

def format_dies_milidies(dt):
    dies, milidies = astronomical_time(dt)
    return f"{dies:03d}.{milidies:03d}"

# Primer: validacija pluginova (samo proverava da NE koriste core._ ili core konstante)
def is_valid_plugin(plugin):
    # Osnovna validacija: plugin ne sme imati atribut _core_patch ili _core_override
    forbidden = ["_core_patch", "_core_override", "LAMBDA_REF_DEG", "DAY_SECONDS"]
    for attr in forbidden:
        if hasattr(plugin, attr):
            return False
    return True

# API za registrovanje validnih pluginova
def safe_register_plugin(name, plugin):
    if not is_valid_plugin(plugin):
        raise ValueError("Plugin nije validan: pokušava da menja core!")
    register_plugin(name, plugin)
