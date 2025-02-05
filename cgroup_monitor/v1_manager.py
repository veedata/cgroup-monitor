import os
import subprocess


class CGroupManager:
    def __init__(self, cgroup_name, cgroup_base_path="/sys/fs/cgroup", helper_script=None):
        '''
        Initialize the CGroupManager object. If helper_script is not provided,
        the script will use the default method of managing cgroups.

        One CGroupManager object is responsible for managing one cgroup. Hence,
        the code expects the cgoup_name to be provided while initializing the object.

        Parameters:
        - cgroup_name (str): Name of the cgroup. Necessary argument.
        - cgroup_base_path (str): Base path of the cgroup. Default is /sys/fs/cgroup.
        - helper_script (str): Path to the helper script to manage cgroups. Default is None.

        Returns:
        - None
        '''
        self.cgroup_name = cgroup_name
        self.cgroup_base_path = cgroup_base_path
        self.cpu_path = os.path.join(self.cgroup_base_path, "cpu", cgroup_name)
        self.mem_path = os.path.join(self.cgroup_base_path, "memory", cgroup_name)
        self.helper_script = None

        if helper_script is not None:
            self.helper_script = os.path.join(os.path.dirname(__file__), helper_script)

    def _run_command(self, runner_cmd, helper_cmd, sudo):
        '''
        Internal function to run given command conditionally.
        If sudo is True, the command will be run with sudo privileges.
        Otherwise, the command will be run as is.
        If helper_script is provided, the command will be run using the helper script.

        Parameters:
        - runner_cmd (str): Command to run using subprocess.run.
        - helper_cmd (list): Command to run using subprocess.run.
        - sudo (bool): Whether to use sudo to run the command.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        try:
            if sudo:
                runner_cmd = f"sudo sh -c '{runner_cmd}'"
                helper_cmd.insert(0, "sudo")

            if self.helper_script is None:
                proc = subprocess.run(runner_cmd, shell=True, check=True)
            else:
                proc = subprocess.run(helper_cmd, check=True)

            return proc.returncode

        except Exception as e:
            raise Exception(f"Failed to run command: {e}")

    def create_cgroup(self):
        '''
        If non-existant, create cgroup and take ownership.
        Note, this command requires sudo privileges.

        Parameters:
        - None

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        # Create cgroup if it does not exist
        for path in [self.cpu_path, self.mem_path]:
            if not os.path.exists(path):
                if self.helper_script is None:
                    proc = subprocess.run(["sudo", "mkdir", path], check=True)
                else:
                    proc = subprocess.run(["sudo", self.helper_script, "create", path], check=True)

                if proc.returncode != 0:
                    raise Exception(f"Failed to create cgroup: {path}")

        # Take ownership of cgroup
        for path in [self.cpu_path, self.mem_path]:
            if self.helper_script is None:
                proc = subprocess.run(["sudo", "chown", "-R", f"{os.getuid()}:{os.getgid()}", path], check=True)
            else:
                proc = subprocess.run(["sudo", self.helper_script, "chown", os.getuid(), path], check=True)

            if proc.returncode != 0:
                raise Exception(f"Failed to take ownership of cgroup: {path}")

        return proc.returncode

    def set_cpu_limit(self, quota, period=100000, sudo=False):
        '''
        Set the CPU limits.

        Parameters:
        - quota (int): CPU quota in microseconds.
        - period (int): CPU period in microseconds. Default is 100000.
        - sudo (bool): Whether to use sudo to run the command. Default is True.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        cpu_quota_path = os.path.join(self.cpu_path, "cpu.cfs_quota_us")
        cpu_period_path = os.path.join(self.cpu_path, "cpu.cfs_period_us")

        runner_cmd_quota = f"echo \"{quota * period}\" > {cpu_quota_path}"
        runner_cmd_period = f"echo \"{period}\" > {cpu_period_path}"
        helper_cmd_quota = [self.helper_script, "write", cpu_quota_path, str(quota)]
        helper_cmd_period = [self.helper_script, "write", cpu_period_path, str(period)]

        self._run_command(runner_cmd_quota, helper_cmd_quota, sudo)
        return self._run_command(runner_cmd_period, helper_cmd_period, sudo)

    def set_memory_limit(self, limit, sudo=False):
        '''
        Set the memory limit in bytes.

        Parameters:
        - limit (int): Memory limit in bytes.
        - sudo (bool): Whether to use sudo to run the command. Default is True.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        mem_limit_path = os.path.join(self.mem_path, "memory.limit_in_bytes")
        runner_cmd = f"echo \"{limit}\" > {mem_limit_path}"
        helper_cmd = [self.helper_script, "write", mem_limit_path, str(limit)]

        return self._run_command(runner_cmd, helper_cmd, sudo)

    def set_memory_swap_limit(self, limit, sudo=False):
        '''
        Set the memory+swap limit in bytes.
        Note: This sets maximum amount for the sum of memory and swap usage.

        Parameters:
        - limit (int): Memory+swap limit in bytes.
        - sudo (bool): Whether to use sudo to run the command.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        mem_swap_limit_path = os.path.join(self.mem_path, "memory.memsw.limit_in_bytes")
        runner_cmd = f"echo \"{limit}\" > {mem_swap_limit_path}"
        helper_cmd = [self.helper_script, "write", mem_swap_limit_path, str(limit)]

        return self._run_command(runner_cmd, helper_cmd, sudo)

    def add_process(self, pid, sudo=False):
        '''
        Add a process to the cgroup.

        Parameters:
        - pid (int): Process ID to add to the cgroup.
        - sudo (bool): Whether to use sudo to run the command. Default is True.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        for path in [self.cpu_path, self.mem_path]:
            procs_path = os.path.join(path, "cgroup.procs")
            runner_cmd = f"echo \"{pid}\" > {procs_path}"
            helper_cmd = [self.helper_script, "write", procs_path, str(pid)]

            self._run_command(runner_cmd, helper_cmd, sudo)

    def delete_cgroup(self, sudo=False):
        '''
        Delete the cgroup directories.

        Parameters:
        - sudo (bool): Whether to use sudo to run the command. Default is True.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        for path in [self.cpu_path, self.mem_path]:
            if os.path.exists(path):
                runner_cmd = f"rmdir {path}"
                helper_cmd = [self.helper_script, "delete", path]
                self._run_command(runner_cmd, helper_cmd, sudo)
