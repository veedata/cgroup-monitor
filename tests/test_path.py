import unittest
import time

from cgroup_monitor import CGroupMonitor


class TestCGroupMonitor(unittest.TestCase):

    def test_monitor(self):
        monitor = CGroupMonitor()
        monitor.start_monitor()
        time.sleep(5)
        op = monitor.stop_monitor()

        assert op["average_cpu_usage_percent"] >= 0
        assert op["average_memory_usage_gib"] >= 0
        assert op["average_memory_usage_percent"] >= 0
        assert op["max_cpu_usage_percent"] >= 0
        assert op["max_memory_usage_gib"] >= 0
        assert op["max_memory_usage_percent"] >= 0

        assert op["monitoring_duration_s"] >= 5
        assert op["monitoring_duration_s"] < 6
