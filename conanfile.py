# -*- coding: utf-8 -*-

import os
from conans import tools
from conans.errors import ConanInvalidConfiguration
from conanfile_base import FlexBase


class FlexConan(FlexBase):
    name = "flex"
    version = FlexBase.version
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Flex is not supported on Windows.")
        del self.settings.compiler.libcxx

    def _configure_args(self):
        configure_args = ["--enable-shared" if self.options.shared else "--disable-shared"]
        configure_args.append("--disable-static" if self.options.shared else "--enable-static")
        configure_args.append("--disable-nls")
        return configure_args

    def package(self):
        super().package()
        for header in ["flexint.h", "flexdef.h", "parse.h", ""]:
            self.copy(header, dst="include", src=os.path.join(self._source_subfolder, "src"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
