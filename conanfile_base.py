# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools


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



    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))