import time
import os
import threading


class CGroupMonitor:
    def __init__(self, cgroup_name="", cgroup_base_path="/sys/fs/cgroup"):
        '''
        Initialize the CGroupMonitor object.

        Parameters:
        - cgroup_name (str): Name of the cgroup. Default is an empty string.
        - cgroup_base_path (str): Base path of the cgroup. Default is /sys/fs/cgroup.

        Returns:
        - None
        '''
        self.cgroup_name = cgroup_name
        self.cgroup_base_path = cgroup_base_path
        self.cgroup_path = os.path.join(cgroup_base_path, cgroup_name)

        self.monitoring = False
        self.cpu_usage_percentages = []
        self.memory_usage = []
        self.monitor_thread = None
        self.start_time = None

    def _read_file(self, path):
        '''
        Internal method to read the contents of a file.

        Parameters:
        - path (str): Path to the file.

        Returns:
        - content (str): Content of the file.
        '''
        try:
            with open(path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def get_cpu_usage_us(self):
        '''
        Get the cumulative CPU usage in microseconds.

        Parameters:
        - None

        Returns:
        - usage_usec (int): CPU usage in microseconds.
        '''
        cpu_stat_path = os.path.join(self.cgroup_path, "cpu.stat")
        content = self._read_file(cpu_stat_path)
        if content:
            for line in content.splitlines():
                if line.startswith("usage_usec"):
                    return int(line.split()[1])
        return 0

    def get_cpu_limit(self):
        '''
        Get the CPU quota and period.

        Parameters:
        - None

        Returns:
        - quota (int or None): CPU quota.
        - period (int): CPU period in microseconds.
        '''
        cpu_max_path = os.path.join(self.cgroup_path, "cpu.max")
        content = self._read_file(cpu_max_path)
        if content:
            data = content.split()
            if data[0] == "max":
                return None, int(data[1])
            else:
                return int(data[0]), int(data[1])
        return None, 100000  # Default period if not specified

    def get_memory_usage(self):
        '''
        Get the current memory usage in bytes.

        Parameters:
        - None

        Returns:
        - memory_usage (int): Memory usage in bytes.
        '''
        memory_current_path = os.path.join(self.cgroup_path, "memory.current")
        content = self._read_file(memory_current_path)
        return int(content) if content else 0

    def get_memory_limit(self):
        '''
        Get the memory limit in bytes.

        Parameters:
        - None

        Returns:
        - memory_limit (int): Memory limit in bytes.
        '''
        memory_max_path = os.path.join(self.cgroup_path, "memory.max")
        content = self._read_file(memory_max_path)
        return int(content) if content else 0

    def get_swap_limit(self):
        '''
        Get the memory+swap limit in bytes.

        Parameters:
        - None

        Returns:
        - memory_swap_limit (int): Memory+Swap limit in bytes.
        '''
        swap_max_path = os.path.join(self.cgroup_path, "memory.swap.max")
        content = self._read_file(swap_max_path)
        return int(content) if content else 0

    def _monitor(self, interval):
        '''
        Internal method to monitor CPU and memory usage.

        Parameters:
        - interval (int): Monitoring interval in seconds.

        Returns:
        - None
        '''
        previous_cpu_usage = self.get_cpu_usage_us()
        while self.monitoring:
            time.sleep(interval)

            # CPU percentage calculation
            current_cpu_usage = self.get_cpu_usage_us()
            delta_cpu_usage = current_cpu_usage - previous_cpu_usage
            previous_cpu_usage = current_cpu_usage

            quota, period = self.get_cpu_limit()
            num_cores = quota / period if quota else os.cpu_count()
            total_cpu_time_available = num_cores * (interval * 1000000)
            cpu_usage_percentage = (delta_cpu_usage / total_cpu_time_available) * 100

            # Store results
            self.cpu_usage_percentages.append(cpu_usage_percentage)
            self.memory_usage.append(self.get_memory_usage())

    def start_monitor(self, interval=1.0):
        '''
        Start monitoring CPU and memory usage.

        Parameters:
        - interval (float): Monitoring interval in seconds. Default is 1 second.
            Uses time.sleep() and can be float value for higher precision.

        Returns:
        - None
        '''
        if self.monitoring:
            raise RuntimeError("Monitoring is already running.")

        self.monitoring = True
        self.cpu_usage_percentages = []
        self.memory_usage = []
        self.start_time = time.time()
        self.monitor_thread = threading.Thread(
            target=self._monitor, args=(interval,), daemon=True
        )
        self.monitor_thread.start()

    def get_last_n_stats(self, n=1, info_level=0):
        '''
        Get the last n stats recorded.

        Parameters:
        - n (int): Number of stats to retrieve. Default is 1.
        - info_level (int): Level of information to return. Default is 0.
            - 0: Return average and max usage stats.
            - 1: Return detailed stats including all recorded values.

        Returns:
        - stats (dict): Dictionary containing average and max usage stats.
        '''
        if not self.monitoring:
            raise RuntimeError("Monitoring is not running.")

        avg_cpu = (
            sum(self.cpu_usage_percentages[-n:]) / n
            if self.cpu_usage_percentages else 0
        )
        avg_memory = (
            sum(self.memory_usage[-n:]) / n
            if self.memory_usage else 0
        )
        avg_memory_gb = avg_memory / (1024 ** 3)
        avg_memory_percent = (
            (avg_memory / self.get_memory_limit()) * 100
            if self.get_memory_limit() else 0
        )

        max_cpu = max(self.cpu_usage_percentages[-n:], default=0)
        max_memory = max(self.memory_usage[-n:], default=0)
        max_memory_gb = max_memory / (1024 ** 3)
        max_memory_percent = (
            (max_memory / self.get_memory_limit()) * 100
            if self.get_memory_limit() else 0
        )

        if info_level == 1:
            return {
                "average_cpu_usage_percent": round(avg_cpu, 2),
                "max_cpu_usage_percent": round(max_cpu, 2),
                "cpu_usage_percentage_list": self.cpu_usage_percentages[-n:],
                "average_memory_usage_gib": round(avg_memory_gb, 2),
                "max_memory_usage_gib": round(max_memory_gb, 2),
                "average_memory_usage_percent": round(avg_memory_percent, 2),
                "max_memory_usage_percent": round(max_memory_percent, 2),
                "memory_usage_bytes_list": self.memory_usage[-n:],
            }

        return {
            "average_cpu_usage_percent": round(avg_cpu, 2),
            "max_cpu_usage_percent": round(max_cpu, 2),
            "average_memory_usage_gib": round(avg_memory_gb, 2),
            "max_memory_usage_gib": round(max_memory_gb, 2),
            "average_memory_usage_percent": round(avg_memory_percent, 2),
            "max_memory_usage_percent": round(max_memory_percent, 2),
        }

    def stop_monitor(self, info_level=0):
        '''
        Stop monitoring and return average and max usage stats.
        ```
        Returns:
            dict = {
                "average_cpu_usage_percent": float,
                "max_cpu_usage_percent": float,
                "average_memory_usage_gib": float,
                "max_memory_usage_gib": float,
                "average_memory_usage_percent": float,
                "max_memory_usage_percent": float,
                "monitoring_duration_s": float
            }
        ```

        Parameters:
        - info_level (int): Level of information to return. Default is 0.
            - 0: Return average and max usage stats.
            - 1: Return detailed stats including all recorded values.

        Returns:
        - stats (dict): Dictionary containing average and max usage stats.
        '''
        if not self.monitoring:
            raise RuntimeError("Monitoring is not running.")

        self.monitoring = False
        self.monitor_thread.join()
        self.monitor_thread = None
        total_time = time.time() - self.start_time

        avg_cpu = (
            sum(self.cpu_usage_percentages) / len(self.cpu_usage_percentages)
            if self.cpu_usage_percentages else 0
        )
        avg_memory = (
            sum(self.memory_usage) / len(self.memory_usage)
            if self.memory_usage else 0
        )
        avg_memory_gb = avg_memory / (1024 ** 3)
        avg_memory_percent = (
            (avg_memory / self.get_memory_limit()) * 100
            if self.get_memory_limit() else 0
        )

        max_cpu = max(self.cpu_usage_percentages, default=0)
        max_memory = max(self.memory_usage, default=0)
        max_memory_gb = max_memory / (1024 ** 3)
        max_memory_percent = (
            (max_memory / self.get_memory_limit()) * 100
            if self.get_memory_limit() else 0
        )

        if info_level == 1:
            return {
                "average_cpu_usage_percent": round(avg_cpu, 2),
                "max_cpu_usage_percent": round(max_cpu, 2),
                "cpu_usage_percentage_list": self.cpu_usage_percentages,
                "average_memory_usage_gib": round(avg_memory_gb, 2),
                "max_memory_usage_gib": round(max_memory_gb, 2),
                "average_memory_usage_percent": round(avg_memory_percent, 2),
                "max_memory_usage_percent": round(max_memory_percent, 2),
                "memory_usage_bytes_list": self.memory_usage,
                "start_time": self.start_time,
                "monitoring_duration_s": round(total_time, 2),
            }

        return {
            "average_cpu_usage_percent": round(avg_cpu, 2),
            "max_cpu_usage_percent": round(max_cpu, 2),
            "average_memory_usage_gib": round(avg_memory_gb, 2),
            "max_memory_usage_gib": round(max_memory_gb, 2),
            "average_memory_usage_percent": round(avg_memory_percent, 2),
            "max_memory_usage_percent": round(max_memory_percent, 2),
            "monitoring_duration_s": round(total_time, 2),
        }
