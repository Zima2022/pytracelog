import unittest
from logging import CRITICAL, DEBUG, ERROR, WARNING, makeLogRecord, root

from pytracelog.base import PyTraceLog
from pytracelog.logging.handlers import (
    StderrHandler,
    StdoutHandler,
    TracerHandler
)


class TestPyTraceLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        PyTraceLog.init_root_logger()

    def test_init_root_logger(self):
        self.assertTrue(
            root.hasHandlers(),
            'Отсутствуют обработчики root логгера'
        )
        self.assertTrue(
            root.isEnabledFor(WARNING),
            'Если не указан уровень логирования, логгер должен регистрировать логи уровня WARNING'
        )
        self.assertTrue(
            root.isEnabledFor(ERROR),
            'Если не указан уровень логирования, логгер должен регистрировать логи уровня ERROR'
        )
        self.assertTrue(
            root.isEnabledFor(CRITICAL),
            'Если не указан уровень логирования, логгер должен регистрировать логи уровня CRITICAL'
        )
        self.assertFalse(
            root.isEnabledFor(DEBUG),
            'Если не указан уровень логирования, логгер НЕ должен регистрировать логи уровня DEBUG'
        )
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
        self.log_record = makeLogRecord({'msg': 'Some message'})
        self.assertIn(
            'app_name', self.log_record.__dict__,
            'Метод extend_log_record должен добавлять статические атрибуты в объект LogRecord'
        )

    def test_init_tracer_logger(self):
        PyTraceLog.init_tracer_logger()
        self.assertTrue(
            any(isinstance(h, TracerHandler) for h in root.handlers),
            'Отсутствует TracerHandler в списке обработчиков root логгера'
        )
        PyTraceLog.init_tracer_logger()
        self.assertEqual(
            len(root.handlers), 3,
            'Если в списке обработчиков уже есть TracerHandler, его не надо добавлять'
        )

    def test_reset(self):
        PyTraceLog.reset()
        self.assertTrue(
            root.isEnabledFor(WARNING),
            'При сбросе настроек установить уровень логирования WARNING'
        )
        self.assertEqual(
            len(root.handlers), 0,
            ('При сбросе настроек должны удалятся обработчики ' +
             'StderrHandler, StdoutHandler, TracerHandler из списка root логгера')
        )
        self.assertIsNone(
            PyTraceLog._old_factory,
            'Надо сбросить настройки фабрики для создания объектов LogRecord'
        )


if __name__ == '__main__':
    unittest.main()
