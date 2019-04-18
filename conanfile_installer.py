#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import AutoToolsBuildEnvironment, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration
from conanfile_base import FlexBase


class FlexInstaller(FlexBase):
    name = "flex_installer"
    version = FlexBase.version
    settings = "os_build", "arch_build", "compiler"

    def configure(self):
        if self.settings.os_build == "Windows":
            raise ConanInvalidConfiguration("Flex is not supported on Windows.")

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            configure_args = ["--disable-shared", "--disable-static", "--disable-nls"]
            if str(self.settings.compiler) == "gcc" and Version(self.settings.compiler.version.value) >= "6":
                configure_args.append("ac_cv_func_reallocarray=no")
            if tools.cross_building(self.settings):
                with tools.chdir(self._source_subfolder):
                    # stage1flex must be built on native arch: https://github.com/westes/flex/issues/78
                    self.run("./configure %s" % " ".join(configure_args))
                    self._autotools.make(args=["-C", "src", "stage1flex"])
                    os.rename(os.path.join("src", "stage1flex"), os.path.join("src", "stage1flex.build"))
                    self._autotools.make(args=["distclean"])
                    with tools.environment_append(self._autotools.vars):
                        self._autotools.configure(args=configure_args)
                        cpu_count_option = "-j%s" % tools.cpu_count()
                        self.run("make -C src %s || true" % cpu_count_option)
                        os.rename(os.path.join("src", "stage1flex.build"), os.path.join("src", "stage1flex"))
                        open(os.path.join("src", "stage1flex"), 'a').close()
                        self._autotools.make(args=["-C", "src"])
            else:
                with tools.environment_append(self._autotools.vars):
                    self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def package(self):
        super().package()
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
