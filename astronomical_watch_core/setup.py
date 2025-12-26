
from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
import os

class LicenseCheckInstall(install):
    def run(self):
        # Pozovi skriptu za prihvatanje licence pre instalacije
        try:
            import setup_license_check
        except ImportError:
            sys.path.insert(0, os.path.dirname(__file__))
            import setup_license_check
        install.run(self)

setup(
    name="astronomical_watch_core",
    version="0.1.0",
    description="Minimalni core za astronomsko vreme (Dies, miliDies, ekvinocijum)",
    author="NndMlc",
    packages=find_packages(),
    python_requires=">=3.8",
    license="SEE LICENSE.CORE",
    include_package_data=True,
    zip_safe=False,
    cmdclass={
        'install': LicenseCheckInstall,
    },
)