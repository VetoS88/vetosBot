# -*- coding: utf8 -*-

from xml.etree import cElementTree
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from .models import *


def is_drink_prepared(user_id):
    chat_user = User.objects.get(person_id=user_id)
    drink_user = Drink.objects.get(person=chat_user)
    return drink_user.is_ready


def start_drink_prepared(user_id):
    chat_user = User.objects.get(person_id=user_id)
    drink_user = Drink.objects.get(person=chat_user)
    drink_user.is_ready = False
    drink_user.liquid = ""
    drink_user.cup = ""
    drink_user.sugar = ""
    drink_user.save()
    return drink_user.is_ready


def try_get_or_create_user(user_id):
    try:
        chat_user = User.objects.get(person_id=user_id)
    except ObjectDoesNotExist:
        chat_user = User(person_id=user_id)
        chat_user.save()
        try_get_or_create_drink(user_id)
    finally:
        return chat_user


def try_get_or_create_drink(user_id):
    chat_user = try_get_or_create_user(user_id)
    try:
        drink_user = Drink.objects.get(person=chat_user)
        drink_user = Drink.objects.get(person=chat_user)
    except ObjectDoesNotExist:
        drink_user = Drink(person=chat_user)
        drink_user.save()
        drink_user = Drink.objects.get(person=chat_user)
        chat_user.person_drink = drink_user
        chat_user.save()
    finally:
        return drink_user


def drink_condition(user_id):
    try:
        chat_user = User.objects.get(person_id=user_id)
        drink_user = Drink.objects.get(person=chat_user)
        liquid = drink_user.liquid
        cup = drink_user.cup
        sugar = drink_user.sugar
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
            return prepared_drink


def drink_preparation(user_id, answer):
    condition = drink_condition(user_id)
    answer = answer.lower().strip()
    if condition == "no_liquid":
        verification = answer_verification(answer, condition)
        if not verification:
            cup_response = render_to_string('answer_repeat.md')
        else:
            answer = verification
            drink_user = try_get_or_create_drink(user_id)
            drink_user.liquid = answer
            drink_user.save()
            cup_response = " Вы хотите в какой кружке: большой или маленькой? "
        return cup_response
    elif condition == "no_cup":
        verification = answer_verification(answer, condition)
        print
        if not verification:
            sugar_response = render_to_string('answer_repeat.md')
        else:
            answer = verification
            drink_user = try_get_or_create_drink(user_id)
            drink_user.cup = answer
            drink_user.save()
            sugar_response = " Положить ли сахар: да или нет? "
        return sugar_response
    elif condition == "no_sugar":
        verification = answer_verification(answer, condition)
        if not verification:
            prepared_response = render_to_string('answer_repeat.md')
        else:
            answer = verification
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

    if condition == "no_liquid" and right_liquid_answers.get(answer.encode('utf-8')):
        ver_status = right_liquid_answers.get(answer.encode('utf-8'))
    elif condition == "no_cup" and right_cup_answers.get(answer.encode('utf-8')):
        ver_status = right_cup_answers.get(answer.encode('utf-8'))
    elif condition == "no_sugar" and right_sugar_answers.get(answer.encode('utf-8')):
        ver_status = right_sugar_answers.get(answer.encode('utf-8'))
    return ver_status
