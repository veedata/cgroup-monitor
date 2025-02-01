import os


def is_cgroup_v2():
    return os.path.exists("/sys/fs/cgroup/cgroup.controllers")


if is_cgroup_v2():
    from .v2_monitor import CGroupMonitor
    from .v2_manager import CGroupManager
else:
    from .v1_monitor import CGroupMonitor
    from .v1_manager import CGroupManager

__version__ = "0.1.3"
__all__ = ["CGroupMonitor"]
