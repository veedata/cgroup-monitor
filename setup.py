import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_desc = fh.read()

setuptools.setup(
    name='cgroup-monitor',
    version='0.1.2',
    url='https://github.com/veedata/cgroup-monitor',
    download_url='https://github.com/veedata/cgroup-monitor/archive/refs/tags/v0.1.2-stable.tar.gz',
    author='Viraj Thakkar',
    author_email='vdthakkar111@gmail.com',
    description='A simple library to monitor CPU and Memory usage only using cgroups. Mainly created to monitor the resources inside the container.',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    keywords=['cgroup', 'docker'],
    project_urls={
        "Code": "https://github.com/veedata/cgroup-monitor",
        "Issue tracker": "https://github.com/veedata/cgroup-monitor/issues",
        'Documentation': "https://cgroup-monitor.readthedocs.io/en/latest",
    },
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Monitoring',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    packages=['cgroup_monitor'],
    include_package_data=True,
    test_suite='tests',
)
