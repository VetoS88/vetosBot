# -*- coding: utf8 -*-

import json
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import *
from .models import User
from .models import Drink


def drink_condition(user_id):
    try:
        chat_user = User.objects.get(person_id=user_id)
        drink_user = Drink.objects.get(person=chat_user)
        liquid = drink_user.liquid
        cup = drink_user.cup
        sugar = drink_user.sugar
        print liquid, cup, sugar
        print "!!!"
    except ObjectDoesNotExist:
        print "ObjectDoesNotExist"
        return False
    else:
        print "Check condition"
        if not liquid:
            return "no_liquid"
        elif not cup:
            return "no_cup"
        elif not sugar:
            return "no_sugar"
        else:
            yes_answer = 'да'
            all_component = {
                'liquid': liquid.encode('utf-8'),
                'cup': cup.encode('utf-8'),
                'sugar': sugar.encode('utf-8'),
                'answer': yes_answer
            }
            prepared_drink = render_to_string('prepared_drink.md', all_component)
            print prepared_drink
            return prepared_drink


def drink_preparation(user_id, answer):
    condition = drink_condition(user_id)
    if condition == "no_liquid":
        answer = answer.lower()
        verification = answer_verification(answer, condition)
        print "проверка жидкости " + verification
        print
        if not verification:
            cup_response = render_to_string('answer_repeat.md')
        else:
            drink_user = try_get_or_create_drink(user_id)
            drink_user.liquid = answer
            drink_user.save()
            cup_response = " Вы хотите в какой кружке: большой или маленькой? "
        return cup_response
    elif condition == "no_cup":
        print " Начало проверки чашки "
        answer = answer.lower()
        verification = answer_verification(answer, condition)
        print
        if not verification:
            sugar_response = render_to_string('answer_repeat.md')
        else:
            drink_user = try_get_or_create_drink(user_id)
            drink_user.cup = answer
            drink_user.save()
            sugar_response = " Положить ли сахар: да или нет? "
        return sugar_response
    elif condition == "no_sugar":
        answer = answer.lower()
        verification = answer_verification(answer, condition)
        print "проверка сахара " + verification + "  ответ " + answer
        print
        if not verification:
            prepared_response = render_to_string('answer_repeat.md')
        else:
            drink_user = try_get_or_create_drink(user_id)
            drink_user.sugar = answer
            drink_user.is_ready = True
            drink_user.save()
            prepared_response = drink_condition(user_id)
        return prepared_response
    else:
        return "Нет вариантов начните сначала!"


def answer_verification(answer, condition):
    answer = answer.lower()
    ver_status = ""
    print " обьявление  словарей"
    right_liquid_answers = {
        'чай': 'чай',
        'чая': 'чай',
        'кофе': 'кофе',
    }
    right_cup_answers = {
        'большая': 'большой',
        'большой': 'большой',
        'в большой': 'большой',
        'вбольшой': 'большой',
        'маленькая': 'маленькой',
        'маленькой': 'маленькой',
        'в маленькой': 'маленькой',
        'вмаленькой': 'маленькой',
    }
    right_sugar_answers = {
        'да': 'да',
        'нет': 'нет',
        'положить': 'да',
        'да положить': 'да',
        'нет не ложить': 'нет'
    }
    print "конец обьявления"
    print right_cup_answers.get(answer.encode('utf-8')) and condition =="no_cup"

    if condition == "no_liquid" and right_liquid_answers.get(answer.encode('utf-8')):
        ver_status = right_liquid_answers.get(answer.encode('utf-8'))
    elif condition == "no_cup" and right_cup_answers.get(answer.encode('utf-8')):
        ver_status = right_liquid_answers.get(answer.encode('utf-8'))
    elif condition == "no_sugar" and right_sugar_answers.get(answer.encode('utf-8')):
        ver_status = right_liquid_answers.get(answer.encode('utf-8'))
    return ver_status


class CommandTestView(View):
    def post(self, request, bot_token):

        user_id = 142315803
        chat_user = User.objects.get(person_id=user_id)
        drink_user = Drink.objects.get(person=chat_user)
        liquid = drink_user.liquid
        cup = drink_user.cup
        sugar = drink_user.sugar
        raw = request.body.decode('utf-8')
        payload = json.loads(raw)
        answer = payload['message'].get('text')
        answer = answer.lower()

        drink_preparation(user_id, answer)

        print "test"
        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandTestView, self).dispatch(request, *args, **kwargs)
