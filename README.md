# cgroup-monitor

[![PyPi](https://img.shields.io/pypi/v/cgroup-monitor.svg)](https://pypi.org/project/cgroup-monitor/)
[![Documentation Status](https://readthedocs.org/projects/cgroup-monitor/badge/?version=latest)](https://cgroup-monitor.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/veedata/cgroup-monitor)](https://github.com/veedata/cgroup-monitor/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/cgroup-monitor)](https://pepy.tech/project/cgroup-monitor)

# Description
A package to simplify CPU and Memory Analysis using cgroup. Primiarily created to give access to windows of CPU and Memory usage.
The package also provides a built-in mechanism to manage the cgroup resources.

# Installation
```bash
pip install cgroup-monitor
```

# Usage
```python
from cgroup_monitor import CGroupManager

# Manage cgroup resources
manager = CGroupManager()
manager.create_cgroup("test_cgroup")
manager.set_cpu_limit("test_cgroup", 5) # 5 cores  
manager.set_memory_limit("test_cgroup", 512 * 1024 * 1024)  # 512MB Memory
```

```python
from cgroup_monitor import CGroupMonitor

monitor = CGroupMonitor("test_cgroup")
monitor.start_monitor()
# run task here
manager.add_process_to_cgroup("test_cgroup", 1234) # Add process with PID 1234 to the cgroup 
last_n_op = monitor.get_last_n_operations(10) # Measurements from last 10 time interval
output = monitor.stop_monitor()

print(output)
# output = {
#     "average_cpu_usage_percent": float,
#     "max_cpu_usage_percent": float,
#     "average_memory_usage_gib": float,
#     "max_memory_usage_gib": float,
#     "average_memory_usage_percent": float,
#     "max_memory_usage_percent": float,
#     "monitoring_duration_s": float
# }
```

# Documentation
The official, definitely complete, documentation is on Read the Docs: https://cgroup-monitor.readthedocs.io/en/latest/

# License
This project is licensed under the terms of the MIT license, see [LICENSE](./LICENSE).

# Contributing
Contributions are welcome, and they are greatly appreciated! Every little bit helps.

