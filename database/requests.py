async def check_admin_func(user_id):
    if session.query(Users.is_admin).filter(Users.user_id == f'{user_id}').first()[0] is True:
        return True
    return False


async def check_subscribe_func(user_id):
    if session.query(Users.subscribe).filter(Users.user_id == f'{user_id}', Users.subscribe.is_(True)).count() != 0:
        return True


async def check_black_list_func(user_id):
    if session.query(Users.black_list).filter(Users.user_id == f'{user_id}', Users.black_list is True).count() == 0:
        return False
    return True


async def check_indicators(user_id):
    result_of_count_with_ind = session.query(UserWords.word).filter(
        UserWords.indicator.is_(True), UserWords.user_id == f'{user_id}').count()
    result_of_all = session.query(UserWords.word).filter(
        UserWords.user_id == f'{user_id}').count()
    if int(result_of_count_with_ind) == int(result_of_all):
        return True
    return False


async def update_all_indicators(user_id):
    session.query(UserWords).filter(UserWords.user_id == f'{user_id}').update({"indicator": False})
    session.commit()


async def add_to_black_list(user_name):
    session.query(Users).filter(Users.username == user_name).update({"black_list": True})
    session.commit()


async def add_to_white_list(user_name):
    session.query(Users).filter(Users.username == f'{user_name}').update({"black_list": False})
    session.commit()


async def change_indicator(user_id, word):
    session.query(UserWords).filter(UserWords.user_id == f'{user_id}', UserWords.word == f'{word}').update({"indicator": True})
    session.commit()


def add_user(user_id, username):
    if session.query(Users.user_id).filter(Users.user_id == f'{user_id}').count() != 0:
        return True
    else:
        user_to_add = Users(
            user_id=user_id,
            username=username
        )
        session.add(user_to_add)
        session.commit()
        return False


async def add_schedule(user_id, username, task, time, day):
    schedule_to_add = Tasks(
        user_id=user_id,
        username=username,
        task=task,
        time=time,
        day=day
    )
    session.add(schedule_to_add)
    session.commit()


async def delete_word_from_list(id_list, user_id):
    session.query(UserWords).filter(
        UserWords.list_id == id_list, UserWords.user_id == user_id).delete(synchronize_session='fetch')
    session.commit()
    session.query(UserWords).filter(
        UserWords.list_id > id_list, UserWords.user_id == user_id).update(
        {"list_id": UserWords.list_id - 1})
    session.commit()


async def list_of_words(user_id):
    result = session.query(UserWords.word, UserWords.translation).filter(UserWords.user_id == f'{user_id}').all()
    return result


async def learning_func_first(user_id):
    result = session.query(UserWords.word).filter(
        UserWords.user_id == f'{user_id}', UserWords.indicator.is_(False)).order_by(UserWords.list_id).limit(1).first()
    return result[0]


async def learning_func_next(user_id, current_word):
    subsquery = session.query(UserWords.list_id).filter(
        UserWords.word == current_word, UserWords.user_id == user_id).first()[0]
    result = session.query(UserWords.word).filter(
        UserWords.user_id == f'{user_id}', UserWords.list_id > subsquery, UserWords.indicator.is_(False)).order_by(
        UserWords.list_id.asc()).first()
    if result is not None:
        return result[0]
    return None


def image_learning_func(user_id, word):
    return session.query(UserWords.image_data).filter(UserWords.word == word, UserWords.user_id == user_id).first()[0]


def audio_learning_func(user_id, word):
    return session.query(UserWords.audio_data).filter(UserWords.word == word, UserWords.user_id == user_id).first()[0]


async def list_add_func(user_id):
    return session.query(UserWords.word, UserWords.translation, UserWords.list_id).filter(
        UserWords.user_id == user_id).order_by(UserWords.list_id).all()


def list_add(user_id):
    result = session.query(UserWords.list_id).filter(UserWords.user_id == f'{user_id}').count()
    return result


async def stat_of_user(user_id):
    list_of_stat = []
    count_of_words = session.query(UserWords.list_id).filter(UserWords.user_id == f'{user_id}').count()
    list_of_stat.append(count_of_words)
    return list_of_stat


async def add_word(word, translation, transcription, image, audio, user_id):
    list_id = list_add(user_id) + 1
    word_to_add = UserWords(
        user_id=user_id,
        list_id=list_id,
        word=word,
        translation=translation,
        transcription=transcription,
        image_data=image,
        audio_data=audio,
    )
    session.add(word_to_add)
    session.commit()


async def get_users():
    return session.query(Users.user_id).all()


def check_db():
    date_time_now = datetime.datetime.now()
    current_time = date_time_now.time()
    date_without_seconds = str(current_time.replace(second=0, microsecond=0))
    current_day_of_week = date_time_now.weekday()
    result = session.query(Tasks.user_id, Tasks.task).filter(
        Tasks.day == current_day_of_week, Tasks.time == date_without_seconds).all()
    print(result)
    return result
