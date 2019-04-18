# -*- coding: utf-8 -*-

import os
from conans import tools
from conans.errors import ConanInvalidConfiguration
from conanfile_base import FlexBase


class FlexInstaller(FlexBase):
    name = "flex_installer"
    version = FlexBase.version
    settings = "os_build", "arch_build", "compiler", "arch"

    def configure(self):
        if self.settings.os_build == "Windows":
            raise ConanInvalidConfiguration("Flex is not supported on Windows.")

    def _configure_args(self):
        return ["--disable-shared", "--disable-static", "--disable-nsl"]

    def package(self):
        super().package()
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.settings.arch_build = self.info.settings.arch
        del self.info.settings.arch
        del self.info.settings.compiler

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
