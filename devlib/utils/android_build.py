# SPDX-License-Identifier: Apache-2.0
#
# Copyright (C) 2015, ARM Limited and contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import os
from collections import namedtuple

class Build(object):
    BuildParams = namedtuple("BuildParams", "arch defconfig cross_compile")

    device_kernel_build_params = {
        'hikey960': BuildParams('arm64', 'hikey960_defconfig', 'aarch64-linux-android-'),
        'hikey': BuildParams('arm64', 'hikey_defconfig', 'aarch64-linux-android-')
    }

    """
    Collection of Android related build actions
    """
    def __init__(self, te):
        if (te.ANDROID_BUILD_TOP and te.TARGET_PRODUCT and te.TARGET_BUILD_VARIANT):
            self._te = te
        else:
            te._log.warning('Build initialization failed: invalid paramterers')
            raise

    def build_module(self, module_path):
        """
        Build a module and its dependencies.

        :param module_path: module path
        :type module_path: str

        """
        self._te._log.info('BUILDING module %s', module_path)
        cur_dir = os.getcwd()
        os.chdir(self._te.ANDROID_BUILD_TOP)
        lunch_target = self._te.TARGET_PRODUCT + '-' + self._te.TARGET_BUILD_VARIANT
        os.system('source build/envsetup.sh && lunch ' +
            lunch_target + ' && mmma -j16 ' + module_path)
        os.chdir(cur_dir)


    def build_kernel(self, kernel_path, arch, defconfig, cross_compile, clean=False):
        """
        Build kernel.

        :param kernel_path: path to kernel sources
        :type kernel_path: str

        :param arch: device architecture string used in ARCH command line parameter
        :type arch: str

        :param defconfig: defconfig file name
        :type defconfig: str

        :param cross_compile: compiler string used in CROSS_COMPILE command line parameter
        :type cross_compile: str

        :param clean: flag to clean the previous build
        :type clean: boolean

        """
        self._te._log.info('BUILDING kernel @ %s', kernel_path)
        cur_dir = os.getcwd()
        os.chdir(kernel_path)
        os.system('. ./build.config')
        if clean:
            os.system('make clean')
        os.system('make ARCH=' + arch + ' ' + defconfig)
        os.system('make -j24 ARCH=' + arch + ' CROSS_COMPILE=' + cross_compile)
        os.chdir(cur_dir)

    def build_kernel_for_device(self, kernel_path, device_name, clean):
        """
        Build kernel for specified device.

        :param kernel_path: path to kernel sources
        :type kernel_path: str

        :param device_name: device name
        :type device_name: str

        :param clean: flag to clean the previous build
        :type clean: boolean

        """
        if not device_name in self.device_kernel_build_params:
            return False

        params = self.device_kernel_build_params[device_name]
        self.build_kernel(kernel_path, params.arch,
            params.defconfig, params.cross_compile, clean)
        return True


# vim :set tabstop=4 shiftwidth=4 expandtab
