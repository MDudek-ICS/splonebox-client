"""
This file is part of the splonebox python client library.

The splonebox python client library is free software: you can
redistribute it and/or modify it under the terms of the GNU Lesser
General Public License as published by the Free Software Foundation,
either version 3 of the License or any later version.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this splonebox python client library.  If not,
see <http://www.gnu.org/licenses/>.

"""

import unittest

from splonebox.api.result import RemoteError, RunResult


class ResultTest(unittest.TestCase):
    def test_run_result(self):
        res = RunResult()

        self.assertEqual(res.get_status(), 0)
        self.assertIsNone(res.get_id())
        self.assertIsNone(res.get_result(blocking=False))
        self.assertFalse(res.has_result())

        res.set_id(42)
        self.assertTrue(res.was_exec())
        self.assertEqual(res.get_id(), 42)
        self.assertFalse(res.has_result())
        self.assertEqual(res.get_status(), 1)

        res.set_result([0])
        self.assertTrue(res.was_exec())
        self.assertTrue(res.has_result())
        self.assertEqual(res.get_status(), 2)
        self.assertEqual(res.get_result(), [0])

        res = RunResult()
        res.set_error([0, "err"])
        with self.assertRaises(RemoteError):
            res.get_result()
        self.assertEqual(res.get_status(), -1)

        pass
