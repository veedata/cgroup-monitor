import unittest
import time

from cgroup_monitor import CGroupMonitor

class TestCGroupMonitor(unittest.TestCase):

    def test_monitor(self):
        monitor = CGroupMonitor()
        monitor.start_monitor()
        time.sleep(5)
        monitor.stop_monitor()
        cpu_usage_percent_list = monitor.cpu_usage_percent_list

        if len(cpu_usage_percent_list) > 0:
            print(f"CPU Usage Percent List: {cpu_usage_percent_list}")
        else:
            print("No CPU Usage Percent List")

        assert(len(cpu_usage_percent_list) > 0)