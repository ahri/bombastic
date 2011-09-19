function Game() {
    var uid,
        last_frame,
        img_refs = [],
        lookup_prefix = 'img/',
        lookup = {
            ' ': 'tile.png',
            'S': 'tile.png',
            'B': ['block_dome.png', 'block_plain.png', 'block.png', 'block_striped.png', 'block_vents.png'],
            'x': 'bomb.png',
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

    var get_img_for = function (c) {
        img = lookup[c];
        if ($.isArray(img)) {
            // pick a random image
            img = img[Math.floor(Math.random() * img.length)];
        }

        return img;
    }

    var player_create = function () {
        $.create('/player', JSON.stringify({'name': 'js'}), function(resp) {
            uid = resp.uid;
        });
    }

    var keys_register = function () {
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

    var table_build = function () {
        $.read('/game', function(resp) {
            var table = document.getElementById('game'),
                table_row = document.createElement('tr'),
                table_cell,
                img;

            last_frame = resp;

            for (i = 0; i < resp.length; i++) {
                var c = resp.charAt(i);
                if (c == "\n") {
                    table.appendChild(table_row);
                    table_row = document.createElement('tr');
                    continue;
                }
                table_cell = document.createElement('td');
                img        = document.createElement('img');
                img_refs[i] = img;
                img.setAttribute('src', lookup_prefix + get_img_for(c));
                table_cell.appendChild(img);
                table_row.appendChild(table_cell);
            }
        });
    }

    var table_update = function () {
        $.read('/player/' + uid, function(resp) {
            for (i = 0; i < resp.game.length; i++) {
                var c  = resp.game.charAt(i);
                if (c == "\n") {
                    continue;
                }
                var cl = last_frame.charAt(i);

                if (c != cl) {
                    img_refs[i].setAttribute('src', lookup_prefix + get_img_for(c));
                }
            }
            last_frame = resp.game;
        });
    }

    player_create();
    keys_register();
    table_build();

    setInterval(function() {
        table_update();
    }, 100);
}

$(function() {
    Game();
});
