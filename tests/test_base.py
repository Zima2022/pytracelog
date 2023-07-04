import unittest
from logging import root, DEBUG, WARNING, ERROR, CRITICAL, makeLogRecord

from pytracelog.base import PyTraceLog
from pytracelog.logging.handlers import StdoutHandler, StderrHandler


class TestPyTraceLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        PyTraceLog.init_root_logger()

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

    def test_extend_log_record(self):
        PyTraceLog.extend_log_record(app_name='my_app')
        self.log_record = makeLogRecord({'msg': 'LogRecord object'})
        self.assertIn(
            'app_name', self.log_record.__dict__,
            'Метод extend_log_record должен добавлять статические атрибуты в объект LogRecord'
        )


if __name__ == '__main__':
    unittest.main()
