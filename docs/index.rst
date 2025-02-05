.. cgroup-monitor documentation master file, created by
   sphinx-quickstart on Sat Feb  1 16:44:38 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cgroup-monitor
==========================================

A package to simplify CPU and Memory Analysis using cgroup. Primiarily created to give access to windows of CPU and Memory usage.
The package also provides a built-in mechanism to manage the cgroup resources.

Installation
--------------------------------------
.. code-block:: language

   pip install cgroup-monitor


Usage
--------------------------------------
CGroupManager, a simple example.

.. code-block:: python

   from cgroup_monitor import CGroupManager

   # Manage cgroup resources
   manager = CGroupManager()
   manager.create_cgroup("test_cgroup")
   manager.set_cpu_limit("test_cgroup", 5) # 5 cores  
   manager.set_memory_limit("test_cgroup", 512 * 1024 * 1024)  # 512MB Memory


CGroupMonitor, a simple example.

.. code-block:: python

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


License
--------------------------------------
This project is licensed under the terms of the MIT license, see [LICENSE](./LICENSE).

Contributing
--------------------------------------
Contributions are welcome, and they are greatly appreciated! Every little bit helps.


.. toctree::
   :maxdepth: 2
   :caption: Getting Started:
   :hidden:

Links
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* Source code: https://github.com/veedata/cgroup-monitor