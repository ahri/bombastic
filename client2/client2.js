function state_update() {
    $.read('/state', function(resp) {
        $('#state').text(resp);
    });
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
    });
}

$(function() {
    player_create();

    // refresh loop
    setInterval(function() {
        state_update();
    }, 100);
});
