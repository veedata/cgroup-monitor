import os
import subprocess

class CGroupManager:
    def __init__(self, cgroup_name, cgroup_base_path="/sys/fs/cgroup", helper_script=""):
        self.cgroup_name = cgroup_name
        self.cgroup_base_path = cgroup_base_path
        self.cpu_path = os.path.join(self.cgroup_base_path, "cpu", cgroup_name)
        self.mem_path = os.path.join(self.cgroup_base_path, "memory", cgroup_name)
        self.helper_script = None

        if helper_script != "":
            self.helper_script = os.path.join(os.path.dirname(__file__), helper_script)

    def create_cgroup(self):
        for path in [self.cpu_path, self.mem_path]:
            if not os.path.exists(path):
                if self.helper_script is None:
                    subprocess.run(["sudo", "mkdir", path], check=True)
                else:
                    subprocess.run(["sudo", self.helper_script, "create", path], check=True)

    def set_cpu_limit(self, quota, period=100000):
        cpu_quota_path = os.path.join(self.cpu_path, "cpu.cfs_quota_us")
        cpu_period_path = os.path.join(self.cpu_path, "cpu.cfs_period_us")

        if self.helper_script is None:
            with open(cpu_quota_path, "w") as f:
                f.write(str(quota))
            with open(cpu_period_path, "w") as f:
                f.write(str(period))
        else:
            subprocess.run(["sudo", self.helper_script, "write", cpu_quota_path, str(quota)], check=True)
            subprocess.run(["sudo", self.helper_script, "write", cpu_period_path, str(period)], check=True)

    def set_memory_limit(self, limit):
        mem_limit_path = os.path.join(self.mem_path, "memory.limit_in_bytes")

        if self.helper_script is None:
            with open(mem_limit_path, "w") as f:
                f.write(str(limit))
        else:
            subprocess.run(["sudo", self.helper_script, "write", mem_limit_path, str(limit)], check=True)

    def add_process(self, pid):
        for path in [self.cpu_path, self.mem_path]:
            procs_path = os.path.join(path, "cgroup.procs")
            if self.helper_script is None:
                with open(procs_path, "w") as f:
                    f.write(str(pid))
            else:
                subprocess.run(["sudo", self.helper_script, "write", procs_path, str(pid)], check=True)

    def delete_cgroup(self):
        for path in [self.cpu_path, self.mem_path]:
            if os.path.exists(path):
                if self.helper_script is None:
                    subprocess.run(["sudo", "rmdir", path], check=True)
                else:
                    subprocess.run(["sudo", self.helper_script, "delete", path], check=True)