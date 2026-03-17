# Copyright 2026 IBM Corporation
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0);
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# See the LICENSE file in the project root for license information.

import regex
from itertools import islice


class FormatEngine:
    EMPTY_FORMAT = "<EMPTY>"
    NA_FORMAT = "<NA>"

    @staticmethod
    def utf16_code_units(s: str):
        """
        Iterate UTF-16 code units exactly like Java char iteration.
        surrogatepass allows Java-style surrogate handling.
        """
        data = s.encode("utf-16-le", "surrogatepass")
        for i in range(0, len(data), 2):
            yield int.from_bytes(data[i : i + 2], "little")

    @staticmethod
    def is_low_surrogate(unit: int) -> bool:
        return 0xDC00 <= unit <= 0xDFFF

    @staticmethod
    def is_high_surrogate(unit: int) -> bool:
        return 0xD800 <= unit <= 0xDBFF

    @staticmethod
    def is_common_script(ch: str) -> bool:
        return regex.match(r"\p{Script=Common}", ch) is not None

    @staticmethod
    def is_ideographic(ch: str) -> bool:
        return (
            regex.match(
                r"\p{Script=Han}|\p{Script=Hiragana}|\p{Script=Katakana}|\p{Script=Hangul}",
                ch,
            )
            is not None
        )

    def get_format(self, value: str):
        if value is None:
            return None

        if value == "":
            return self.EMPTY_FORMAT

        utf16_units = list(islice(self.utf16_code_units(value), 256))
        if len(utf16_units) > 255:
            return self.NA_FORMAT

        sb = []
        i = 0
        length = len(utf16_units)

        while i < length:
            unit = utf16_units[i]

            if self.is_low_surrogate(unit):
                i += 1
                continue

            if self.is_high_surrogate(unit) and i + 1 < length:
                low = utf16_units[i + 1]
                if self.is_low_surrogate(low):
                    code_point = 0x10000 + ((unit - 0xD800) << 10) + (low - 0xDC00)
                    i += 1
                else:
                    code_point = unit
            else:
                code_point = unit

            ch = chr(code_point)

            if ch.islower():
                sb.append("a")
            elif ch.isupper():
                sb.append("A")
            elif ch.isdigit():
                sb.append("9")
            elif self.is_ideographic(ch):
                sb.append("I")
            elif (
                self.is_common_script(ch)
                and i > 0
                and self.is_ideographic(chr(utf16_units[i - 1]))
                and (i + 1 >= length or self.is_ideographic(chr(utf16_units[i + 1])))
            ):
                sb.append("I")
            else:
                sb.append(ch)

            i += 1

        return "".join(sb)
