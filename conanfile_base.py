# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.model.version import Version


class FlexBase(ConanFile):
    version = "2.6.4"
    url = "https://github.com/bincrafters/conan-flex"
    homepage = "https://github.com/westes/flex"
    description = "Flex, the fast lexical analyzer generator"
    license = "BSD-2-Clause"
    author = "Bincrafters <bincrafters@gmail.com>"
    topics = ("conan", "flex", "lexical-analyzer", "lexical-analyzer-generator")
    exports = ["LICENSE.md", os.path.basename(__file__)]
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        sha256 = "e87aae032bf07c26f85ac0ed3250998c37621d95f8bd748b31f15b33c45ee995"
        tools.get("{}/releases/download/v{version}/flex-{version}.tar.gz".format(self.homepage, version=self.version), sha256=sha256)
        extracted_dir = "flex-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            configure_args = self._configure_args()
            if str(self.settings.compiler) == "gcc" and Version(self.settings.compiler.version.value) >= "6":
                configure_args.append("ac_cv_func_reallocarray=no")
            if tools.cross_building(self.settings):
                # stage1flex must be built on native arch: https://github.com/westes/flex/issues/78
                self.run("%s/configure %s" % (self._source_subfolder, " ".join(configure_args)))
                self._autotools.make(args=["-C", "src", "stage1flex"])
                os.rename(os.path.join("src", "stage1flex"), os.path.join("src", "stage1flex.build"))
                self._autotools.make(args=["distclean"])
                with tools.environment_append(self._autotools.vars):
                    self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
                    cpu_count_option = "-j%s" % tools.cpu_count()
                    self.run("make -C src %s || true" % cpu_count_option)
                    os.rename(os.path.join("src", "stage1flex.build"), os.path.join("src", "stage1flex"))
                    open(os.path.join("src", "stage1flex"), 'a').close()
            else:
                with tools.environment_append(self._autotools.vars):
                    self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        args = ["-C","src"] if tools.cross_building(self.settings) else None
        autotools = self._configure_autotools()
        autotools.make(args=args)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))