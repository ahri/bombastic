function game_update(uid) {
    // refresh loop
    setInterval(function() {
        $.read('/player/' + uid, function(resp) {
            $('#game').text(resp.state);
        });
    }, 100);
}

function keys_register(uid) {
    $(document).keydown(function(e) {
        if (e.keyCode == 32) {
            $.update('/player/' + uid, JSON.stringify({'action': 'BOMB'}));
            return false;
        } else if (e.keyCode == 37) {
            $.update('/player/' + uid, JSON.stringify({'action': 'LEFT'}));
            return false;
        } else if (e.keyCode == 38) {
            $.update('/player/' + uid, JSON.stringify({'action': 'UP'}));
            return false;
        } else if (e.keyCode == 39) {
            $.update('/player/' + uid, JSON.stringify({'action': 'RIGHT'}));
            return false;
        } else if (e.keyCode == 40) {
            $.update('/player/' + uid, JSON.stringify({'action': 'DOWN'}));
            return false;
        }
    });
}

function player_create() {
    $.create('/player', JSON.stringify({'name': 'js'}), function(resp) {
        keys_register(resp.uid);
        game_update(resp.uid);
    });
}

$(function() {
    player_create();
});
