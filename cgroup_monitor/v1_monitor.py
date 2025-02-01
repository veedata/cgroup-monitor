import time
import os
import threading


class CGroupMonitor:
    def __init__(self, cgroup_name="", cgroup_base_path="/sys/fs/cgroup"):
        self.cgroup_name = cgroup_name
        self.cgroup_base_path = cgroup_base_path

        self.monitoring = False
        self.cpu_usage_percentages = []
        self.memory_usage = []
        self.monitor_thread = None
        self.start_time = None

    def get_cpu_usage_us(self):
        """
        In cgroup v1, we read from cpuacct.usage (in nanoseconds).
        """
        cpu_stat_path = os.path.join(self.cgroup_base_path, "cpu", self.cgroup_name, "cpuacct.usage")
        try:
            with open(cpu_stat_path, "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 0

    def get_cpu_limit(self):
        """
        Return (quota, period).
        """
        cpu_quota_path = os.path.join(self.cgroup_base_path, "cpu", self.cgroup_name, "cpu.cfs_quota_us")
        cpu_period_path = os.path.join(self.cgroup_base_path, "cpu", self.cgroup_name, "cpu.cfs_period_us")
        quota, period = None, None
        try:
            with open(cpu_quota_path, "r") as f_quota:
                quota = int(f_quota.read().strip())
        except FileNotFoundError:
            pass
        try:
            with open(cpu_period_path, "r") as f_period:
                period = int(f_period.read().strip())
        except FileNotFoundError:
            pass
        return quota, period

    def get_memory_usage(self):
        memory_current_path = os.path.join(self.cgroup_base_path, "memory", self.cgroup_name, "memory.usage_in_bytes")
        try:
            with open(memory_current_path, "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 0

    def get_memory_limit(self):
        memory_max_path = os.path.join(self.cgroup_base_path, "memory", self.cgroup_name, "memory.limit_in_bytes")
        try:
            with open(memory_max_path, "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 0

    def _monitor(self, interval):
        prev_cpu_usage = self.get_cpu_usage_us()
        while self.monitoring:
            time.sleep(interval)
            current_cpu_usage = self.get_cpu_usage_us()
            delta = current_cpu_usage - prev_cpu_usage
            prev_cpu_usage = current_cpu_usage

            quota, period = self.get_cpu_limit()
            if quota is None or quota < 0:
                quota = os.cpu_count() * 100000
                period = 100000
            num_cores = quota / period
            total_cpu_time_available = num_cores * (interval * 1e9)

            cpu_usage_percent = (delta / total_cpu_time_available) * 100
            self.cpu_usage_percentages.append(cpu_usage_percent)
            self.memory_usage.append(self.get_memory_usage())

    def start_monitor(self, interval=1):
        if self.monitoring:
            raise RuntimeError("Monitoring is already running.")
        self.monitoring = True
        self.cpu_usage_percentages.clear()
        self.memory_usage.clear()
        self.start_time = time.time()
        self.monitor_thread = threading.Thread(
            target=self._monitor, args=(interval,), daemon=True
        )
        self.monitor_thread.start()

    def get_last_n_stats(self, n=1):
        if not self.monitoring:
            raise RuntimeError("Monitoring is not running.")

        avg_cpu = (sum(self.cpu_usage_percentages[-n:]) / n
                   if self.cpu_usage_percentages else 0)
        avg_mem = (sum(self.memory_usage[-n:]) / n
                   if self.memory_usage else 0)
        avg_mem_gb = avg_mem / (1024 ** 3)
        avg_mem_pct = (avg_mem / self.get_memory_limit()) * 100 if self.get_memory_limit() else 0

        max_cpu = max(self.cpu_usage_percentages) if self.cpu_usage_percentages else 0
        max_mem = max(self.memory_usage) if self.memory_usage else 0
        max_mem_gb = max_mem / (1024 ** 3)
        max_mem_pct = (max_mem / self.get_memory_limit()) * 100 if self.get_memory_limit() else 0

        return {
            "average_cpu_usage_percent": round(avg_cpu, 2),
            "average_memory_usage_gib": round(avg_mem_gb, 2),
            "average_memory_usage_percent": round(avg_mem_pct, 2),
            "max_cpu_usage_percent": round(max_cpu, 2),
            "max_memory_usage_gib": round(max_mem_gb, 2),
            "max_memory_usage_percent": round(max_mem_pct, 2),
        }

    def stop_monitor(self):
        if not self.monitoring:
            raise RuntimeError("Monitoring is not running.")
        self.monitoring = False
        self.monitor_thread.join()
        total_time = time.time() - self.start_time

        avg_cpu = (sum(self.cpu_usage_percentages) / len(self.cpu_usage_percentages)
                   if self.cpu_usage_percentages else 0)
        avg_mem = (sum(self.memory_usage) / len(self.memory_usage)
                   if self.memory_usage else 0)
        avg_mem_gb = avg_mem / (1024 ** 3)
        mem_limit = self.get_memory_limit()
        avg_mem_pct = (avg_mem / mem_limit) * 100 if mem_limit else 0

        max_cpu = max(self.cpu_usage_percentages) if self.cpu_usage_percentages else 0
        max_mem = max(self.memory_usage) if self.memory_usage else 0
        max_mem_gb = max_mem / (1024 ** 3)
        max_mem_pct = (max_mem / mem_limit) * 100 if mem_limit else 0

        return {
            "average_cpu_usage_percent": round(avg_cpu, 2),
            "average_memory_usage_gib": round(avg_mem_gb, 2),
            "average_memory_usage_percent": round(avg_mem_pct, 2),
            "max_cpu_usage_percent": round(max_cpu, 2),
            "max_memory_usage_gib": round(max_mem_gb, 2),
            "max_memory_usage_percent": round(max_mem_pct, 2),
            "monitoring_duration_s": round(total_time, 2),
        }
