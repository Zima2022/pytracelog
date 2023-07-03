import logging
import unittest
from pathlib import Path

from pytracelog.logging.handlers import StdoutHandler, StderrHandler


class Fixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.file = Path('logfile.log')
        self.file.touch(exist_ok=True)

    def tearDown(self) -> None:
        file = Path(self.file.name)
        file.unlink()

    def make_logging_in_file(self, handler: logging.StreamHandler) -> None:
        with open(self.file, 'w') as file:
            handler.setStream(stream=file)
            self.logger.addHandler(handler)
            self.logger.debug('DEBUG')
            self.logger.info('INFO')
            self.logger.warning('WARNING')
            self.logger.error('ERROR')
            self.logger.critical('CRITICAL')
            self.logger.removeHandler(handler)

    def read_from_logfile(self):
        with open(self.file) as file:
            return file.read()


class TestStdoutHandler(Fixtures):
    def setUp(self) -> None:
        super().setUp()
        self.handler = StdoutHandler()

    def tearDown(self) -> None:
        super().tearDown()

    def test_init(self):
        self.assertEqual(
            self.handler.stream.name, '<stdout>',
            'Обработчик должен выводить логи в <stdout>')

    def test_handler_filter(self):
        self.make_logging_in_file(self.handler)
        logfile_content = self.read_from_logfile()

        self.assertIn(
            'DEBUG', logfile_content,
            'Отсутствуют логи уровня DEBUG. Проверь фильтр обработчика'
        )
        self.assertIn(
            'INFO', logfile_content,
            'Отсутствуют логи уровня INFO. Проверь фильтр обработчика'
        )
        self.assertIn(
            'WARNING', logfile_content,
            'Отсутствуют логи уровня WARNING. Проверь фильтр обработчика'
        )
        self.assertNotIn(
            'ERROR', logfile_content,
            'Фильтр обработчика НЕ должен пропускать логи уровня ERROR'
        )
        self.assertNotIn(
            'CRITICAL', logfile_content,
            'Фильтр обработчика НЕ должен пропускать логи уровня CRITICAL'
        )


class TestStderrHandler(Fixtures):
    def setUp(self) -> None:
        super().setUp()
        self.handler = StderrHandler()

    def tearDown(self) -> None:
        super().tearDown()

    def test_init(self):
        self.assertEqual(
            self.handler.stream.name,
            '<stderr>',
            'Обработчик должен выводить логи в <stderr>'
        )

    def test_handler_filter(self):
        self.make_logging_in_file(self.handler)
        logfile_content = self.read_from_logfile()

        self.assertNotIn(
            'DEBUG', logfile_content,
            'Фильтр обработчика НЕ должен пропускать логи уровня DEBUG'
        )
        self.assertNotIn(
            'INFO', logfile_content,
            'Фильтр обработчика НЕ должен пропускать логи уровня INFO'
        )
        self.assertNotIn(
            'WARNING', logfile_content,
            'Фильтр обработчика НЕ должен пропускать логи уровня WARNING'
        )
        self.assertIn(
            'ERROR', logfile_content,
            'Отсутствуют логи уровня ERROR. Проверь фильтр обработчика'
        )
        self.assertIn(
            'CRITICAL', logfile_content,
            'Отсутствуют логи уровня CRITICAL. Проверь фильтр обработчика'
        )


if __name__ == '__main__':
    unittest.main()
