#
# Copyright 2015 Naver Corp.
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
#

import basic_op_capi
import util

class TestBasicOpCAPI64(basic_op_capi.TestBasicOpCAPI):
    arch = 64
    def test_basic_op_capi(self):
        util.print_frame()
        basic_op_capi.TestBasicOpCAPI.test_basic_op_capi(self)
