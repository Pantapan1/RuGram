import sys
import re
import requests
import time
import json
from typing import Callable, Any

ЗАМЕНЫ = {
    'если': 'if',
    'или': 'or',
    'иначе': 'else',
    'пока': 'while',
    'для': 'for',
    'в': 'in',
    'из': 'import',
    'как': 'as',
    'с': 'with',
    'попробовать': 'try',
    'кроме': 'except',
    'finally': 'finally',
    'поднять': 'raise',
    'класс': 'class',
    'функция': 'def',
    'возврат': 'return',
    'выход': 'break',
    'продолжить': 'continue',
    'пройти': 'pass',
    'ничего': 'None',
    'истина': 'True',
    'ложь': 'False',
    'печать': 'print',
    'длина': 'len',
    'ввод': 'input',
    'строка': 'str',
    'число': 'int',
    'РуГрам': 'RuGram',
    'сказать': 'send',
    'слушать': 'listen',
    'не': 'not',
    'и': 'and',
    'сам': 'self',
    'список': 'list',
    'словарь': 'dict',
    'множество': 'set',
    'кортеж': 'tuple',
    'диапазон': 'range',
    'перечислить': 'enumerate',
    'соединить': 'zip',
    'открыть': 'open',
    'записать': 'write',
    'читать': 'read',
    'сумма': 'sum',
    'макс': 'max',
    'мин': 'min',
    'сортировать': 'sorted',
    'фильтр': 'filter',
    'карта': 'map',
    'любой': 'any',
    'все': 'all',
    'тип': 'type',
    'экземпляр': 'isinstance',
    'наследник': 'issubclass',
    'вызвать': 'callable',
    'получить': 'getattr',
    'установить': 'setattr',
    'имеет': 'hasattr',
    'удалить': 'delattr',
    'модуль': '__import__',
    'округлить': 'round',
    'абс': 'abs',
    'степень': 'pow',
    'деление': 'divmod',
    'шестнадцать': 'hex',
    'восемь': 'oct',
    'двоичный': 'bin',
    'представить': 'repr',
    'формат': 'format',
    'помощь': 'help',
    'каталог': 'dir',
    'идентификатор': 'id',
    'хэш': 'hash',
    'память': 'memoryview',
    'байты': 'bytes',
    'байтмассив': 'bytearray',
    'асинх': 'async',
    'ждать': 'await',
    'задача': 'Task',
    'корутина': 'coroutine',
    'генератор': 'generator',
    'итератор': 'iterator',
    'контекст': 'contextmanager',
    'свойство': 'property',
    'статический': 'staticmethod',
    'классметод': 'classmethod',
    'абстрактный': 'abstractmethod',
    'окончательно': 'final',
    'перегрузка': 'overload',
    'сообщение': 'message',
    'чат': 'chat',
    'пользователь': 'user',
    'команда': 'command',
    'текст': 'text',
    'отправить': 'send_message',
    'ответить': 'reply_to',
    'переслать': 'forward_message',
    'копировать': 'copy_message',
    'удалить_сообщение': 'delete_message',
    'редактировать': 'edit_message_text',
    'фото': 'photo',
    'видео': 'video',
    'аудио': 'audio',
    'документ': 'document',
    'стикер': 'sticker',
    'опрос': 'poll',
    'локация': 'location',
    'контакт': 'contact',
    'клавиатура': 'keyboard',
    'кнопка': 'button',
    'меню': 'menu',
    'инлайн': 'inline',
    'обратный_вызов': 'callback',
    'запрос': 'callback_query',
    'уведомление': 'answer_callback_query',
    'чат_действие': 'send_chat_action',
    'печатает': 'typing',
    'загружает_фото': 'upload_photo',
    'загружает_видео': 'upload_video',
    'загружает_аудио': 'upload_audio',
    'загружает_документ': 'upload_document',
    'выбирает_локацию': 'find_location',
    'записывает_видео': 'record_video',
    'записывает_голос': 'record_voice',
    'ограничения': 'restrictions',
    'права': 'permissions',
    'администратор': 'administrator',
    'создатель': 'creator',
    'участник': 'member',
    'покинул': 'left',
    'заблокирован': 'kicked',
    'вебхук': 'webhook',
    'опрос_сервера': 'polling',
    'сервер': 'server',
    'маршрут': 'route',
    'запрос_от': 'request',
    'ответ_на': 'response',
    'заголовки': 'headers',
    'тело': 'body',
    'статус': 'status',
    'успешно': 'ok',
    'ошибка': 'error',
    'токен': 'token',
    'секрет': 'secret',
    'ключ': 'key',
    'значение': 'value',
    'данные': 'data',
    'файл': 'file',
    'путь': 'path',
    'имя': 'name',
    'расширение': 'extension',
    'размер': 'size',
    'дата': 'date',
    'время_отправки': 'date',
    'редактирования': 'edit_date',
    'пересылки': 'forward_date',
    'подпись': 'caption',
    'сущности': 'entities',
    'ссылка': 'url',
    'предпросмотр': 'preview',
    'уведомление_о': 'disable_notification',
    'защита': 'protect_content',
    'ответ_на_сообщение': 'reply_to_message_id',
    'разрешённые': 'allow_sending_without_reply',
    'разметка': 'parse_mode',
    'HTML': 'HTML',
    'Маркдаун': 'MarkdownV2',
    'смещение': 'offset',
    'предел': 'limit',
    'таймаут': 'timeout',
    'повторы': 'retries',
    'задержка': 'sleep',
    'логирование': 'logging',
    'уровень': 'level',
    'отладка': 'debug',
    'инфо': 'info',
    'предупреждение': 'warning',
    'критическое': 'critical',
    'обработчик': 'handler',
    'диспетчер': 'dispatcher',
    'фильтр': 'filter',
    'состояние': 'state',
    'контекст_пользователя': 'user_context',
    'память_бота': 'bot_memory',
    'очередь': 'queue',
    'задача_в_фоне': 'background_task',
    'расписание': 'schedule',
    'интервал': 'interval',
    'повтор': 'repeat',
    'единожды': 'once',
    'сейчас': 'now',
    'сегодня': 'today',
    'завтра': 'tomorrow',
    'вчера': 'yesterday',
    'утро': 'morning',
    'день': 'afternoon',
    'вечер': 'evening',
    'ночь': 'night',
    'час': 'hour',
    'минута': 'minute',
    'секунда': 'second',
    'миллисекунда': 'millisecond',
    'неделя': 'week',
    'месяц': 'month',
    'год': 'year',
    'весна': 'spring',
    'лето': 'summer',
    'осень': 'autumn',
    'зима': 'winter',
    'понедельник': 'monday',
    'вторник': 'tuesday',
    'среда': 'wednesday',
    'четверг': 'thursday',
    'пятница': 'friday',
    'суббота': 'saturday',
    'воскресенье': 'sunday',
    'январь': 'january',
    'февраль': 'february',
    'март': 'march',
    'апрель': 'april',
    'май': 'may',
    'июнь': 'june',
    'июль': 'july',
    'август': 'august',
    'сентябрь': 'september',
    'октябрь': 'october',
    'ноябрь': 'november',
    'декабрь': 'december',
    'цвет': 'color',
    'красный': 'red',
    'зелёный': 'green',
    'синий': 'blue',
    'жёлтый': 'yellow',
    'чёрный': 'black',
    'белый': 'white',
    'серый': 'gray',
    'прозрачный': 'transparent',
    'шрифт': 'font',
    'жирный': 'bold',
    'курсив': 'italic',
    'подчёркнутый': 'underline',
    'зачёркнутый': 'strikethrough',
    'код_в_строке': 'code',
    'блок_кода': 'pre',
    'спойлер': 'spoiler',
    'цитата': 'blockquote',
    'ссылка_текст': 'text_link',
    'ссылка_упоминание': 'text_mention',
    'хэштег': 'hashtag',
    'упоминание': 'mention',
    'бот_команда': 'bot_command',
    'эмодзи': 'emoji',
    'стикер_эмодзи': 'custom_emoji',
    'анимация': 'animation',
    'видеозаметка': 'video_note',
    'голосовое': 'voice',
    'видеосообщение': 'video_message',
    'альбом': 'media_group',
    'медиа': 'media',
    'файл_ввода': 'input_file',
    'файл_с_диска': 'file_from_disk',
    'файл_из_сети': 'file_from_url',
    'миниатюра': 'thumbnail',
    'ширина': 'width',
    'высота': 'height',
    'продолжительность': 'duration',
    'исполнитель': 'performer',
    'название': 'title',
    'тип_файла': 'mime_type',
    'идентификатор_файла': 'file_id',
    'уникальный_ид': 'file_unique_id',
    'вес': 'file_size',
    'битрейт': 'bitrate',
    'частота': 'frequency',
    'каналы': 'channels',
    'сэмплов': 'sample_rate',
    'разрешение': 'resolution',
    'кадры': 'fps',
    'кодек': 'codec',
    'контейнер': 'container',
    'поддержка_стриминга': 'supports_streaming',
    'премиум': 'premium',
    'обычный': 'regular',
    'админ': 'admin',
    'владелец': 'owner',
    'модератор': 'moderator',
    'ограниченный': 'restricted',
    'бан': 'banned',
    'мут': 'muted',
    'размут': 'unmuted',
    'разбан': 'unbanned',
    'пригласить': 'invite',
    'выгнать': 'kick',
    'забанить': 'ban',
    'разбанить': 'unban',
    'назначить_админа': 'promote',
    'понизить_админа': 'demote',
    'настройки_чата': 'chat_settings',
    'описание': 'description',
    'пригласительная_ссылка': 'invite_link',
    'закреплённое': 'pinned_message',
    'открепить': 'unpin',
    'закрепить': 'pin',
    'медленный_режим': 'slow_mode',
    'секретный_чат': 'secret_chat',
    'супергруппа': 'supergroup',
    'канал': 'channel',
    'группа': 'group',
    'приватный': 'private',
    'публичный': 'public',
    'верифицированный': 'verified',
    'поддержка': 'support',
    'скам': 'scam',
    'фейк': 'fake',
    'официальный': 'official',
    'удалённый': 'deleted',
    'активный': 'active',
    'неактивный': 'inactive',
    'онлайн': 'online',
    'офлайн': 'offline',
    'был_недавно': 'recently',
    'был_на_неделе': 'within_week',
    'был_в_месяц': 'within_month',
    'давно': 'long_ago',
    'скрытый': 'hidden',
    'видимый': 'visible',
    'доступный': 'available',
    'недоступный': 'unavailable',
    'занят': 'busy',
    'свободен': 'free',
    'на_связи': 'available',
    'отошёл': 'away',
    'не_беспокоить': 'do_not_disturb',
    'готов_к_работе': 'ready',
    'загрузка': 'loading',
    'обработка': 'processing',
    'готово': 'done',
    'завершено': 'completed',
    'отменено': 'cancelled',
    'приостановлено': 'paused',
    'возобновлено': 'resumed',
    'запущено': 'started',
    'остановлено': 'stopped',
    'перезапущено': 'restarted',
    'подключено': 'connected',
    'отключено': 'disconnected',
    'переподключение': 'reconnecting',
    'ожидание': 'waiting',
    'получение': 'receiving',
    'отправка': 'sending',
    'загрузка_файла': 'uploading',
    'скачивание': 'downloading',
    'синхронизация': 'synchronizing',
    'обновление': 'updating',
    'установка': 'installing',
    'удаление': 'deleting',
    'перемещение': 'moving',
    'копирование': 'copying',
    'создание': 'creating',
    'открытие': 'opening',
    'закрытие': 'closing',
    'сохранение': 'saving',
    'чтение_файла': 'reading',
    'запись_файла': 'writing',
    'сжатие': 'compressing',
    'распаковка': 'extracting',
    'шифрование': 'encrypting',
    'дешифрование': 'decrypting',
    'хеширование': 'hashing',
    'проверка': 'verifying',
    'валидация': 'validating',
    'форматирование': 'formatting',
    'парсинг': 'parsing',
    'сериализация': 'serializing',
    'десериализация': 'deserializing',
    'кодирование': 'encoding',
    'декодирование': 'decoding',
    'конвертация': 'converting',
    'трансформация': 'transforming',
    'генерация': 'generating',
    'вычисление': 'calculating',
    'анализ': 'analyzing',
    'поиск': 'searching',
    'сортировка': 'sorting',
    'фильтрация': 'filtering',
    'группировка': 'grouping',
    'агрегация': 'aggregating',
    'нормализация': 'normalizing',
    'стандартизация': 'standardizing',
    'оптимизация': 'optimizing',
    'минификация': 'minifying',
    'обфускация': 'obfuscating',
    'красивая_печать': 'pretty_print',
    'логирование_в_файл': 'file_logging',
    'логирование_в_консоль': 'console_logging',
    'ротация_логов': 'log_rotation',
    'архивация_логов': 'log_archiving',
    'очистка_логов': 'log_cleaning',
    'уровень_логирования': 'log_level',
    'формат_лога': 'log_format',
    'временная_метка': 'timestamp',
    'сообщение_лога': 'log_message',
    'контекст_лога': 'log_context',
    'трассировка': 'traceback',
    'стек_вызовов': 'call_stack',
    'исключение': 'exception',
    'предупреждение_системы': 'system_warning',
    'ошибка_системы': 'system_error',
    'критическая_ошибка': 'system_critical',
    'фатальная_ошибка': 'fatal_error',
    'восстановление': 'recovery',
    'откат': 'rollback',
    'фиксация': 'commit',
    'транзакция': 'transaction',
    'блокировка': 'lock',
    'разблокировка': 'unlock',
    'семафор': 'semaphore',
    'мьютекс': 'mutex',
    'монитор': 'monitor',
    'синхронизированный': 'synchronized',
    'атомарный': 'atomic',
    'поток': 'thread',
    'процесс': 'process',
    'пул_потоков': 'thread_pool',
    'пул_процессов': 'process_pool',
    'исполнитель': 'executor',
    'будущее': 'future',
    'обещание': 'promise',
    'отложенный': 'deferred',
    'колбэк': 'callback',
    'событие': 'event',
    'слушатель': 'listener',
    'издатель': 'publisher',
    'подписчик': 'subscriber',
    'наблюдатель': 'observer',
    'посредник': 'mediator',
    'фасад': 'facade',
    'прокси': 'proxy',
    'декоратор_класса': 'decorator',
    'адаптер': 'adapter',
    'мост': 'bridge',
    'компоновщик': 'composite',
    'легковес': 'flyweight',
    'стратегия': 'strategy',
    'состояние_объекта': 'state_pattern',
    'команда_паттерн': 'command_pattern',
    'цепочка_обязанностей': 'chain_of_responsibility',
    'итератор_паттерн': 'iterator_pattern',
    'посетитель': 'visitor',
    'хранитель': 'memento',
    'прототип': 'prototype',
    'одиночка': 'singleton',
    'фабрика': 'factory',
    'абстрактная_фабрика': 'abstract_factory',
    'строитель': 'builder',
    'пул_объектов': 'object_pool',
    'сервис': 'service',
    'репозиторий': 'repository',
    'контроллер': 'controller',
    'модель': 'model',
    'представление': 'view',
    'шаблон': 'template',
    'статический_файл': 'static_file',
    'медиа_файл': 'media_file',
    'кеш': 'cache',
    'сессия': 'session',
    'куки': 'cookie',
    'заголовок': 'header',
    'параметр': 'parameter',
    'аргумент': 'argument',
    'переменная': 'variable',
    'константа': 'constant',
    'функция_обратного_вызова': 'callback_function',
    'лямбда': 'lambda',
    'замыкание': 'closure',
    'декоратор_функции': 'wrapper',
    'рекурсия': 'recursion',
    'итерация': 'iteration',
    'композиция': 'composition',
    'наследование': 'inheritance',
    'инкапсуляция': 'encapsulation',
    'полиморфизм': 'polymorphism',
    'абстракция': 'abstraction',
    'интерфейс': 'interface',
    'реализация': 'implementation',
    'экземпляр_класса': 'instance',
    'объект': 'object',
    'метод': 'method',
    'атрибут': 'attribute',
    'поле': 'field',
    'свойство_класса': 'class_property',
    'конструктор': 'constructor',
    'деструктор': 'destructor',
    'инициализация': 'initialization',
    'финализация': 'finalization',
    'сериализация_объекта': 'object_serialization',
    'клонирование': 'cloning',
    'сравнение': 'comparison',
    'равенство': 'equality',
    'идентичность': 'identity',
    'подобие': 'similarity',
    'различие': 'difference',
    'совпадение': 'match',
    'поиск_совпадений': 'pattern_matching',
    'сопоставление': 'mapping',
    'преобразование': 'conversion',
    'приведение_типов': 'type_casting',
    'проверка_типа': 'type_checking',
    'аннотация_типа': 'type_annotation',
    'подсказка_типа': 'type_hint',
    'обобщение': 'generic',
    'параметризация': 'parameterization',
    'специализация': 'specialization',
    'инстанциирование': 'instantiation',
    'вызов_функции': 'function_call',
    'возврат_значения': 'return_value',
    'передача_параметров': 'parameter_passing',
    'именованный_аргумент': 'keyword_argument',
    'позиционный_аргумент': 'positional_argument',
    'значение_по_умолчанию': 'default_value',
    'переменное_число_аргументов': 'variable_arguments',
    'распаковка_аргументов': 'argument_unpacking',
    'частичное_применение': 'partial_application',
    'каррирование': 'currying',
    'мемоизация': 'memoization',
    'декорирование': 'decoration',
    'обёртка': 'wrapping',
    'развёртка': 'unwrapping',
    'вложение': 'nesting',
    'вложенная_функция': 'nested_function',
    'внутренняя_функция': 'inner_function',
    'внешняя_функция': 'outer_function',
    'глобальная_переменная': 'global_variable',
    'локальная_переменная': 'local_variable',
    'нелокальная_переменная': 'nonlocal_variable',
    'пространство_имён': 'namespace',
    'область_видимости': 'scope',
    'время_жизни': 'lifetime',
    'сборщик_мусора': 'garbage_collector',
    'подсчёт_ссылок': 'reference_counting',
    'циклическая_ссылка': 'circular_reference',
    'слабая_ссылка': 'weak_reference',
    'сильная_ссылка': 'strong_reference',
    'владелец_ресурса': 'resource_owner',
    'менеджер_контекста': 'context_manager'
}

class RuGram:
    def __init__(self, token):
        self.token = token
        self.api = f"https://api.telegram.org/bot{token}"
        self.handlers = []
        self.error_handlers = []
        self.middlewares = []
        self._running = False
    
    def __setitem__(self, chat_id, text):
        self.send(chat_id, text)
    
    def __getitem__(self, chat_id):
        return Chat(chat_id, self)
    
    def on(self, command=None, text=None, regex=None, content_type=None):
        def wrapper(func):
            self.handlers.append({
                'command': command,
                'text': text,
                'regex': regex,
                'content_type': content_type,
                'func': func
            })
            return func
        return wrapper
    
    def on_error(self, func):
        self.error_handlers.append(func)
        return func
    
    def use(self, middleware):
        self.middlewares.append(middleware)
        return middleware
    
    def send(self, chat_id, text, parse_mode=None, reply_markup=None, disable_notification=False):
        data = {
            'chat_id': chat_id,
            'text': text,
            'disable_notification': disable_notification
        }
        if parse_mode:
            data['parse_mode'] = parse_mode
        if reply_markup:
            data['reply_markup'] = reply_markup.to_json()
        return requests.post(f"{self.api}/sendMessage", json=data).json()
    
    def reply(self, message, text, parse_mode=None, reply_markup=None):
        return self.send(message.chat.id, text, parse_mode, reply_markup)
    
    def send_photo(self, chat_id, photo, caption=None, reply_markup=None):
        data = {'chat_id': chat_id, 'photo': photo}
        if caption:
            data['caption'] = caption
        if reply_markup:
            data['reply_markup'] = reply_markup.to_json()
        return requests.post(f"{self.api}/sendPhoto", json=data).json()
    
    def send_document(self, chat_id, document, caption=None):
        data = {'chat_id': chat_id, 'document': document}
        if caption:
            data['caption'] = caption
        return requests.post(f"{self.api}/sendDocument", json=data).json()
    
    def send_sticker(self, chat_id, sticker):
        return requests.post(f"{self.api}/sendSticker", json={
            'chat_id': chat_id, 'sticker': sticker
        }).json()
    
    def send_poll(self, chat_id, question, options, is_anonymous=True):
        return requests.post(f"{self.api}/sendPoll", json={
            'chat_id': chat_id,
            'question': question,
            'options': options,
            'is_anonymous': is_anonymous
        }).json()
    
    def send_location(self, chat_id, latitude, longitude):
        return requests.post(f"{self.api}/sendLocation", json={
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude
        }).json()
    
    def send_contact(self, chat_id, phone_number, first_name):
        return requests.post(f"{self.api}/sendContact", json={
            'chat_id': chat_id,
            'phone_number': phone_number,
            'first_name': first_name
        }).json()
    
    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text
        }
        if reply_markup:
            data['reply_markup'] = reply_markup.to_json()
        return requests.post(f"{self.api}/editMessageText", json=data).json()
    
    def delete_message(self, chat_id, message_id):
        return requests.post(f"{self.api}/deleteMessage", json={
            'chat_id': chat_id, 'message_id': message_id
        }).json()
    
    def forward_message(self, chat_id, from_chat_id, message_id):
        return requests.post(f"{self.api}/forwardMessage", json={
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id
        }).json()
    
    def send_chat_action(self, chat_id, action):
        return requests.post(f"{self.api}/sendChatAction", json={
            'chat_id': chat_id, 'action': action
        }).json()
    
    def get_chat(self, chat_id):
        return requests.post(f"{self.api}/getChat", json={'chat_id': chat_id}).json()
    
    def get_chat_member(self, chat_id, user_id):
        return requests.post(f"{self.api}/getChatMember", json={
            'chat_id': chat_id, 'user_id': user_id
        }).json()
    
    def kick_chat_member(self, chat_id, user_id):
        return requests.post(f"{self.api}/kickChatMember", json={
            'chat_id': chat_id, 'user_id': user_id
        }).json()
    
    def unban_chat_member(self, chat_id, user_id):
        return requests.post(f"{self.api}/unbanChatMember", json={
            'chat_id': chat_id, 'user_id': user_id
        }).json()
    
    def restrict_chat_member(self, chat_id, user_id, permissions):
        return requests.post(f"{self.api}/restrictChatMember", json={
            'chat_id': chat_id,
            'user_id': user_id,
            'permissions': permissions
        }).json()
    
    def promote_chat_member(self, chat_id, user_id, **kwargs):
        data = {'chat_id': chat_id, 'user_id': user_id, **kwargs}
        return requests.post(f"{self.api}/promoteChatMember", json=data).json()
    
    def set_chat_photo(self, chat_id, photo):
        return requests.post(f"{self.api}/setChatPhoto", json={
            'chat_id': chat_id, 'photo': photo
        }).json()
    
    def delete_chat_photo(self, chat_id):
        return requests.post(f"{self.api}/deleteChatPhoto", json={'chat_id': chat_id}).json()
    
    def set_chat_title(self, chat_id, title):
        return requests.post(f"{self.api}/setChatTitle", json={
            'chat_id': chat_id, 'title': title
        }).json()
    
    def set_chat_description(self, chat_id, description):
        return requests.post(f"{self.api}/setChatDescription", json={
            'chat_id': chat_id, 'description': description
        }).json()
    
    def pin_chat_message(self, chat_id, message_id):
        return requests.post(f"{self.api}/pinChatMessage", json={
            'chat_id': chat_id, 'message_id': message_id
        }).json()
    
    def unpin_chat_message(self, chat_id):
        return requests.post(f"{self.api}/unpinChatMessage", json={'chat_id': chat_id}).json()
    
    def answer_callback(self, callback_query_id, text=None, show_alert=False):
        data = {
            'callback_query_id': callback_query_id,
            'show_alert': show_alert
        }
        if text:
            data['text'] = text
        return requests.post(f"{self.api}/answerCallbackQuery", json=data).json()
    
    def _process_middlewares(self, update, handler):
        context = {}
        for middleware in self.middlewares:
            result = middleware(update, context)
            if result is False:
                return False
        return True
    
    def run(self, skip_updates=True):
        self._running = True
        offset = None
        
        while self._running:
            try:
                params = {'timeout': 30}
                if offset:
                    params['offset'] = offset
                
                updates = requests.get(f"{self.api}/getUpdates", params=params).json()
                
                if not updates.get('ok'):
                    continue
                
                for update in updates['result']:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        msg = Message(update['message'])
                        
                        for handler in self.handlers:
                            if not self._process_middlewares(update, handler):
                                continue
                            
                            match = False
                            
                            if handler['command'] and msg.text:
                                if msg.text.startswith(f"/{handler['command']}"):
                                    match = True
                            
                            if handler['text'] and msg.text:
                                if handler['text'] in msg.text:
                                    match = True
                            
                            if handler['regex'] and msg.text:
                                if re.search(handler['regex'], msg.text):
                                    match = True
                            
                            if handler['content_type'] and msg.content_type:
                                if msg.content_type == handler['content_type']:
                                    match = True
                            
                            if match:
                                handler['func'](self, msg)
                    
                    elif 'callback_query' in update:
                        cb = CallbackQuery(update['callback_query'])
                        
                        for handler in self.handlers:
                            if handler['command'] and cb.data:
                                if cb.data == handler['command']:
                                    handler['func'](self, cb)
                
            except Exception as e:
                for err_handler in self.error_handlers:
                    err_handler(e)
                time.sleep(1)
    
    def stop(self):
        self._running = False


class Chat:
    def __init__(self, chat_id, bot):
        self.id = chat_id
        self.bot = bot
    
    def __lshift__(self, text):
        self.bot.send(self.id, text)
    
    def send(self, text, **kwargs):
        return self.bot.send(self.id, text, **kwargs)
    
    def send_photo(self, photo, caption=None):
        return self.bot.send_photo(self.id, photo, caption)
    
    def send_document(self, document, caption=None):
        return self.bot.send_document(self.id, document, caption)
    
    def send_sticker(self, sticker):
        return self.bot.send_sticker(self.id, sticker)
    
    def send_poll(self, question, options):
        return self.bot.send_poll(self.id, question, options)
    
    def send_location(self, latitude, longitude):
        return self.bot.send_location(self.id, latitude, longitude)
    
    def send_contact(self, phone_number, first_name):
        return self.bot.send_contact(self.id, phone_number, first_name)
    
    def send_action(self, action):
        return self.bot.send_chat_action(self.id, action)
    
    def kick(self, user_id):
        return self.bot.kick_chat_member(self.id, user_id)
    
    def unban(self, user_id):
        return self.bot.unban_chat_member(self.id, user_id)
    
    def promote(self, user_id, **kwargs):
        return self.bot.promote_chat_member(self.id, user_id, **kwargs)


class Message:
    def __init__(self, data):
        self.data = data
        self.message_id = data.get('message_id')
        self.from_user = User(data.get('from', {}))
        self.chat = Chat(data['chat']['id'], None)
        self.date = data.get('date')
        self.text = data.get('text', '')
        self.entities = data.get('entities', [])
        self.content_type = self._detect_content_type()
    
    def _detect_content_type(self):
        if 'photo' in self.data:
            return 'photo'
        elif 'video' in self.data:
            return 'video'
        elif 'audio' in self.data:
            return 'audio'
        elif 'document' in self.data:
            return 'document'
        elif 'sticker' in self.data:
            return 'sticker'
        elif 'location' in self.data:
            return 'location'
        elif 'contact' in self.data:
            return 'contact'
        elif 'poll' in self.data:
            return 'poll'
        elif 'text' in self.data:
            return 'text'
        return 'unknown'


class User:
    def __init__(self, data):
        self.id = data.get('id')
        self.is_bot = data.get('is_bot', False)
        self.first_name = data.get('first_name', '')
        self.last_name = data.get('last_name', '')
        self.username = data.get('username', '')
        self.language_code = data.get('language_code', '')


class CallbackQuery:
    def __init__(self, data):
        self.id = data.get('id')
        self.from_user = User(data.get('from', {}))
        self.message = Message(data['message']) if 'message' in data else None
        self.data = data.get('data', '')
        self.chat_instance = data.get('chat_instance', '')


class Keyboard:
    def __init__(self, one_time=False, resize=False):
        self.buttons = []
        self.one_time = one_time
        self.resize = resize
    
    def row(self, *buttons):
        self.buttons.append(list(buttons))
        return self
    
    def to_json(self):
        return json.dumps({
            'keyboard': [[b.to_dict() for b in row] for row in self.buttons],
            'one_time_keyboard': self.one_time,
            'resize_keyboard': self.resize
        })


class InlineKeyboard:
    def __init__(self):
        self.buttons = []
    
    def row(self, *buttons):
        self.buttons.append(list(buttons))
        return self
    
    def to_json(self):
        return json.dumps({
            'inline_keyboard': [[b.to_dict() for b in row] for row in self.buttons]
        })


class Button:
    def __init__(self, text):
        self.text = text
        self._data = {'text': text}
    
    def to_dict(self):
        return self._data


class TextButton(Button):
    pass


class RequestContact(Button):
    def __init__(self, text):
        super().__init__(text)
        self._data['request_contact'] = True


class RequestLocation(Button):
    def __init__(self, text):
        super().__init__(text)
        self._data['request_location'] = True


class InlineButton(Button):
    def __init__(self, text, callback_data=None, url=None):
        super().__init__(text)
        if callback_data:
            self._data['callback_data'] = callback_data
        if url:
            self._data['url'] = url


def перевести(код):
    результат = код
    
    for рус, англ in sorted(ЗАМЕНЫ.items(), key=lambda x: -len(x[0])):
        результат = re.sub(rf'\b{re.escape(рус)}\b', англ, результат)
    
    return результат


def главная():
    if len(sys.argv) < 2:
        печать("Использование: rugram файл.ру")
        sys.exit(1)
    
    входной = sys.argv[1]
    if not входной.endswith('.ру'):
        печать("Файл должен иметь расширение .ру")
        sys.exit(1)
    
    with open(входной, 'r', encoding='utf-8') as ф:
        русский_код = ф.read()
    
    питоний_код = перевести(русский_код)
    
    with open(входной.replace('.ру', '.py'), 'w', encoding='utf-8') as ф:
        ф.write(питоний_код)
    
    печать(f"Готово! {входной} скомпилирован")


if __name__ == '__main__':
    главная()