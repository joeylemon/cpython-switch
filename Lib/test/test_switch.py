import unittest
import random

class SwitchTests(unittest.TestCase):
    def test_static_case_matching(self):
        switch 1:
            case 0:
                self.fail("matched incorrect case")
            case 1:
                pass
            else:
                self.fail("matched incorrect case")

    def test_random_case_matching(self):
        switch random.randint(0, 2):
            case 0:
                pass
            case 1:
                pass
            case 2:
                pass
            else:
                self.fail("matched incorrect case")

    def test_static_else_matching(self):
        switch 1:
            case 0:
                self.fail("matched incorrect case")
            case 2:
                self.fail("matched incorrect case")
            case 3:
                self.fail("matched incorrect case")
            else:
                pass

    def test_random_else_matching(self):
        switch random.randint(0, 2):
            case 3:
                self.fail("matched incorrect case")
            case 4:
                self.fail("matched incorrect case")
            case 5:
                self.fail("matched incorrect case")
            else:
                pass

    def test_nested_stmts(self):
        switch 0:
            case 0:
                switch 0:
                    case 0:
                        return
        self.fail("no matched cases")

    def test_no_matches(self):
        switch 0:
            case 1:
                self.fail("matched incorrect case")
            case 2:
                self.fail("matched incorrect case")

    def test_switch_tuple(self):
        switch (0, 1):
            case (0, 0):
                self.fail("matched incorrect case")
            case (0, 1):
                pass
            else:
                self.fail("matched incorrect case")

    def test_switch_arr(self):
        switch [0, 0, 0, 0, 1]:
            case [0, 0, 0]:
                self.fail("matched incorrect case")
            case [0, 1]:
                self.fail("matched incorrect case")
            case [0, 0, 0]:
                self.fail("matched incorrect case")
            case [0,0,0,0,1]:
                pass
            else:
                self.fail("matched incorrect case")

    def test_switch_multiline_dict(self):
        switch {
            "a": 0,
            "b": 1
        }:
            case {
                "z": 0
            }:
                self.fail("matched incorrect case")
            case {
                "b": 1
            }:
                self.fail("matched incorrect case")
            case {
                "a": 0,
                "b": 0
            }:
                self.fail("matched incorrect case")
            case {
                "a": 0,
                "b": 1
            }:
                pass
            else:
                self.fail("matched incorrect case")

if __name__ == '__main__':
    unittest.main()