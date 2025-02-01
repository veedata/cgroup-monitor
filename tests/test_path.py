import unittest
import time

from cgroup_monitor import CGroupMonitor


class TestCGroupMonitor(unittest.TestCase):

    def test_monitor(self):
        try: 
            # CGROUP V1
            monitor = CGroupMonitor()
            monitor.start_monitor()
            time.sleep(5)
            monitor.stop_monitor()
            cpu_usage_percent_list = monitor.cpu_usage_percent_list

            if len(cpu_usage_percent_list) > 0:
                print(f"CPU Usage Percent List: {cpu_usage_percent_list}")
            else:
                print("No CPU Usage Percent List")

            assert (len(cpu_usage_percent_list) > 0)
        except:
            # CGROUP V2
            monitor = CGroupMonitor('llm_cgroup')
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
