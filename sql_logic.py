import sqlite3
from datetime import datetime
from config import path_log, path_error


def logging(log_data):
    """ logging """
    with open(path_log, 'a') as f:
        date_now = datetime.now().strftime("%d.%m.%y %H:%M")
        f.write(f"{date_now} - {log_data}\n")


def logging_errors(log_data):
    """ logging errors """
    with open(path_error, 'a') as f:
        date_now = datetime.now().strftime("%d.%m.%y %H:%M")
        f.write(f"{date_now} - {log_data}\n")


def sql_decorator(func):
    """ decorator test """
    def wrapper():
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        try:
            log_text = func()

            logging(log_text)
        except sqlite3.Error as error:
            error_text = "Ошибка при работе с SQLite ", error
            logging_errors(error_text)
        cursor.close()


def sql_check_and_create_bd():
    """ проверка бд """
    try:
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        # таблица для видео
        cursor.execute("""CREATE TABLE IF NOT EXISTS video(
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    full_name TEXT,
                    date_create TEXT);
                    """)
        # таблица для нюков
        cursor.execute("""CREATE TABLE IF NOT EXISTS nuke(
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    ip TEXT NOT NULL UNIQUE,
                    comment TEXT,
                    ping TEXT,
                    date_create TEXT);
                    """)
        # таблица для ассоциации видео на нюках
        cursor.execute("""CREATE TABLE IF NOT EXISTS linking(
                    id INTEGER PRIMARY KEY,
                    id_nuke  INTEGER REFERENCES nuke (id) ON DELETE CASCADE,
                    id_video INTEGER REFERENCES video (id) ON DELETE CASCADE,
                    date_create TEXT);
                    """)
        conn.commit()
        cursor.close()
        logging(f"bd checked success")
        return True
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
        return False


def sql_add_nuke(nuke_name, nuke_ip, comment):
    """ добавить новый нюк в бд """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'INSERT INTO nuke(name, ip, comment, date_create) VALUES("{nuke_name}", "{nuke_ip}", '
                       f'"{comment}", "{datetime.now().strftime("%d.%m.%Y %H:%M")}")')
        conn.commit()
        logging(f"add nuke success")
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_add_video(name, full_name):
    """ добавить новое видео в бд """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'INSERT INTO video(name, full_name, date_create) VALUES("{name}", "{full_name}", '
                       f'"{datetime.now().strftime("%d.%m.%Y %H:%M")}")')
        conn.commit()
        logging(f"add video success")
    except sqlite3.Error as error:
        logging_errors(error)
    cursor.close()


def sql_create_link_video_and_nuke(id_nuke, id_video):
    """ добавление связи видео - нюк по id """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'INSERT INTO linking(id_nuke, id_video, date_create) VALUES("{id_nuke}", "{id_video}", '
                       f'"{datetime.now().strftime("%d.%m.%Y %H:%M")}")')
        conn.commit()
        logging(f"create link success")
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_get_name_nuke(id_nuke):
    """ возвращает имя нюка по id """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        name = cursor.execute(f'SELECT name FROM nuke where id="{id_nuke}"').fetchall()[0]
        return name[0]
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_delete_link_video_and_nuke(id_nuke, id_video):
    """ удаление связи нюк - видео по id """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'DELETE FROM linking WHERE id_nuke="{id_nuke}" AND id_video="{id_video}"')
        conn.commit()
        logging(f"delete link nuke success")
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_get_ip_nuke_and_video(id_nuke, full_name):
    """ возращает ip, имя в бд, имя на фтп """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        id_video = cursor.execute(f'SELECT id FROM video WHERE full_name="{full_name}"').fetchall()[0]
        video_name = cursor.execute(f'SELECT name FROM video where id="{id_video}"').fetchall()[0]
        full_name = cursor.execute(f'SELECT full_name FROM video where id="{id_video}"').fetchall()[0]
        ip_nuke = cursor.execute(f'SELECT ip FROM nuke where id="{id_nuke}"').fetchall()[0]
        return ip_nuke[0], video_name[0], full_name[0]
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_get_all_video_name_on_nuke(id_nuke):
    """ возвращает уникальные видео из таблицы связей """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        all_videos_on_nuke = cursor.execute(f"""SELECT video.full_name FROM linking, nuke, video
        where linking.id_nuke=nuke.id and linking.id_video=video.id and linking.id_nuke='{id_nuke}'""").fetchall()
        video_on_nuke = []
        for video in all_videos_on_nuke:
            # print(video)
            video_on_nuke.append(video[0])
        # print(video_on_nuke)
        return video_on_nuke
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_get_all_nukes():
    """ возвращает массив из всех нюков для создания массива на основе класса """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        nukes = cursor.execute(f'SELECT id, name, ip, comment, ping from nuke ORDER BY name').fetchall()
        nuke = {}
        for item in nukes:
            id_nuke = item[0]
            name = item[1]
            ip = item[2]
            comment = item[3]
            ping = item[4]
            nuke[name] = {'ip_nuke': ip, 'name': name, 'id_nuke': id_nuke, 'comment': comment, 'ping': ping}
        return nuke
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_get_all_videos():
    """ вовзращает все видео в бд """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        videos = cursor.execute(f'SELECT id, name, full_name from video').fetchall()
        return videos
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


# получение всех id видео из таблицы связей с нюком по id нюка
def sql_all_video_on_nuke(id_nuke):
    """ возвращает все id видео для нюка """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        all_videos_on_nuke = cursor.execute(f"""SELECT video.id FROM linking, nuke, video
        where linking.id_nuke=nuke.id and linking.id_video=video.id and linking.id_nuke='{id_nuke}'""").fetchall()
        video_on_nuke = []
        for video in all_videos_on_nuke:
            video_on_nuke.append(str(video[0]))
        return video_on_nuke
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_ip_nuke(id_nuke):
    """ возвращает ip нюка """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        ip_nuke = cursor.execute(f'SELECT ip FROM nuke WHERE id="{id_nuke}"').fetchall()
        return ip_nuke[0]
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_id_from_name_video(full_name):
    """ возвращает id видео """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        id_video = cursor.execute(f'SELECT id FROM video WHERE full_name="{full_name}"').fetchall()[0]
        return id_video[0]
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_sync_video(name_video):
    """ добавление в бд видео для синхронизации """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'INSERT INTO video(name, full_name) VALUES("{name_video}", "{name_video}")')
        conn.commit()
        logging('videos sync success')
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


# список всех видео для нюка из таблицы связей. возвращает id_video, video_name, full_name
def sql_get_all_video_on_nuke(id_nuke):
    """ возвращает id видео, имя вбд, имя на фтп """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        all_videos = cursor.execute(f"""SELECT video.id, video.name, video.full_name FROM linking, video
        WHERE video.id = linking.id_video AND linking.id_nuke={id_nuke}""").fetchall()
        return all_videos
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)


def sql_get_info_video_from_id(video_id):
    """ возвращает id, имя в бд, имя на фтп """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        info_video = cursor.execute(f"""SELECT id, name, full_name FROM video WHERE id={video_id}""").fetchall()
        return info_video[0]
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)


def sql_delete_nuke(id_nuke):
    """ удалить нюк из бд """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'DELETE FROM nuke WHERE id="{int(id_nuke)}"')
        cursor.execute(f'DELETE FROM linking WHERE id_nuke="{int(id_nuke)}"')
        conn.commit()
        logging(f'nuke {id_nuke} deleted success')
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_delete_video(video_id, video_name):
    """ удалить видео из бд """
    try:
        conn = sqlite3.connect('base.sqlite3')
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM video WHERE id="{int(video_id)}"')
        cursor.execute(f'DELETE FROM linking WHERE id_video="{int(video_id)}"')
        conn.commit()
        logging(f'video {video_name} deleted success')
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_get_name_fullname_video(id_video):
    """ возвращает имя видео в бд, имя видео на фтп """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        video_name = cursor.execute(f'SELECT name FROM video where id="{id_video}"').fetchall()[0][0]
        full_name = cursor.execute(f'SELECT full_name FROM video where id="{id_video}"').fetchall()[0][0]
        return video_name, full_name
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_rename_video(id_video, new_name):
    """ переименовать видео """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'UPDATE video SET name="{new_name}" WHERE id="{id_video}"')
        conn.commit()
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_edit_nuke(id_nuke, new_name, new_ip, new_comment):
    """ изменить данные о нюке """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(
            f'UPDATE nuke SET name="{new_name}", ip="{new_ip}", comment="{new_comment}" WHERE id="{id_nuke}"')
        conn.commit()
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_exchange_ping(id_nuke, ping_status):
    """ обновление доступности нюка в бд """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'UPDATE nuke SET ping="{ping_status}" WHERE id="{id_nuke}"')
        conn.commit()
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_get_ping_status(id_nuke):
    """ возвращает статус нюка """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        status_ping = cursor.execute(f'SELECT ping FROM nuke WHERE id="{id_nuke}"').fetchall()[0]
        return status_ping
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_delete_all_link_video(video_id):
    """ удалить все связи для видео """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute(f'DELETE FROM linking WHERE id_video="{video_id}"')
        conn.commit()
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_get_all_users():
    """ возвращает всех юзеров """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    try:
        all_users = cursor.execute(f'SELECT username, password FROM users').fetchall()
        return all_users
    except sqlite3.Error as error:
        error_text = "Ошибка при работе с SQLite ", error
        logging_errors(error_text)
    cursor.close()


def sql_check_ip(ip_nuke, id_nuke):
    """ проверка на эксклюзивность айпи """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    ip = cursor.execute(f'SELECT ip FROM nuke WHERE ip="{ip_nuke}" AND id!="{id_nuke}" ').fetchall()
    return ip


def sql_get_nuke_name(ip_nuke):
    """ возвращает имя нюка """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    nuke_name = cursor.execute(f'SELECT name FROM nuke WHERE ip="{ip_nuke}"').fetchall()
    return nuke_name


def sql_check_admin(username):
    """ проверка на админа """
    conn = sqlite3.connect('base.sqlite3')
    cursor = conn.cursor()
    is_admin = cursor.execute(f'SELECT is_admin FROM users WHERE username="{username}"').fetchall()[0]
    return is_admin
