# -*- coding: utf-8 -*-

import os
from conans import AutoToolsBuildEnvironment, tools
from conans.model.version import Version
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

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            configure_args = ["--enable-shared" if self.options.shared else "--disable-shared"]
            configure_args.append("--disable-static" if self.options.shared else "--enable-static")
            configure_args.append("--disable-nls")
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
        for header in ["flexint.h", "flexdef.h", "parse.h", ""]:
            self.copy(header, dst="include", src=os.path.join(self._source_subfolder, "src"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
