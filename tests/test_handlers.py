import logging
import unittest
from pathlib import Path

from pytracelog.logging.handlers import StdoutHandler, StderrHandler


class Fixtures(unittest.TestCase):
    LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

    @classmethod
    def setUpClass(cls) -> None:
        """
        Создание root логгера и адреса для логфайла.
        """
        cls.logger = logging.getLogger()
        cls.file = Path('logfile.log')

    def setUp(self) -> None:
        """
        Установка уровня логирования root логгера.
        """
        self.logger.setLevel(logging.DEBUG)

    def make_logging_in_file(self, handler: logging.StreamHandler) -> None:
        """
        Подключение обработчика к логгеру,
        перенаправление потока вывода в логфайл,
        удаление обработчика из списка обработчиков логгера.
        """
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
        """
        Чтение логфайла.
        """
        with open(self.file) as file:
            return file.read()


class TestStdoutHandler(Fixtures):
    def setUp(self) -> None:
        """
        Создание обработчика.
        """
        super().setUp()
        self.handler = StdoutHandler()

    def test_init(self):
        """
        Проверка потока вывода логгера.
        """
        self.assertEqual(
            self.handler.stream.name, '<stdout>',
            'Обработчик должен выводить логи в <stdout>')

    def test_handler_filter(self):
        """
        Проверка корректной работы фильтра обработчика.
        """
        self.make_logging_in_file(self.handler)
        logfile_content = self.read_from_logfile()

        for level in self.LOG_LEVELS[:3]:
            self.assertIn(
                level, logfile_content,
                f'Отсутствуют логи уровня {level}. Проверь фильтр обработчика'
            )

        for level in self.LOG_LEVELS[3:]:
            self.assertNotIn(
                level, logfile_content,
                f'Фильтр обработчика НЕ должен пропускать логи уровня {level}'
            )


class TestStderrHandler(Fixtures):
    def setUp(self) -> None:
        """
        Создание обработчика.
        """
        super().setUp()
        self.handler = StderrHandler()

    def test_init(self):
        """
        Проверка потока вывода логгера.
        """
        self.assertEqual(
            self.handler.stream.name,
            '<stderr>',
            'Обработчик должен выводить логи в <stderr>'
        )

    def test_handler_filter(self):
        """
        Проверка корректной работы фильтра обработчика.
        """
        self.make_logging_in_file(self.handler)
        logfile_content = self.read_from_logfile()

        for level in self.LOG_LEVELS[:3]:
            self.assertNotIn(
                level, logfile_content,
                f'Фильтр обработчика НЕ должен пропускать логи уровня {level}'
            )

        for level in self.LOG_LEVELS[3:]:
            self.assertIn(
                level, logfile_content,
                f'Отсутствуют логи уровня {level}. Проверь фильтр обработчика'
            )


if __name__ == '__main__':
    unittest.main()
