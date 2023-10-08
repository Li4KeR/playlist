from flask import Flask, render_template, url_for, request, redirect, session
import os
from sql_logic import *
from logic import *
from app import app
from app import path_all_video
import time


@app.route('/login')
def login():
    """ форма входа """
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    """ хэндлер входа """
    all_users = get_all_users()

    username = request.form['username'].lower()
    password = request.form['pass']

    if username == 'admin' and password == all_users.get('admin'):
        session['username'] = username
        return redirect('/admin')
    if username in all_users.keys() and password == all_users.get(username):
        session['username'] = username
        return redirect('/')
    else:
        return render_template('login.html', data="Невверный логин или пароль")


@app.route('/admin')
def admin():
    """ страница администрирования """
    username = session['username']
    if sql_check_admin(username) == 1:
    # if 'username' == 'admin':
        all_nukes = get_all_nukes()
        all_video = sql_get_all_videos()
        return render_template("index.html", all_videos=all_video, all_nukes=all_nukes)
    else:
        return redirect('/login')


@app.route('/')
def index():
    """ главная страница """
    # проверка доступности бд
    sql_check_and_create_bd()
    try:
        all_nukes = get_all_nukes()
        """
        all_nukes = get_all_nukes(session.get['username']) sql_get_all_nukes_user(id_user) return (id='id_nuke')
        sql_ get_all_nukes() select * from nukes where id=?, id_nukes
        """
    except:
        pass
    if 'username' in session:
        all_video = sql_get_all_videos()
        return render_template("index.html", all_videos=all_video, all_nukes=all_nukes)
    else:
        return redirect('/login')


@app.route('/', methods=['POST'])
def index_post():
    """ хэндлер для главной страницы """
    response_marks = request.values.lists()
    check_playlist_mark_sql(response_marks)
    return "response_marks"


@app.route('/handler/<id>', methods=['POST'])
def handler(id):
    """ хэндлер для кнопок главной стр """
    all_nukes = get_all_nukes()
    for nuke_cache in all_nukes:
        if str(nuke_cache.id) == id:
            nuke = nuke_cache
    response_data = request.form['index']
    # button play video
    if response_data == f'PlayVideo_{nuke.id}':
        nuke.play_video()
        return "Видео запущено"
    # button pause video
    elif response_data == f'PauseVideo_{nuke.id}':
        nuke.stop_video()
        return "Видео остановлено"
    # sync video
    elif response_data == f'CheckPlaylist_{nuke.id}':
        nuke.stop_video()
        time.sleep(1)
        check_playlist_sql_physic(nuke.ip, nuke.id)
        nuke.play_video()
        logging(f'Синхронизация видео {nuke.ip}')
        return "Синхронизация видео"
    else:
        return redirect('/')


@app.route('/nukes')
def all_nuke():
    """ страница нюков """
    if 'username' in session:
        all_nukes = sql_get_all_nukes()
        return render_template('nukes.html', all_nukes=all_nukes)
    else:
        return redirect('/login')


@app.route('/nukes', methods=['POST'])
def all_nuke_post():
    """ хэндлер для нюков """

    # удаление нюка из бд
    if request.form['name'].split('_')[0] == 'delete':
        id_nuke = request.form['name'].split('_')[1]
        sql_delete_nuke(id_nuke)
        return redirect('/nukes')

    # редактирование нюка
    elif request.form['name'].split('_____')[0] == 'edit':
        id_nuke = request.form['name'].split('_____')[1]
        new_name = request.form['nuke_name']
        new_ip = request.form['ip']
        new_comment = request.form['comment']
        check_ip = sql_check_ip(new_ip, id_nuke)

        if check_ip == []:
            sql_edit_nuke(id_nuke, new_name, new_ip, new_comment)
            return redirect('/nukes')
        else:
            dec_nuke = sql_get_nuke_name(new_ip)[0][0]
            all_nukes = sql_get_all_nukes()
            feedback = f'ip: {new_ip} занят нюком: {dec_nuke}'
            return render_template('nukes.html', all_nukes=all_nukes, feedback=feedback)

    # синхронизация видео
    elif request.form['name'].split('_')[0] == 'sync':
        id_nuke = request.form['name'].split('_')[1]
        ip_nuke = sql_ip_nuke(id_nuke)[0]
        check_playlist_sql_physic(ip_nuke, id_nuke)
        return 'ok'

    # проверка запущен ли сервер на нюке
    elif request.form['name'].split('_')[0] == 'check':
        id_nuke = request.form['name'].split('_')[1]
        ip_nuke = sql_ip_nuke(id_nuke)[0]
        value = send_data(ip_nuke, 'CheckConnections_____')
        if value is True:
            return 'vse ok'
        else:
            return 'ne ok'
    else:
        # добавление нового нюка
        name = request.form['name']
        ip = request.form['ip']
        comment = request.form['comment']
        if comment == '':
            comment = 'Нет описания'
        sql_add_nuke(name, ip, comment)
        return redirect('/nukes')


@app.route('/videos')
def all_videos():
    """ страница с видео """
    if 'username' in session:
        all_video = sql_get_all_videos()
        return render_template('videos.html', all_video=all_video)
    else:
        return redirect('/login')


# отлов событий на странице с видео
@app.route('/videos', methods=['POST'])
def all_videos_post():
    """ хэндлер страницы видео """

    # добавление видео
    if request.form['send'] == "Отправить":
        name = request.form['name']
        file = request.files['file']
        full_name = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], full_name))
        sql_add_video(name, full_name)
        feedback_status = f"Видео {full_name} успешно загружено!"
        all_video = sql_get_all_videos()
        return render_template('videos.html', all_video=all_video, status_download_video=feedback_status)

    # переменование видео
    elif request.form['send'].split('_____')[0] == 'rename':
        new_name = request.form['name']
        id_video = request.form['send'].split('_____')[1]
        sql_rename_video(id_video, new_name)
        all_video = sql_get_all_videos()
        return render_template('videos.html', all_video=all_video)

    # удаление видео
    elif request.form['send'].split('_____')[0] == 'delete':
        video_name = request.form['send'].split('_____')[1]
        video_id = request.form['send'].split('_____')[2]
        delete_video_from_host(video_name, video_id)
        return redirect('/videos')

    # синхронизация видосов
    else:
        all_video = sql_get_all_videos()
        sync_all_videos_ftp_sql(all_video)
        return render_template('videos.html', all_video=all_video, status=True)


@app.route('/faq')
def faq():
    """ страница информации """
    return render_template('faq.html')

