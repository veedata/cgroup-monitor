import time
import threading
import os

CPUACCT_USAGE_PATH = "/sys/fs/cgroup/cpuacct/cpuacct.usage"
CPU_QUOTA_PATH = "/sys/fs/cgroup/cpu/cpu.cfs_quota_us"
CPU_PERIOD_PATH = "/sys/fs/cgroup/cpu/cpu.cfs_period_us"
MEMORY_USAGE_PATH = "/sys/fs/cgroup/memory/memory.usage_in_bytes"
MEMORY_LIMIT_PATH = "/sys/fs/cgroup/memory/memory.limit_in_bytes"


class CGroupMonitor(threading.Thread):
    """
    Class to monitor the cgroup stats of a process
    """

    def __init__(self):
        # For threading
        super().__init__()
        self._stop_event = threading.Event()
        # For monitoring
        self.monitor_start_time = 0
        self.monitor_end_time = 0
        self.cpu_limit = self.get_cpu_limit()
        self.cpu_usage_percent_list = []
        self.memory_limit = self.get_memory_limit()
        self.memory_usage_percent_list = []
        self.monitor_thread = None

    def get_cpu_usage(self, interval=0.1):
        """
        Get the CPU usage of the process

        Parameters:
        - interval (float): Interval to calculate the CPU usage. Default 0.1s

        Returns:
        - cpu_usage (float): The CPU usage of the process
        """
        with open(CPUACCT_USAGE_PATH, "r") as f:
            start_cpu_usage = int(f.read())
            start_time = time.time_ns()

        time.sleep(interval)

        with open(CPUACCT_USAGE_PATH, "r") as f:
            end_cpu_usage = int(f.read())
            end_time = time.time_ns()

        cpu_usage = (end_cpu_usage - start_cpu_usage) / (end_time - start_time)
        return cpu_usage

    def get_cpu_usage_percent(self, interval=1, decimal_places=2):
        """
        Get the CPU usage percentage of the process

        Parameters:
        - interval (float): The interval to calculate the CPU usage. Default 1s

        Returns:
        - cpu_usage_percent (float): The CPU usage percentage of the process
        """
        cpu_usage = self.get_cpu_usage(interval)
        cpu_usage_percent = cpu_usage / self.cpu_limit * 100
        return round(cpu_usage_percent, decimal_places)

    def get_cpu_limit(self):
        """
        Get the CPU limit of the process

        Returns:
        - cpu_limit (float): The CPU limit of the process
        """
        with open(CPU_QUOTA_PATH, "r") as f:
            cpu_quota = int(f.read())

        if cpu_quota == -1:
            return os.cpu_count()
        else:
            with open(CPU_PERIOD_PATH, "r") as f2:
                cpu_limit = cpu_quota / int(f2.read())

        return cpu_limit

    def get_memory_usage(self):
        """
        Get the memory usage of the process

        Returns:
        - memory_usage (int): The memory usage of the process (in bytes)
        """
        with open(MEMORY_USAGE_PATH, "r") as f:
            memory_usage = int(f.read())
        return memory_usage

    def get_memory_usage_percent(self, decimal_places=2):
        """
        Get the memory usage percentage of the process

        Returns:
        - memory_usage_percent (float): The memory usage percentage of system
        """
        memory_usage = self.get_memory_usage()
        memory_usage_percent = memory_usage / self.memory_limit * 100
        return round(memory_usage_percent, decimal_places)

    def get_memory_limit(self):
        """
        Get the memory limit of the process

        Returns:
        - memory_limit (int): The memory limit of the process (in bytes)
        """
        with open(MEMORY_LIMIT_PATH, "r") as f:
            memory_limit = int(f.read())
        return memory_limit

    def start_monitor(self):
        """
        Starts the monitor in a secondary thread.
        The monitor will keep a track of the CPU and Memory usage of system
        and print the average stats when end_monitor is called.
        """
        self.monitor_start_time = time.time_ns()

        print("[CGM] Monitor started")
        print("[CGM] CPU Limit: ", self.get_cpu_limit())
        print("[CGM] Memory Limit: ", self.get_memory_limit())

        # Monitor the stats every 1 second in a thread
        self.monitor_thread = threading.Thread(target=self.constant_monitoring)
        self.monitor_thread.start()

    def stop_monitor(self):
        """
        Ends monitor and returns the average CPU and Memory usage of system

        Returns:
        - cpu_usage (float): Average CPU usage (in %)
        - memory_usage (float): Average Memory usage (in %)
        """

        # End the monitor
        self._stop_event.set()
        self.monitor_thread.join()
        self.monitor_end_time = time.time_ns()

        if (len(self.cpu_usage_percent_list) > 0 and
                len(self.memory_usage_percent_list)):
            # Calculate the average CPU and Memory usage
            average_cpu_usage = sum(self.cpu_usage_percent_list) / len(
                self.cpu_usage_percent_list
            )
            average_memory_usage = sum(self.memory_usage_percent_list) / len(
                self.memory_usage_percent_list
            )
        else:
            return 1, 1
        return round(average_cpu_usage, 2), round(average_memory_usage, 2)

    def constant_monitoring(self):
        """
        Keep monitoring the CPU and Memory usage of the system
        Every datapoint to be stored in a list for average calculation
        """

        # Start the monitor
        self.monitor_start_time = time.time_ns()

        # Monitor the stats every 1 second
        while not self._stop_event.is_set():
            # If time is greater than 1 second, print
            if (time.time_ns() - self.monitor_start_time) > 1000000000:
                self.monitor_start_time = time.time_ns()
                self.cpu_usage_percent_list.append(
                    self.get_cpu_usage_percent())
                self.memory_usage_percent_list.append(
                    self.get_memory_usage_percent())
