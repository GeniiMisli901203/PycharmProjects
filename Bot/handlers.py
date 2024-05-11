from __future__ import annotations

import telebot.types as tt
import datetime

from api_requests import get_destination_id, get_hotels_info
from loader import bot, db, UserRequest
from abc import ABC, abstractmethod
from typing import Union


class UserContext:
    _state = None

    def __init__(self, user_id: int, state: State) -> None:
        self.change_state(state)
        self.user_id = user_id
        self.user_request = None

    def change_state(self, state: Union[State, CallbackStateMixin]) -> None:
        self._state = state
        self._state.context = self

    async def text_request(self, msg: tt.Message) -> None:
        await self._state.message_handle(msg)

    async def callback_request(self, call: tt.CallbackQuery) -> None:
        await self._state.callback_handle(call)


class State(ABC):

    @property
    def context(self) -> UserContext:
        return self._context

    @context.setter
    def context(self, context: UserContext) -> None:
        self._context = context

    @abstractmethod
    async def message_handle(self, msg: tt.Message) -> None:
        pass


class CallbackStateMixin(ABC):

    @abstractmethod
    async def callback_handle(self, call: tt.CallbackQuery) -> None:
        pass


class StartState(State):

    async def message_handle(self, msg: tt.Message) -> None:
        text = msg.text

        if text.lower() in ("/hello-world", "привет", "/help", "help"):
            response = "Привет. " \
                       "\nЭтот телеграмм-бот поможет найти подходящие отели в любом городе мира." \
                       "\n\nКоманды бота:" \
                       "\n/lowprice: самые дешёвые отели в выбранном городе" \
                       "\n/highprice: самые дорогие отели" \
                       "\n/bestdeal: отели в заданном ценовом диапазоне, " \
                       "находящиеся от центра города не далее заданного расстояния" \
                       "\n/history: история запросов"
            await bot.send_message(msg.from_user.id, response)

        elif text in ("/lowprice", "/highprice", "/bestdeal"):
            today = datetime.datetime.now()
            check_in = (today + datetime.timedelta(1)).date()
            check_out = (today + datetime.timedelta(2)).date()
            with db:
                user_request = UserRequest(user_id=msg.from_user.id,
                                           command=text,
                                           request_dt=datetime.datetime.now(),
                                           check_in=check_in,
                                           check_out=check_out)
                user_request.save()
                self.context.user_request = user_request
            await bot.send_message(msg.from_user.id, "Введите город: ")
            self.context.change_state(GetCityState())

        else:
            await bot.send_message(msg.from_user.id,
                                   'Извините, но такую команду бот не поддерживает. '
                                   'Воспользуйтесь командой /help или введите '
                                   '"Привет" для получения информации о боте.')


class GetCityState(State):

    async def message_handle(self, msg: tt.Message) -> None:
        with db:
            user_request = self.context.user_request
            city = msg.text
            user_request.city = city
            user_request.save()

        if not await get_destination_id(city,
                                        user_request):
            await bot.send_message(msg.from_user.id,
                                   "Не получается найти такой город."
                                   "Проверьте правильность ввода, "
                                   "затем попробуйте ввести заново")
            return

        await bot.send_message(msg.from_user.id,
                               "Сколько отелей показать? (не более 25)")
        self.context.change_state(HotelsCountState())


class HotelsCountState(State):

    async def message_handle(self, msg: tt.Message) -> None:
        if msg.text.isdigit() and 0 < int(msg.text) <= 25:
            count = int(msg.text)
            with db:
                request_data = self.context.user_request
                request_data.hotels_count = count
                request_data.save()
        else:
            await bot.send_message(msg.from_user.id,
                                   "Укажите, пожалуйста, число от 1 до 25")
            return

        need_photos_keyboard = tt.InlineKeyboardMarkup()

        key_yes = tt.InlineKeyboardButton("Да",
                                          callback_data="yes")
        need_photos_keyboard.add(key_yes)
        key_no = tt.InlineKeyboardButton("Нет",
                                         callback_data="no")
        need_photos_keyboard.add(key_no)
        await bot.send_message(msg.from_user.id,
                               text="Показать фотографии отелей? ",
                               reply_markup=need_photos_keyboard)
        self.context.change_state(NeedPhotoState())


class NeedPhotoState(State, CallbackStateMixin):

    async def message_handle(self, msg: tt.Message) -> None:
        pass

    async def callback_handle(self, call: tt.CallbackQuery) -> None:
        user_request = self.context.user_request

        if call.data == "yes":
            await bot.send_message(call.message.chat.id,
                                   "Сколько показать фотографий?\n(не более 4-х)")
            self.context.change_state(PhotosCountState())
        elif call.data == "no":
            await bot.send_message(call.message.chat.id,
                                   "Минутку")
            await get_hotels_info(call.message.chat.id, user_request)
            self.context.change_state(StartState())


class PhotosCountState(State):

    async def message_handle(self, msg: tt.Message) -> None:
        if not msg.text.isdigit() or not 0 < int(msg.text) < 5:
            await bot.send_message(msg.from_user.id,
                                   "Укажите, пожалуйста, число от 1 до 4")
            return

        with db:
            request_data = self.context.user_request
            request_data.photos_count = int(msg.text)
            request_data.save()

        await bot.send_message(msg.from_user.id,
                               "Минутку")
        self.context.change_state(StartState())
        await get_hotels_info(msg.chat.id, request_data)
