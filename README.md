# cgroup-monitor

[![PyPi](https://img.shields.io/pypi/v/cgroup-monitor.svg)](https://pypi.org/project/cgroup-monitor/)
[![Documentation Status](https://readthedocs.org/projects/cgroup-monitor/badge/?version=latest)](https://cgroup-monitor.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/veedata/cgroup-monitor)](https://github.com/veedata/cgroup-monitor/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/cgroup-monitor)](https://pepy.tech/project/cgroup-monitor)

# Description
cgroup-monitor is a Python package that provides a simple interface to monitor cgroup metrics. It is designed to be used in a containerized environment to monitor the resource usage of the containers. It can be used to monitor the CPU, and memory, of the containers. 
> The current version is only compatible with cgroup v1 (Ubuntu 20.04 and lower)

# Installation
```bash
pip install cgroup-monitor
```

# Usage
```python
from cgroup_monitor import CgroupMonitor

monitor = CgroupMonitor()
monitor.start_monitor()
# run task here
cpu, mem = monitor.stop_monitor()

print(f"CPU Usage: {cpu}%, Memory Usage: {mem}%")
```

# Features
- Monitor CPU and Memory usage of the containers
- Simple interface to start and stop monitoring
- Lightweight and easy to use

# Documentation
The official documentation is hosted on Read the Docs: https://cgroup-monitor.readthedocs.io/en/latest/

# License
This project is licensed under the terms of the MIT license, see [LICENSE](./LICENSE).

# Contributing
Contributions are welcome, and they are greatly appreciated! Every little bit helps.

