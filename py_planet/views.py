# -*- coding: utf8 -*-

import json
import logging

import telepot
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .utils import *

TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

logger = logging.getLogger('telegram.bot')


def _display_help():
    return render_to_string('help.md')


def _start_chat(user_id):
    chat_user = try_get_or_create_user(user_id)
    greetings = chat_user.first_name + '\n' + render_to_string('help.md')
    return greetings


def _drink(user_id):
    try_get_or_create_drink(user_id)
    start_drink_prepared(user_id)
    return render_to_string('start_drink.md')


def _display_hello():
    return render_to_string('hello.md')


class CommandReceiveView(View):
    def post(self, request, bot_token):

        raw = request.body.decode('utf-8')

        logger.info(raw)

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            user_id = payload['message']['from']['id']
            chat_id = payload['message']['chat']['id']
            cmd = payload['message'].get('text')  # command
            if cmd == "/start":
                response = _start_chat(user_id)
                TelegramBot.sendMessage(chat_id, response)
            elif cmd == "/help":
                response = _display_help()
                TelegramBot.sendMessage(chat_id, response)
            try:
                dialog_drink_condition = is_drink_prepared(user_id)
            except ObjectDoesNotExist:
                TelegramBot.sendMessage(chat_id, 'Сначала введите команду "/start"!')
            else:
                if cmd == "/drink":
                    response = _drink(user_id)
                    TelegramBot.sendMessage(chat_id, response)
                elif not dialog_drink_condition:
                    response = drink_preparation(user_id, cmd)
                    TelegramBot.sendMessage(chat_id, response)
                elif cmd != "/start" and cmd != "/help":
                    TelegramBot.sendMessage(chat_id, "Не понятно. ")
        finally:
            return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
