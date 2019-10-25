import random

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from datacenter.models import Schoolkid, Mark, Chastisement, Lesson, Commendation

COMMENDATIONS = ["Молодец",
                 "Отлично!",
                 "Хорошо!",
                 "Гораздо лучше, чем я ожидал!",
                 "Ты меня приятно удивил!",
                 "Великолепно!",
                 "Прекрасно!",
                 "Ты меня очень обрадовал!",
                 "Именно этого я давно ждал от тебя!",
                 "Сказано здорово – просто и ясно!",
                 "Ты, как всегда, точен!",
                 "Очень хороший ответ!",
                 "Талантливо!",
                 "Ты сегодня прыгнул выше головы!",
                 "Я поражен!",
                 "Уже существенно лучше!",
                 "Потрясающе!",
                 "Замечательно!",
                 "Прекрасное начало!",
                 "Так держать!",
                 "Ты на верном пути!",
                 "Здорово!",
                 "Это как раз то, что нужно!",
                 "Я тобой горжусь!",
                 "С каждым разом у тебя получается всё лучше!",
                 "Мы с тобой не зря поработали!",
                 "Я вижу, как ты стараешься!",
                 "Ты растешь над собой!",
                 "Ты многое сделал, я это вижу!",
                 "Теперь у тебя точно все получится!"]


class KidNotFoundException(Exception):
    pass


class TooManyKidsFoundException(Exception):
    pass


class CommendationAlreadyExistException(Exception):
    pass


class SubjectDoesNotExistException(Exception):
    pass


def look_for_kid(name):
    try:
        kid = Schoolkid.objects.get(full_name__contains=name)
    except MultipleObjectsReturned:
        raise TooManyKidsFoundException('По запросу найдено более одного ученика, уточните фамилию и имя!')
    except ObjectDoesNotExist:
        raise KidNotFoundException('Ученик не найден, уточните фамилию и имя!')
    return kid


def fix_marks(name):
    kid = look_for_kid(name)
    bad_marks = Mark.objects.filter(schoolkid=kid, points__lte=3)
    for mark in bad_marks:
        mark.points = 5
        mark.save()
    return


def remove_chastisements(name):
    kid = look_for_kid(name)
    chastisements = Chastisement.objects.filter(schoolkid=kid)
    chastisements.delete()
    return


def create_commendation(name, title):
    kid = look_for_kid(name)
    lesson = Lesson.objects.filter(year_of_study=kid.year_of_study,
                                   group_letter=kid.group_letter,
                                   subject__title__contains=title).order_by('-date').first()
    if lesson is None:
        raise SubjectDoesNotExistException('Предмет не найден, уточните название!')
    if Commendation.objects.filter(created=lesson.date, subject=lesson.subject, schoolkid=kid):
        raise CommendationAlreadyExistException('У тебя уже есть похвала за последний урок!')
    random_commendation = random.choice(COMMENDATIONS)
    Commendation.objects.create(text=random_commendation,
                                created=lesson.date,
                                schoolkid=kid,
                                subject=lesson.subject,
                                teacher=lesson.teacher)
    return
