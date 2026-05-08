import requests
import time
import json
import re
from threading import Thread
from datetime import datetime

class ОшибкаТокена(Exception):
    pass

class ОшибкаОтправки(Exception):
    pass

class ОшибкаОбработчика(Exception):
    pass

class Клавиатура:
    def __init__(self, одноразовая=False, изменяемая=False, выборочная=False):
        self.кнопки = []
        self.одноразовая = одноразовая
        self.изменяемая = изменяемая
        self.выборочная = выборочная
    
    def строка(self, *кнопки):
        self.кнопки.append(list(кнопки))
        return self
    
    def в_json(self):
        return json.dumps({
            'keyboard': [[к.словарь() for к in строка] for строка in self.кнопки],
            'one_time_keyboard': self.одноразовая,
            'resize_keyboard': self.изменяемая,
            'selective': self.выборочная
        })
    
    def убрать(self):
        return json.dumps({'remove_keyboard': True})
    
    def сжать(self):
        return json.dumps({'remove_keyboard': True, 'selective': self.выборочная})


class ИнлайнКлавиатура:
    def __init__(self):
        self.кнопки = []
    
    def строка(self, *кнопки):
        self.кнопки.append(list(кнопки))
        return self
    
    def в_json(self):
        return json.dumps({
            'inline_keyboard': [[к.словарь() for к in строка] for строка in self.кнопки]
        })


class Кнопка:
    def __init__(self, текст):
        self.текст = текст
    
    def словарь(self):
        return {'text': self.текст}


class КнопкаКонтакта(Кнопка):
    def словарь(self):
        return {'text': self.текст, 'request_contact': True}


class КнопкаЛокации(Кнопка):
    def словарь(self):
        return {'text': self.текст, 'request_location': True}


class КнопкаОпроса(Кнопка):
    def __init__(self, текст, тип_опроса='regular'):
        super().__init__(текст)
        self.тип_опроса = тип_опроса
    
    def словарь(self):
        return {'text': self.текст, 'request_poll': {'type': self.тип_опроса}}


class ИнлайнКнопка(Кнопка):
    def __init__(self, текст, колбэк=None, ссылка=None, инлайн_запрос=None, 
                 инлайн_чат=None, оплата=None, веб_приложение=None):
        super().__init__(текст)
        self.колбэк = колбэк
        self.ссылка = ссылка
        self.инлайн_запрос = инлайн_запрос
        self.инлайн_чат = инлайн_чат
        self.оплата = оплата
        self.веб_приложение = веб_приложение
    
    def словарь(self):
        данные = {'text': self.текст}
        if self.колбэк:
            данные['callback_data'] = self.колбэк
        if self.ссылка:
            данные['url'] = self.ссылка
        if self.инлайн_запрос:
            данные['switch_inline_query'] = self.инлайн_запрос
        if self.инлайн_чат:
            данные['switch_inline_query_current_chat'] = self.инлайн_чат
        if self.оплата:
            данные['pay'] = True
        if self.веб_приложение:
            данные['web_app'] = self.веб_приложение
        return данные


class Пользователь:
    def __init__(self, данные):
        self.ид = данные.get('id')
        self.бот = данные.get('is_bot', False)
        self.имя = данные.get('first_name', '')
        self.фамилия = данные.get('last_name', '')
        self.юзернейм = данные.get('username', '')
        self.язык = данные.get('language_code', '')
        self.премиум = данные.get('is_premium', False)
        self.ссылка = f"tg://user?id={self.ид}" if self.ид else ''
    
    def упоминание(self):
        if self.юзернейм:
            return f"@{self.юзернейм}"
        elif self.имя:
            return self.имя
        return f"Пользователь {self.ид}"
    
    def __str__(self):
        return self.упоминание()


class Чат:
    def __init__(self, данные):
        self.ид = данные.get('id')
        self.тип = данные.get('type', 'private')
        self.название = данные.get('title', '')
        self.юзернейм = данные.get('username', '')
        self.имя = данные.get('first_name', '')
        self.фамилия = данные.get('last_name', '')
    
    def __str__(self):
        if self.название:
            return self.название
        return f"Чат {self.ид}"


class Сообщение:
    def __init__(self, данные, бот=None):
        self.бот = бот
        self.ид = данные.get('message_id')
        self.от = Пользователь(данные.get('from', {}))
        self.чат = Чат(данные.get('chat', {}))
        self.дата = данные.get('date')
        self.текст = данные.get('text', '')
        self.подпись = данные.get('caption', '')
        self.тип = self._определить_тип(данные)
        self.фото = данные.get('photo', [])
        self.видео = данные.get('video', {})
        self.аудио = данные.get('audio', {})
        self.документ = данные.get('document', {})
        self.стикер = данные.get('sticker', {})
        self.голос = данные.get('voice', {})
        self.видеозаметка = данные.get('video_note', {})
        self.локация = данные.get('location', {})
        self.контакт = данные.get('contact', {})
        self.опрос = данные.get('poll', {})
        self.данные = данные
    
    def _определить_тип(self, данные):
        if 'text' in данные:
            return 'текст'
        elif 'photo' in данные:
            return 'фото'
        elif 'video' in данные:
            return 'видео'
        elif 'audio' in данные:
            return 'аудио'
        elif 'document' in данные:
            return 'документ'
        elif 'sticker' in данные:
            return 'стикер'
        elif 'voice' in данные:
            return 'голос'
        elif 'video_note' in данные:
            return 'видеозаметка'
        elif 'location' in данные:
            return 'локация'
        elif 'contact' in данные:
            return 'контакт'
        elif 'poll' in данные:
            return 'опрос'
        elif 'animation' in данные:
            return 'анимация'
        return 'неизвестно'
    
    def ответить(self, текст, **kwargs):
        if self.бот:
            return self.бот.ответить(self, текст, **kwargs)
    
    def переслать(self, чат_ид):
        if self.бот:
            return self.бот.переслать(чат_ид, self.чат.ид, self.ид)
    
    def удалить(self):
        if self.бот:
            return self.бот.удалить_сообщение(self.чат.ид, self.ид)
    
    def изменить(self, текст, **kwargs):
        if self.бот:
            return self.бот.изменить_сообщение(self.чат.ид, self.ид, текст, **kwargs)


class КолбэкЗапрос:
    def __init__(self, данные, бот=None):
        self.бот = бот
        self.ид = данные.get('id')
        self.от = Пользователь(данные.get('from', {}))
        self.сообщение = Сообщение(данные['message'], бот) if 'message' in данные else None
        self.данные = данные.get('data', '')
        self.чат_экземпляр = данные.get('chat_instance', '')
    
    def ответить(self, текст=None, предупреждение=False):
        if self.бот:
            return self.бот.ответить_на_колбэк(self.ид, текст, предупреждение)


class ИнлайнЗапрос:
    def __init__(self, данные):
        self.ид = данные.get('id')
        self.от = Пользователь(данные.get('from', {}))
        self.запрос = данные.get('query', '')
        self.смещение = данные.get('offset', '')
        self.тип_чата = данные.get('chat_type', '')


class ПредварительнаяОплата:
    def __init__(self, данные):
        self.ид = данные.get('id')
        self.от = Пользователь(данные.get('from', {}))
        self.валюта = данные.get('currency', '')
        self.сумма = данные.get('total_amount', 0)
        self.полезная_нагрузка = данные.get('invoice_payload', '')


class РуГрам:
    def __init__(self, токен):
        self.токен = токен
        self.api = f"https://api.telegram.org/bot{токен}"
        self.обработчики = []
        self.ошибки = []
        self.прослойки = []
        self.запущен = False
        self.контекст = {}
        self.сессии = {}
    
    def __setitem__(self, чат_ид, текст):
        self.отправить(чат_ид, текст)
    
    def __getitem__(self, чат_ид):
        return self.получить_чат(чат_ид)
    
    def обработать(self, команда=None, текст=None, шаблон=None, тип=None, 
                   условие=None, колбэк=None):
        def обёртка(функция):
            self.обработчики.append({
                'команда': команда,
                'текст': текст,
                'шаблон': шаблон,
                'тип': тип,
                'условие': условие,
                'колбэк': колбэк,
                'функция': функция
            })
            return функция
        return обёртка
    
    def ловить_ошибки(self, функция):
        self.ошибки.append(функция)
        return функция
    
    def добавить_прослойку(self, функция):
        self.прослойки.append(функция)
        return функция
    
    def отправить(self, чат_ид, текст, разметка=None, клавиатура=None, 
                  убрать_клавиатуру=False, тихо=False, защита=False,
                  ответ_на=None, разрешить_без_ответа=True):
        данные = {
            'chat_id': чат_ид,
            'text': текст,
            'disable_notification': тихо,
            'protect_content': защита
        }
        if разметка:
            данные['parse_mode'] = разметка
        if клавиатура:
            данные['reply_markup'] = клавиатура.в_json() if isinstance(клавиатура, (Клавиатура, ИнлайнКлавиатура)) else клавиатура
        if убрать_клавиатуру:
            данные['reply_markup'] = Клавиатура().убрать()
        if ответ_на:
            данные['reply_to_message_id'] = ответ_на
        if not разрешить_без_ответа:
            данные['allow_sending_without_reply'] = False
        
        ответ = requests.post(f"{self.api}/sendMessage", json=данные).json()
        if not ответ.get('ok'):
            raise ОшибкаОтправки(ответ.get('description', 'Неизвестная ошибка'))
        return Сообщение(ответ['result'], self)
    
    def ответить(self, сообщение, текст, **kwargs):
        return self.отправить(сообщение.чат.ид, текст, ответ_на=сообщение.ид, **kwargs)
    
    def отправить_фото(self, чат_ид, фото, подпись=None, **kwargs):
        данные = {'chat_id': чат_ид, 'photo': фото}
        if подпись:
            данные['caption'] = подпись
        данные.update(kwargs)
        ответ = requests.post(f"{self.api}/sendPhoto", json=данные).json()
        if not ответ.get('ok'):
            raise ОшибкаОтправки(ответ.get('description', ''))
        return Сообщение(ответ['result'], self)
    
    def отправить_видео(self, чат_ид, видео, подпись=None, **kwargs):
        данные = {'chat_id': чат_ид, 'video': видео}
        if подпись:
            данные['caption'] = подпись
        данные.update(kwargs)
        ответ = requests.post(f"{self.api}/sendVideo", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def отправить_аудио(self, чат_ид, аудио, **kwargs):
        данные = {'chat_id': чат_ид, 'audio': аудио, **kwargs}
        ответ = requests.post(f"{self.api}/sendAudio", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def отправить_документ(self, чат_ид, документ, **kwargs):
        данные = {'chat_id': чат_ид, 'document': документ, **kwargs}
        ответ = requests.post(f"{self.api}/sendDocument", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def отправить_стикер(self, чат_ид, стикер, **kwargs):
        данные = {'chat_id': чат_ид, 'sticker': стикер, **kwargs}
        ответ = requests.post(f"{self.api}/sendSticker", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def отправить_голос(self, чат_ид, голос, **kwargs):
        данные = {'chat_id': чат_ид, 'voice': голос, **kwargs}
        ответ = requests.post(f"{self.api}/sendVoice", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def отправить_опрос(self, чат_ид, вопрос, варианты, анонимный=True, **kwargs):
        данные = {
            'chat_id': чат_ид,
            'question': вопрос,
            'options': варианты,
            'is_anonymous': анонимный,
            **kwargs
        }
        ответ = requests.post(f"{self.api}/sendPoll", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def отправить_локацию(self, чат_ид, широта, долгота, **kwargs):
        данные = {
            'chat_id': чат_ид,
            'latitude': широта,
            'longitude': долгота,
            **kwargs
        }
        ответ = requests.post(f"{self.api}/sendLocation", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def отправить_контакт(self, чат_ид, телефон, имя, **kwargs):
        данные = {
            'chat_id': чат_ид,
            'phone_number': телефон,
            'first_name': имя,
            **kwargs
        }
        ответ = requests.post(f"{self.api}/sendContact", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def отправить_действие(self, чат_ид, действие):
        return requests.post(f"{self.api}/sendChatAction", json={
            'chat_id': чат_ид,
            'action': действие
        }).json()
    
    def переслать(self, чат_ид, откуда_чат_ид, сообщение_ид, **kwargs):
        данные = {
            'chat_id': чат_ид,
            'from_chat_id': откуда_чат_ид,
            'message_id': сообщение_ид,
            **kwargs
        }
        ответ = requests.post(f"{self.api}/forwardMessage", json=данные).json()
        return Сообщение(ответ['result'], self)
    
    def копировать(self, чат_ид, откуда_чат_ид, сообщение_ид, **kwargs):
        данные = {
            'chat_id': чат_ид,
            'from_chat_id': откуда_чат_ид,
            'message_id': сообщение_ид,
            **kwargs
        }
        ответ = requests.post(f"{self.api}/copyMessage", json=данные).json()
        return ответ.get('result', {}).get('message_id')
    
    def изменить_сообщение(self, чат_ид, сообщение_ид, текст, разметка=None, клавиатура=None):
        данные = {
            'chat_id': чат_ид,
            'message_id': сообщение_ид,
            'text': текст
        }
        if разметка:
            данные['parse_mode'] = разметка
        if клавиатура:
            данные['reply_markup'] = клавиатура.в_json() if isinstance(клавиатура, ИнлайнКлавиатура) else клавиатура
        
        ответ = requests.post(f"{self.api}/editMessageText", json=данные).json()
        if not ответ.get('ok'):
            raise ОшибкаОтправки(ответ.get('description', ''))
        return Сообщение(ответ['result'], self)
    
    def удалить_сообщение(self, чат_ид, сообщение_ид):
        return requests.post(f"{self.api}/deleteMessage", json={
            'chat_id': чат_ид,
            'message_id': сообщение_ид
        }).json()
    
    def ответить_на_колбэк(self, запрос_ид, текст=None, предупреждение=False):
        данные = {
            'callback_query_id': запрос_ид,
            'show_alert': предупреждение
        }
        if текст:
            данные['text'] = текст
        return requests.post(f"{self.api}/answerCallbackQuery", json=данные).json()
    
    def ответить_на_инлайн(self, запрос_ид, результаты, кнопка_переключения=None, 
                           личный_кэш=False, время_кэша=300):
        данные = {
            'inline_query_id': запрос_ид,
            'results': json.dumps(результаты),
            'is_personal': личный_кэш,
            'cache_time': время_кэша
        }
        if кнопка_переключения:
            данные['switch_pm_text'] = кнопка_переключения.get('text', '')
            данные['switch_pm_parameter'] = кнопка_переключения.get('parameter', '')
        return requests.post(f"{self.api}/answerInlineQuery", json=данные).json()
    
    def получить_чат(self, чат_ид):
        ответ = requests.post(f"{self.api}/getChat", json={'chat_id': чат_ид}).json()
        if ответ.get('ok'):
            return Чат(ответ['result'])
        return None
    
    def получить_участника(self, чат_ид, пользователь_ид):
        ответ = requests.post(f"{self.api}/getChatMember", json={
            'chat_id': чат_ид,
            'user_id': пользователь_ид
        }).json()
        return ответ.get('result')
    
    def получить_админов(self, чат_ид):
        ответ = requests.post(f"{self.api}/getChatAdministrators", json={
            'chat_id': чат_ид
        }).json()
        return ответ.get('result', [])
    
    def получить_количество(self, чат_ид):
        ответ = requests.post(f"{self.api}/getChatMemberCount", json={
            'chat_id': чат_ид
        }).json()
        return ответ.get('result', 0)
    
    def выгнать(self, чат_ид, пользователь_ид, до_даты=None):
        данные = {
            'chat_id': чат_ид,
            'user_id': пользователь_ид
        }
        if до_даты:
            данные['until_date'] = до_даты
        return requests.post(f"{self.api}/kickChatMember", json=данные).json()
    
    def разбанить(self, чат_ид, пользователь_ид):
        return requests.post(f"{self.api}/unbanChatMember", json={
            'chat_id': чат_ид,
            'user_id': пользователь_ид,
            'only_if_banned': True
        }).json()
    
    def ограничить(self, чат_ид, пользователь_ид, права):
        return requests.post(f"{self.api}/restrictChatMember", json={
            'chat_id': чат_ид,
            'user_id': пользователь_ид,
            'permissions': права
        }).json()
    
    def назначить_админа(self, чат_ид, пользователь_ид, **права):
        данные = {
            'chat_id': чат_ид,
            'user_id': пользователь_ид,
            **права
        }
        return requests.post(f"{self.api}/promoteChatMember", json=данные).json()
    
    def пригласительную(self, чат_ид, имя=None, срок=None, лимит=None):
        данные = {'chat_id': чат_ид}
        if имя:
            данные['name'] = имя
        if срок:
            данные['expire_date'] = срок
        if лимит:
            данные['member_limit'] = лимит
        ответ = requests.post(f"{self.api}/createChatInviteLink", json=данные).json()
        return ответ.get('result', {})
    
    def закрепить(self, чат_ид, сообщение_ид, уведомить=True):
        return requests.post(f"{self.api}/pinChatMessage", json={
            'chat_id': чат_ид,
            'message_id': сообщение_ид,
            'disable_notification': not уведомить
        }).json()
    
    def открепить(self, чат_ид):
        return requests.post(f"{self.api}/unpinChatMessage", json={
            'chat_id': чат_ид
        }).json()
    
    def установить_фото_чата(self, чат_ид, фото):
        return requests.post(f"{self.api}/setChatPhoto", json={
            'chat_id': чат_ид,
            'photo': фото
        }).json()
    
    def удалить_фото_чата(self, чат_ид):
        return requests.post(f"{self.api}/deleteChatPhoto", json={
            'chat_id': чат_ид
        }).json()
    
    def установить_название(self, чат_ид, название):
        return requests.post(f"{self.api}/setChatTitle", json={
            'chat_id': чат_ид,
            'title': название
        }).json()
    
    def установить_описание(self, чат_ид, описание):
        return requests.post(f"{self.api}/setChatDescription", json={
            'chat_id': чат_ид,
            'description': описание
        }).json()
    
    def получить_файл(self, файл_ид):
        ответ = requests.post(f"{self.api}/getFile", json={'file_id': файл_ид}).json()
        if ответ.get('ok'):
            данные = ответ['result']
            данные['url'] = f"https://api.telegram.org/file/bot{self.токен}/{данные['file_path']}"
            return данные
        return None
    
    def скачать_файл(self, файл_ид, путь):
        файл = self.получить_файл(файл_ид)
        if not файл:
            return False
        ответ = requests.get(файл['url'])
        if ответ.status_code == 200:
            with open(путь, 'wb') as ф:
                ф.write(ответ.content)
            return True
        return False
    
    def установить_вебхук(self, урл, секрет=None, разрешённые_обновления=None):
        данные = {'url': урл}
        if секрет:
            данные['secret_token'] = секрет
        if разрешённые_обновления:
            данные['allowed_updates'] = разрешённые_обновления
        return requests.post(f"{self.api}/setWebhook", json=данные).json()
    
    def удалить_вебхук(self):
        return requests.post(f"{self.api}/deleteWebhook").json()
    
    def получить_вебхук(self):
        return requests.post(f"{self.api}/getWebhookInfo").json()
    
    def получить_меня(self):
        ответ = requests.post(f"{self.api}/getMe").json()
        if ответ.get('ok'):
            return Пользователь(ответ['result'])
        return None
    
    def _проверить_соответствие(self, обновление, обработчик):
        if обработчик['условие'] and not обработчик['условие'](обновление):
            return False
        
        if isinstance(обновление, Сообщение):
            if обработчик['команда'] and обновление.текст:
                команда = обработчик['команда']
                if not обновление.текст.startswith(f"/{команда}"):
                    return False
            
            if обработчик['текст'] and обновление.текст:
                if обработчик['текст'] not in обновление.текст:
                    return False
            
            if обработчик['шаблон'] and обновление.текст:
                if not re.search(обработчик['шаблон'], обновление.текст):
                    return False
            
            if обработчик['тип'] and обновление.тип != обработчик['тип']:
                return False
        
        elif isinstance(обновление, КолбэкЗапрос):
            if обработчик['колбэк'] and обновление.данные != обработчик['колбэк']:
                return False
        
        return True
    
    def _прослоить(self, обновление):
        контекст = {}
        for прослойка in self.прослойки:
            результат = прослойка(обновление, контекст)
            if результат is False:
                return False
        return контекст
    
    def _обработать_обновление(self, обновление):
        контекст = self._прослоить(обновление)
        if контекст is False:
            return
        
        for обработчик in self.обработчики:
            if self._проверить_соответствие(обновление, обработчик):
                try:
                    обработчик['функция'](обновление, контекст)
                except Exception as ошибка:
                    for ловец in self.ошибки:
                        ловец(ошибка, обновление)
    
    def запустить(self, пропускать_старые=True, интервал=0.5):
        self.запущен = True
        смещение = None
        
        while self.запущен:
            try:
                параметры = {'timeout': 30, 'allowed_updates': ['message', 'callback_query', 'inline_query']}
                if смещение:
                    параметры['offset'] = смещение
                
                ответ = requests.get(f"{self.api}/getUpdates", params=параметры).json()
                
                if not ответ.get('ok'):
                    continue
                
                for обновление in ответ['result']:
                    смещение = обновление['update_id'] + 1
                    
                    if 'message' in обновление:
                        сообщение = Сообщение(обновление['message'], self)
                        self._обработать_обновление(сообщение)
                    
                    elif 'callback_query' in обновление:
                        колбэк = КолбэкЗапрос(обновление['callback_query'], self)
                        self._обработать_обновление(колбэк)
                    
                    elif 'inline_query' in обновление:
                        инлайн = ИнлайнЗапрос(обновление['inline_query'])
                        self._обработать_обновление(инлайн)
                    
                    elif 'pre_checkout_query' in обновление:
                        предоплата = ПредварительнаяОплата(обновление['pre_checkout_query'])
                        self._обработать_обновление(предоплата)
                
                time.sleep(интервал)
                
            except Exception as ошибка:
                for ловец in self.ошибки:
                    ловец(ошибка, None)
                time.sleep(5)
    
    def остановить(self):
        self.запущен = False
    
    def запустить_вебхук(self, приложение, маршрут='/webhook', порт=5000, 
                          хост='0.0.0.0', секрет=None):
        from flask import Flask, request
        
        if not isinstance(приложение, Flask):
            приложение = Flask(__name__)
        
        @приложение.route(маршрут, methods=['POST'])
        def вебхук():
            if секрет:
                заголовок = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
                if заголовок != секрет:
                    return 'Unauthorized', 401
            
            обновление = request.get_json()
            
            if 'message' in обновление:
                сообщение = Сообщение(обновление['message'], self)
                self._обработать_обновление(сообщение)
            elif 'callback_query' in обновление:
                колбэк = КолбэкЗапрос(обновление['callback_query'], self)
                self._обработать_обновление(колбэк)
            
            return 'OK', 200
        
        приложение.run(host=хост, port=порт)


class Состояние:
    def __init__(self):
        self.пользователи = {}
    
    def установить(self, пользователь_ид, состояние, данные=None):
        self.пользователи[пользователь_ид] = {
            'состояние': состояние,
            'данные': данные or {},
            'время': time.time()
        }
    
    def получить(self, пользователь_ид):
        return self.пользователи.get(пользователь_ид)
    
    def удалить(self, пользователь_ид):
        if пользователь_ид in self.пользователи:
            del self.пользователи[пользователь_ид]
    
    def очистить_старые(self, таймаут=3600):
        сейчас = time.time()
        старые = [
            ид for ид, данные in self.пользователи.items()
            if сейчас - данные['время'] > таймаут
        ]
        for ид in старые:
            del self.пользователи[ид]


class ОчередьЗадач:
    def __init__(self, бот):
        self.бот = бот
        self.задачи = []
        self.поток = None
        self.работает = False
    
    def добавить(self, функция, интервал, повторять=True):
        self.задачи.append({
            'функция': функция,
            'интервал': интервал,
            'повторять': повторять,
            'последний_запуск': 0
        })
    
    def запустить(self):
        self.работает = True
        self.поток = Thread(target=self._цикл)
        self.поток.start()
    
    def остановить(self):
        self.работает = False
        if self.поток:
            self.поток.join()
    
    def _цикл(self):
        while self.работает:
            сейчас = time.time()
            for задача in self.задачи[:]:
                if сейчас - задача['последний_запуск'] >= задача['интервал']:
                    try:
                        задача['функция'](self.бот)
                    except Exception:
                        pass
                    задача['последний_запуск'] = сейчас
                    if not задача['повторять']:
                        self.задачи.remove(задача)
            time.sleep(0.1)


class ПамятьБота:
    def __init__(self):
        self.данные = {}
    
    def сохранить(self, ключ, значение):
        self.данные[ключ] = значение
    
    def получить(self, ключ, по_умолчанию=None):
        return self.данные.get(ключ, по_умолчанию)
    
    def удалить(self, ключ):
        if ключ in self.данные:
            del self.данные[ключ]
    
    def существует(self, ключ):
        return ключ in self.данные
    
    def очистить(self):
        self.данные.clear()


class Журнал:
    УРОВНИ = {
        'отладка': 10,
        'инфо': 20,
        'предупреждение': 30,
        'ошибка': 40,
        'критическая': 50
    }
    
    def __init__(self, уровень='инфо', файл=None):
        self.уровень = self.УРОВНИ.get(уровень, 20)
        self.файл = файл
    
    def _писать(self, уровень, сообщение):
        if self.УРОВНИ.get(уровень, 0) >= self.уровень:
            время = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            текст = f"[{время}] [{уровень.upper()}] {сообщение}"
            
            if self.файл:
                with open(self.файл, 'a', encoding='utf-8') as ф:
                    ф.write(текст + '\n')
            else:
                print(текст)
    
    def отладка(self, сообщение):
        self._писать('отладка', сообщение)
    
    def инфо(self, сообщение):
        self._писать('инфо', сообщение)
    
    def предупреждение(self, сообщение):
        self._писать('предупреждение', сообщение)
    
    def ошибка(self, сообщение):
        self._писать('ошибка', сообщение)
    
    def критическая(self, сообщение):
        self._писать('критическая', сообщение)