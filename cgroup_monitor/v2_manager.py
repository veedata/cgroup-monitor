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
        self.cgroup_path = os.path.join(self.cgroup_base_path, cgroup_name)
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
        # Create the cgroup
        if not os.path.exists(self.cgroup_path):
            if self.helper_script is None:
                proc = subprocess.run(["sudo", "mkdir", self.cgroup_path], check=True)
            else:
                proc = subprocess.run(["sudo", self.helper_script, "create", self.cgroup_path], check=True)

                if proc.returncode != 0:
                    raise Exception(f"Failed to create cgroup with command: {proc.args}")

        # Take ownership of the cgroup
        if self.helper_script is None:
            proc = subprocess.run(["sudo", "chown", "-R", f"{os.getuid()}:{os.getgid()}", self.cgroup_path], check=True)
        else:
            proc = subprocess.run(["sudo", self.helper_script, "chown", self.cgroup_path], check=True)

        if proc.returncode != 0:
            raise Exception(f"Failed to taking ownership of cgroup with command: {proc.args}")

        return proc.returncode

    def set_cpu_limit(self, quota, period=100000, sudo=False):
        '''
        Set the CPU limits. Sets the CPU using quota*period.

        Parameters:
        - quota (int): CPU quota in number of cores.
        - period (int): CPU period in microseconds. Default is 100000.
        - sudo (bool): Whether to use sudo to run the command. Default is False.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        cpu_max_data = f"{quota * period} {period}"
        cpu_max_path = os.path.join(self.cgroup_path, "cpu.max")
        runner_cmd = f"echo \"{cpu_max_data}\" > {cpu_max_path}"
        helper_cmd = [self.helper_script, "write", cpu_max_path, str(cpu_max_data)]

        return self._run_command(runner_cmd, helper_cmd, sudo)

    def set_memory_limit(self, limit, sudo=False):
        '''
        Set the memory limit in bytes.

        Parameters:
        - limit (int): Memory limit in bytes.
        - sudo (bool): Whether to use sudo to run the command.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        memory_max_path = os.path.join(self.cgroup_path, "memory.max")
        runner_cmd = f"echo \"{limit}\" > {memory_max_path}"
        helper_cmd = [self.helper_script, "write", memory_max_path, str(limit)]

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
        memory_swap_max_path = os.path.join(self.cgroup_path, "memory.swap.max")
        runner_cmd = f"echo \"{limit}\" > {memory_swap_max_path}"
        helper_cmd = [self.helper_script, "write", memory_swap_max_path, str(limit)]

        return self._run_command(runner_cmd, helper_cmd, sudo)

    def add_process(self, pid, sudo=False):
        '''
        Add a process to the cgroup.

        Parameters:
        - pid (int): Process ID to add to the cgroup.
        - sudo (bool): Whether to use sudo to run the command.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        proc_path = os.path.join(self.cgroup_path, "cgroup.procs")
        runner_cmd = f"echo \"{pid}\" > {proc_path}"
        helper_cmd = [self.helper_script, "write", proc_path, str(pid)]

        return self._run_command(runner_cmd, helper_cmd, sudo)

    def delete_cgroup(self, sudo=False):
        '''
        Delete the cgroup.

        Parameters:
        - sudo (bool): Whether to use sudo to run the command.

        Returns:
        - returncode (int): Return whether the command was successful.
        '''
        runner_cmd = f"rmdir {self.cgroup_path}"
        helper_cmd = [self.helper_script, "delete", self.cgroup_path]

        return self._run_command(runner_cmd, helper_cmd, sudo)
