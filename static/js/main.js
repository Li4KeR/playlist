function send_form(form_id) {
    var form = $('#'+form_id);
    var msg = form.serialize();
    var nuke = '#nuke_'+form_id;

    $('#block_button_player_'+form_id).toggleClass('display-none block-button');
    $('#nuke_'+form_id).addClass('display-none');
    $('#block_for_load_'+form_id).removeClass('display-none')

    $.ajax({
        type: 'POST',
        url: '/',
        data: msg,
        timeout: 0,
        success: function(data) {
            $('#nuke_'+form_id).removeClass('display-none');
            $('#block_for_load_'+form_id).addClass('display-none');
            $('#block_button_player_'+form_id).toggleClass('block-button display-none');
            $('#div_'+form_id).load('/ '+nuke);
//            $('#block_feedback_status_'+form_id).text('Все ок');
//            alert('vse ok')
        },
        error: function(data){
            alert(data);
        }
    });
//    location.reload();
}


function send_play(nuke_id) {
//    alert(nuke_id)
    var form = $('#play_'+nuke_id);
    var msg = form.serialize();
//    alert(msg)
//    var nuke = '#nuke_'+nuke_id;
//
    $.ajax({
        type: 'POST',
        url: '/handler/'+nuke_id,
        data: msg,
        success: function(data) {
            alert(data)
        },
        error: function(data){
            alert(data);
        }
    });
//    location.reload();
}


function send_stop(nuke_id) {
//    alert(nuke_id)
    var form = $('#stop_'+nuke_id);
    var msg = form.serialize();
//    alert(msg)
//    var nuke = '#nuke_'+nuke_id;
//
    $.ajax({
        type: 'POST',
        url: '/handler/'+nuke_id,
        data: msg,
        success: function(data) {
            alert(data)
        },
        error: function(){
            alert('not good stop'+nuke_id);
        }
    });
//    location.reload();
}


function send_CheckPlaylist(nuke_id) {
//    alert(nuke_id)
    var form = $('#CheckPlaylist_'+nuke_id);
    var msg = form.serialize();
//    alert(msg)
//    var nuke = '#nuke_'+nuke_id;
//
    $.ajax({
        type: 'POST',
        url: '/handler/'+nuke_id,
        data: msg,
        success: function(data) {
            alert(data)
        },
        error: function(){
            alert('Error');
        }
    });
//    location.reload();
}


function send_edit_video(video_data) {
    $('#rename_video_'+video_data).toggleClass('display-none')
}

// загрузка видео
$('#button-download-new-video').click(() => {
    $('#form-download-video').addClass('display-none')
    $('#video-download').removeClass('display-none')
});


function sync_video_nuke(id_nuke) {
//    alert(id_nuke)
    var form = $('#SyncNukeForm_'+id_nuke);
    var msg = form.serialize();
//    alert(msg)
//    var nuke = '#nuke_'+nuke_id;
//    $('#btnVideoSync_'+id_nuke).addClass('display-none')
//
    $.ajax({
        type: 'POST',
        url: '/nukes',
        data: msg,
        success: function(data) {
            $('#btnNukeSync_'+id_nuke).removeClass('bg-dark');
            $('#btnNukeSync_'+id_nuke).addClass('btn-success disabled');
            $('#btnNukeSync_'+id_nuke).text('Успешно');
        },
        error: function(data){
            $('#btnNukeSync_'+id_nuke).addClass('btn-success disabled');
            $('#btnNukeSync_'+id_nuke).text('Неудача');
        }
    });
//    location.reload();
}


function send_edit_nuke(nuke_data) {
    $('#edit_nuke_'+nuke_data).toggleClass('display-none')
}


function check_video_nuke(id_nuke) {
//    alert(id_nuke)
    var form = $('#CheckNukeForm_'+id_nuke);
    var msg = form.serialize();

    $('#btnNukeCheck_'+id_nuke).addClass('disabled');
    $('#btnNukeCheck_'+id_nuke).text('Недоступен');

//    alert(msg)
//    var nuke = '#nuke_'+nuke_id;
//    $('#btnVideoSync_'+id_nuke).addClass('display-none')
//
    $.ajax({
        type: 'POST',
        url: '/nukes',
        data: msg,
        success: function(data) {
            $('#btnNukeCheck_'+id_nuke).removeClass('bg-dark');
            $('#btnNukeCheck_'+id_nuke).addClass('btn-success');
            $('#btnNukeCheck_'+id_nuke).text('Доступен');
        },
        error: function(){
            $('#btnNukeCheck_'+id_nuke).text('Недоступен');
        }
    });
//    location.reload();
}

