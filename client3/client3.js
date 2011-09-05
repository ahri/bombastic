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
        state_update(resp.uid);
    });
}

function build_table() {
    $.read('/state', function(resp) {
        var table = document.getElementById('state'),
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

function state_update(uid) {
    // refresh loop
    /*setInterval(function() {
        var last_state;
        $.read('/player/' + uid, function(resp) {
            for (i = 0; i < resp.state.length; i++) {
                var c  = resp.state.charAt(i);
                var cl = last_state.charAt(i);

                if (c == "\n") {
                    alert('newline');
                    continue;
                }

                if (c != cl) {
                    lookup_refs[i].setAttribute('src', lookup_prefix + lookup[c]);
                }
            }
            last_state = resp.state;
        });
    }, 100);*/
}

$(function() {
    player_create();
    build_table();
});
