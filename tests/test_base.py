import unittest
from logging import root, DEBUG, WARNING, ERROR, CRITICAL

from pytracelog.base import PyTraceLog
from pytracelog.logging.handlers import StdoutHandler, StderrHandler


class TestPyTraceLog(unittest.TestCase):
    def setUp(self) -> None:
        self.level = WARNING
        PyTraceLog.init_root_logger(self.level)

    def test_init_root_logger(self):
        self.assertTrue(
            root.hasHandlers(),
            'Отсутствуют обработчики root логгера'
        )
        self.assertTrue(root.isEnabledFor(WARNING))
        self.assertTrue(root.isEnabledFor(ERROR))
        self.assertTrue(root.isEnabledFor(CRITICAL))
        self.assertFalse(root.isEnabledFor(DEBUG))
        self.assertEqual(
            len(root.handlers), 2,
            'У root логгера должно быть два обработчика'
        )
        self.assertTrue(
            any(isinstance(h, StdoutHandler) for h in root.handlers),
            'Отсутствует StdoutHandler в списке обработчиков root логгера'
        )
        self.assertTrue(
            any(isinstance(h, StderrHandler) for h in root.handlers),
            'Отсутствует StdoutHandler в списке обработчиков root логгера'
        )


if __name__ == '__main__':
    unittest.main()
