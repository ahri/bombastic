function Game() {
    var uid,
        websocket,
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
            window.location.replace(window.location.href + '?uid=' + uid)
        });
    }

    var keys_register = function () {
        $(document).keydown(function(e) {
            if (e.keyCode == 32) {
                websocket.send('BOMB');
                return false;
            } else if (e.keyCode == 37) {
                websocket.send('LEFT');
                return false;
            } else if (e.keyCode == 38) {
                websocket.send('UP');
                return false;
            } else if (e.keyCode == 39) {
                websocket.send('RIGHT');
                return false;
            } else if (e.keyCode == 40) {
                websocket.send('DOWN');
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

    var table_update = function (resp) {
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
    }

    uid = window.location.search.substr(window.location.search.indexOf('uid=') + 4, 32);
    if (uid == "") {
        player_create();
    }

    var ws_uri = "ws://" + window.location.hostname + ":9000";
    if (MozWebSocket != undefined) {
       WebSocket = MozWebSocket;
    }
    websocket = new WebSocket(ws_uri);
    websocket.onmessage = function(e) {
        table_update(JSON.parse(e.data));
    }
    // grr I didn't need this before; why do I need to set a timeout now?!
    setTimeout(function () {
        websocket.send(uid);

        keys_register();
        table_build();
    }, 1000);
}

$(function() {
    Game();
});
