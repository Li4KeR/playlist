import os
import socket
from sql_logic import *
from sys import platform
from config import path_all_video, path_old_video

import shutil
import time


def logging(log_data):
    """ logging """
    with open('log.txt', 'a') as f:
        date_now = datetime.now().strftime("%d.%m.%y %H:%M")
        f.write(f"{date_now} - {log_data}\n")


def logging_errors(log_data):
    """ logging errors """
    with open('error.txt', 'a') as f:
        date_now = datetime.now().strftime("%d.%m.%y %H:%M")
        f.write(f"{date_now} - {log_data}\n")


class Nuke:
    def __init__(self, id_nuke, ip, name, comment):
        """ инициализация класса """
        self.id = id_nuke
        self.ip = ip
        self.name = name
        self.comment = comment
        self.videos = sql_get_all_video_on_nuke(id_nuke)
        # self.status = self.check_connection()
        self.status = None
        self.status_ping = sql_get_ping_status(self.id)[0]

    def add_video(self, id_video):
        """ загрузить видео на нюк и добавить в бд """
        full_info_video = sql_get_info_video_from_id(id_video)
        self.videos.append(full_info_video)
        full_name_video = full_info_video[2]
        try:
            feedback = send_data(self.ip, f"DownloadVideo_____{full_name_video}")
            sql_create_link_video_and_nuke(self.id, id_video)
            logging(feedback)
        except:
            logging_errors(f"Ошибка загрузки видео {full_name_video}\nна хосте {self.name}")

    def delete_video(self, id_video):
        """ удалить видео с нюка и из бд """
        full_info_video = sql_get_info_video_from_id(id_video)
        self.videos.remove(full_info_video)
        full_name_video = full_info_video[2]
        try:
            feedback = send_data(self.ip, f"DeleteVideo_____{full_name_video}")
            sql_delete_link_video_and_nuke(self.id, id_video)
            logging(feedback)
        except:
            logging_errors(f"Ошибка удаления видео {full_name_video}\nна хосте {self.name}")

    def check_connection(self):
        """ проверка работы скрипта на нюке """
        try:
            send_data(self.ip, f"CheckConnections_____")
            self.status = True
        except:
            self.status = False

    def stop_video(self):
        """ остановить все видео на нюке """
        send_data(self.ip, 'Stop_____')

    def play_video(self):
        """ запустить все видео на нюке """
        send_data(self.ip, 'Play_____')


def compare_lists(list_1, list2):
    """ вовзращает отсутвие из списка1 в списке2 """
    absent_in_list2 = []
    for item in list_1:
        if item not in list2:
            absent_in_list2.append(item)
    return absent_in_list2


def ping_nuke(ip):
    """ проверка доступности нюка """
    if platform == 'win32':
        response = os.system(f"ping -n 1 -w 10 {ip} > None")
    else:
        response = os.system(f"ping -c 1 -w 10 {ip} > None")
    if response == 0:
        return True
    else:
        return False


def get_all_nukes():
    """ создания массива нюков на основе данных из бд """
    nukes = sql_get_all_nukes()     # возвращает словарь всех нюков.
                                    # name{'ip_nuke': ip, 'name': name, 'id_nuke': id_nuke, 'comment': comment}
    all_nukes = []
    for cache_nuke in nukes:
        nuke_object = Nuke(nukes.get(cache_nuke).get('id_nuke'),
                           nukes.get(cache_nuke).get('ip_nuke'),
                           nukes.get(cache_nuke).get('name'),
                           nukes.get(cache_nuke).get('comment'))
        all_nukes.append(nuke_object)
    return all_nukes


def check_playlist_mark_sql(response_marks):
    """ сравнивание списков видео в бд и переданном списке """
    sql_check_and_create_bd()
    all_nukes = get_all_nukes()

    # проверка не пустой ли список видео
    if len(response_marks) == 2:
        for row in response_marks:
            if row[0] == 'check_box':
                markers = row[1]
            else:
                nuke_id = row[1]
    else:
        nuke_id = response_marks[0][1]
        markers = []

    nuke_response_id = nuke_id[0]
    # синхронизация видео в принятом списке с бд на нюке
    for nuke in all_nukes:
        if int(nuke.id) == int(nuke_response_id):
            # остановка видео на нюке
            nuke.stop_video()
            time.sleep(1)
            all_video_on_nuke = []
            video_for_delete = []
            # если видео не помечено, но есть в бд
            for video in nuke.videos:
                all_video_on_nuke.append(video[0])
                if str(nuke_response_id) == str(nuke.id):  # ?!?!?!
                    if str(video[0]) not in markers:
                        video_for_delete.append(video[0])
            # удаляем не нужные видео
            for vid in video_for_delete:
                nuke.delete_video(vid)
            # если видео помечено, но нет в бд
            if str(nuke_response_id) == str(nuke.id):
                for video in markers:
                    if int(video) not in all_video_on_nuke:
                        nuke.add_video(int(video))

            check_playlist_sql_physic(nuke.ip, nuke.id)  # refactor all block

            # запуск видео на нюке
            nuke.play_video()


def check_playlist_sql_physic(ip_nuke, id_nuke):
    """ сравнивание списков видео на нюке и в бд """
    sql_video_on_nuke = sql_get_all_video_name_on_nuke(id_nuke)
    sql_video_on_nuke.sort()  # 2 лист
    video_on_hard_nuke = send_data(ip_nuke, f"CheckPhysicVideos_____").split('____')  # 1 лист
    video_on_hard_nuke.sort()

    not_in_nuke = compare_lists(sql_video_on_nuke, video_on_hard_nuke)
    not_in_sql = compare_lists(video_on_hard_nuke, sql_video_on_nuke)

    for item in not_in_nuke:  # если видео нет на нюке, но есть в бд
        id_video = sql_id_from_name_video(item)
        ip_nuke = sql_ip_nuke(id_nuke)[0]
        video_name, full_name = sql_get_name_fullname_video(id_video)
        try:
            test = send_data(ip_nuke, f'DownloadVideo_____{full_name}')
            logging(test)
            # sql_create_link_video_and_nuke(id_nuke, id_video)
            logging(f'{ip_nuke}: download video {full_name} name {video_name} - OK')
        except:
            logging_errors(f'{ip_nuke}: download {full_name} name {video_name}')
        """ Передача айди нюка и айди видео, отправить команду для скачивания видео и добавления в плейлист """
    for item in not_in_sql:  # если видео есть на нюке, не нет в бд
        try:
            send_data(ip_nuke, f'DeleteVideo_____{item}')
            logging(f'{ip_nuke}: delete {item} - OK')
        except:
            logging_errors(f'{ip_nuke}: can\'t delete {item}')
        """ передача айди нюка и айди видео, отправить на нюк команду удаления видео """


def sync_all_videos_ftp_sql(all_video):
    """ сравнивание всех видео на фтп и в бд """
    videos_sql = []
    for row in all_video:
        videos_sql.append(row[2])
    videos_on_ftp = []
    for filename in os.listdir(path=path_all_video):
        vid = f"{path_all_video}/{filename}"
        # test ignore fold
        if os.path.isfile(vid):
            videos_on_ftp.append(filename)

        # videos_on_ftp.append(filename) / thats work

    for video in videos_on_ftp:
        if video not in videos_sql:
            sql_sync_video(video)

    for video in videos_sql:
        if video not in videos_on_ftp:
            sql_delete_video(video)


def delete_video_from_host(video_name, video_id):
    """ удаление видео на самбе и в бд """
    try:
        # os.remove(f'{path_all_video}/{video_name}')
        shutil.move(f'{path_all_video}/{video_name}', f'{path_old_video}/{video_name}')
    except shutil.erorr as error:
        logging_errors(f"delete {video_name} - {error}")
        print(error)
    try:
        sql_delete_video(video_id, video_name)
        # video_id = sql_id_from_name_video(video_name)
        # sql_delete_all_link_video(video_id)
        logging(f"delete {video_name} from sql")
    except sqlite3.erorr as error:
        logging_errors(f"delete {video_name} - {error}")
        print(error)


def send_data(ip, send):
    """ сокет для связи с нюком. передается в формате {КОМАНДА}_____{ПЕРЕМЕННЫЕ}
        СПИСОК КОМАНД:
            CheckPhysicVideos
            DownloadVideo
            DeleteVideo
            Play
            Stop
            CheckConnections
            update_desktop
            CheckVersionServer
            UpdateServer
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 55000))
        data_send = f'{send}'
        sock.send(bytes(data_send, encoding='UTF-8'))
        data_rec = sock.recv(1024).decode('UTF-8')
        sock.close()
        return data_rec
    except socket.error as er:
        logging_errors(f"error {er}: {ip} try {send}")
        return data_rec


def get_all_users():
    """ возвращаем список всех юзеров из бд """
    sql_users = sql_get_all_users()
    all_users = {}
    for row in sql_users:
        all_users[row[0]] = row[1]
    return all_users

