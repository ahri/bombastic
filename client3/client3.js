var lookup_prefix = 'img/',
    lookup_refs = [],
    lookup = {
    ' ': 'tile.png',
    'S': 'tile.png',
    'B': 'block.png',
    '.': 'destructible.png',
    '+': 'flame_cross.png',
    '-': 'flame_hz.png',
    '>': 'flame_hz.png',
    '<': 'flame_hz.png',
    '|': 'flame_vt.png',
    '^': 'flame_vt.png',
    'v': 'flame_vt.png',
    '1': 'p1.png',
    '2': 'p2.png',
    '3': 'p3.png',
    '4': 'p4.png',
    'b': 'powerup_bomb.png',
    'f': 'powerup_flame.png',
};

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

function build_table() {
    $.read('/game', function(resp) {
        var table = document.getElementById('game'),
            table_row = document.createElement('tr'),
            table_cell,
            img;

        for (i = 0; i < resp.length; i++) {
            var c = resp.charAt(i);
            if (c == "\n") {
                table.appendChild(table_row);
                table_row = document.createElement('tr');
                continue;
            }
            table_cell = document.createElement('td');
            img        = document.createElement('img');
            lookup_refs[i] = img;
            img.setAttribute('src', lookup_prefix + lookup[c]);
            table_cell.appendChild(img);
            table_row.appendChild(table_cell);
        }
    });
}

function game_update(uid) {
    // refresh loop
    /*setInterval(function() {
        var last_game;
        $.read('/player/' + uid, function(resp) {
            for (i = 0; i < resp.game.length; i++) {
                var c  = resp.game.charAt(i);
                var cl = last_game.charAt(i);

                if (c == "\n") {
                    alert('newline');
                    continue;
                }

                if (c != cl) {
                    lookup_refs[i].setAttribute('src', lookup_prefix + lookup[c]);
                }
            }
            last_game = resp.game;
        });
    }, 100);*/
}

$(function() {
    player_create();
    build_table();
});
