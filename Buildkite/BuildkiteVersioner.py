#!/usr/local/autopkg/python
#
# Copyright 2017 Graham Gilbert
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

from autopkglib import Processor, ProcessorError

__all__ = ["BuildkiteVersioner"]


class BuildkiteVersioner(Processor):

    """Massages Buildkite's version numbers into something pkgbuild will take
    """

    input_variables = {
        "version": {
            "required": True,
            "description": "The version to munge"
        }
    }
    output_variables = {
        "version": {
            "description": "The cleaned version"
        },
    }
    description = __doc__

    def main(self):

        input_version = self.env["version"]
        self.output("Cleaning \"%s\"." % input_version)
        self.env["version"] = input_version.replace('-beta.', '.beta')


if __name__ == "__main__":
    processor = BuildkiteVersioner()
    processor.execute_shell()
