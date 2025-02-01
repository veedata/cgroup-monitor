import os

def is_cgroup_v2():
    return os.path.exists("/sys/fs/cgroup/cgroup.controllers")

if is_cgroup_v2():
    from .v2_monitor import CGroupMonitor
else:
    from .main_monitor import CGroupMonitor

__version__ = "0.1.3"
__all__ = ["CGroupMonitor"]
