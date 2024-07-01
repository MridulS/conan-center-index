import os

from conans import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import copy, rm, rmdir


class UnitsConan(ConanFile):
    name = "llnl-units"
    license = "BSD-3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://units.readthedocs.io"
    description = (
        "A run-time C++ library for working with units "
        "of measurement and conversions between them "
        "and with string representations of units "
        "and measurements"
    )
    topics = (
        "units",
        "dimensions",
        "quantities",
        "physical-units",
        "dimensional-analysis",
        "run-time",
    )
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "base_type": ["uint32_t", "uint64_t"],
        "namespace": [None, "ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "base_type": "uint32_t",
        "namespace": None,
    }
    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["UNITS_ENABLE_TESTS"] = "OFF"
        tc.variables["UNITS_BASE_TYPE"] = self.options.base_type
        units_namespace = str(self.options.get_safe("namespace"))
        if units_namespace != "None":
            tc.variables["UNITS_NAMESPACE"] = units_namespace
        tc.variables["UNITS_BUILD_SHARED_LIBRARY"] = self.options.shared
        tc.variables["UNITS_BUILD_STATIC_LIBRARY"] = not self.options.shared
        tc.variables["UNITS_CMAKE_PROJECT_NAME"] = "LLNL-UNITS"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("*.hpp", dst="include/units", src="units/units")
        self.copy("*units.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["units"]
        self.cpp_info.set_property("cmake_file_name", "llnl-units")
        self.cpp_info.set_property("cmake_target_name", "llnl-units::units")
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "LLNL-UNITS"
        self.cpp_info.filenames["cmake_find_package_multi"] = "llnl-units"
        self.cpp_info.names["cmake_find_package"] = "LLNL-UNITS"
        self.cpp_info.names["cmake_find_package_multi"] = "llnl-units"