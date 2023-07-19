import logging
import unittest
from pathlib import Path
from unittest.mock import patch

from pytracelog.logging.handlers import (
    StdoutHandler,
    StderrHandler,
    TracerHandler,
)

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
LOGGING_LEVEL = 3


class Fixtures(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        Создание root логгера и адреса для логфайла.
        """
        cls.logger = logging.getLogger()
        cls.file = Path('logfile.log')

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Удаление логфайла, использованного для тестирования.
        """
        Path.unlink(cls.file)

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
            'Обработчик НЕ выводить логи в <stdout>')

    def test_handler_filter(self):
        """
        Проверка корректной работы фильтра обработчика.
        """
        self.make_logging_in_file(self.handler)
        logfile_content = self.read_from_logfile()

        for level in LOG_LEVELS[:LOGGING_LEVEL]:
            self.assertIn(
                level, logfile_content,
                f'Отсутствуют логи уровня {level}. Проверь фильтр обработчика'
            )

        for level in LOG_LEVELS[LOGGING_LEVEL:]:
            self.assertNotIn(
                level, logfile_content,
                f'Фильтр обработчика работает некорректно: пропускать логи уровня {level}'
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
            'Обработчик НЕ выводить логи в <stderr>'
        )

    def test_handler_filter(self):
        """
        Проверка корректной работы фильтра обработчика.
        """
        self.make_logging_in_file(self.handler)
        logfile_content = self.read_from_logfile()

        for level in LOG_LEVELS[:LOGGING_LEVEL]:
            self.assertNotIn(
                level, logfile_content,
                f'Фильтр обработчика работает некорректно: пропускать логи уровня {level}'
            )

        for level in LOG_LEVELS[LOGGING_LEVEL:]:
            self.assertIn(
                level, logfile_content,
                f'Отсутствуют логи уровня {level}. Проверь фильтр обработчика'
            )


class TestTracerHandler(unittest.TestCase):
    @patch('pytracelog.logging.handlers.get_current_span')
    def test_emit(self, span_mock):
        """
        Проверка отправки журнала в систему трассировки.
        """
        record_warning = logging.makeLogRecord(
            dict(
                msg='Test logging message',
                levelno=logging.WARNING,
            )
        )
        TracerHandler().emit(record=record_warning)
        span_mock().set_status.assert_not_called()

        record_error = logging.makeLogRecord(
            dict(
                msg='Test logging message',
                levelno=logging.ERROR,
            )
        )
        TracerHandler().emit(record=record_error)
        span_mock().set_status.assert_called()
        span_mock().add_event.assert_called_with(
            name=record_error.msg,
            attributes=TracerHandler().get_record_attrs(record=record_error)
        )

    def test_get_record_attrs(self):
        """
        Проверка формирования справочника атрибутов записи.
        """
        record = logging.makeLogRecord(
            dict(
                msg='Test logging message',
                levelno=logging.ERROR,
            )
        )

        attrs = TracerHandler().get_record_attrs(record=record)
        self.assertTrue(
            all(attrs.values()),
            'Удалить ключи с пустыми значениями в справочнике атрибутов записи'
        )

        attributes_to_delete = (
            'name',
            'exc_info',
            'exc_text',
            'msecs',
            'relativeCreated',
            'otelSpanID',
            'otelTraceID',
            'otelServiceName'
        )
        for attr in attributes_to_delete:
            self.assertNotIn(
                attr, attrs,
                f'Удалить атрибут {attr} из справочника атрибутов записи'
            )

        attrs = TracerHandler().get_record_attrs(
            record=record,
            remove_msg=False,
            message_attr_name='some message'
        )
        self.assertIn(
            'some message', attrs,
            "Отсутствует атрибут 'message_attr_name' в справочнике атрибутов записи"
        )
        self.assertEqual(
            attrs.get('some message'), 'Test logging message',
            "Если remove_msg=False, атрибут 'msg'" +
            "переименовать в соответствии со значением параметра 'message_attr_name'"
        )


if __name__ == '__main__':
    unittest.main()
