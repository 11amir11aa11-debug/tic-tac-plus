import http.server
import socketserver
import json
import threading
import uuid
import time
import os


PORT = int(os.environ.get("PORT", 8000))


online_players = {}

invites = {}

game = {
    "board": [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ],
    "turn": "X",
    "winner": None,
    "players": {}
}


lock = threading.Lock()


class GameServer(http.server.SimpleHTTPRequestHandler):


    def send_json(self, data):

        response = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")


        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.end_headers()

        self.wfile.write(response)



    def do_GET(self):


        # بازیکنان آنلاین

        if self.path == "/players":

            with lock:

                self.send_json(
                    list(online_players.values())
                )

            return



        # وضعیت بازی

        if self.path == "/game":

            with lock:

                self.send_json(game)

            return



        # صفحه اصلی

        if self.path == "/":

            self.path = "/index.html"


        super().do_GET()



    def do_POST(self):


        print("POST REQUEST:", self.path)


        length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )


        body = self.rfile.read(length)


        try:

            data = json.loads(body)


        except:

            self.send_json({
                "error": "داده نامعتبر"
            })

            return



        # ورود به لابی

        if self.path == "/login":

            name = data.get(
                "name",
                "Player"
            )


            player_id = str(
                uuid.uuid4()
            )


            with lock:

                online_players[player_id] = {

                    "id": player_id,

                    "name": name,

                    "last_seen": time.time()

                }


            self.send_json({

                "id": player_id,

                "name": name

            })


            return



        # زنده نگه داشتن بازیکن

        if self.path == "/ping":

            player_id = data.get("id")


            with lock:

                if player_id in online_players:

                    online_players[player_id]["last_seen"] = time.time()


            self.send_json({

                "ok": True

            })


            return



        # ارسال دعوت

        if self.path == "/invite":

            sender = data.get("from")

            target = data.get("to")


            with lock:

                if target in online_players:

                    invites[target] = sender


                    self.send_json({

                        "ok": True

                    })

                else:

                    self.send_json({

                        "error": "بازیکن پیدا نشد"

                    })


            return



        # بررسی دعوت

        if self.path == "/check_invite":

            player_id = data.get("id")


            with lock:

                sender = invites.get(player_id)


            self.send_json({

                "from": sender

            })


            return



        # قبول دعوت

        if self.path == "/accept":

            player_id = data.get("id")


            with lock:

                sender = invites.get(player_id)


                if sender:

                    game["players"] = {

                        sender: "X",

                        player_id: "O"

                    }


                    game["board"] = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    ""
]


                    game["turn"] = "X"

                    game["winner"] = None


                    del invites[player_id]


                    self.send_json({

                        "ok": True

                    })


                else:

                    self.send_json({

                        "error": "دعوتی وجود ندارد"

                    })


            return



        # ورود به بازی

        if self.path == "/join":

            player_id = data.get("id")


            with lock:

                if player_id in game["players"]:

                    self.send_json({

                        "player":
                            game["players"][player_id],

                        "game":
                            game

                    })

                else:

                    self.send_json({

                        "player": "waiting"

                    })


            return



        # حرکت

        if self.path == "/move":


            print("MOVE DATA:", data)

            print("CURRENT BOARD:", game["board"])


            try:

                index = int(
                    data.get("index")
                )

            except:

                self.send_json({

                    "error": "خانه نامعتبر"

                })

                return


            player_id = data.get("id")


            with lock:

                if player_id not in game["players"]:

                    self.send_json({

                        "error":
                            "شما داخل بازی نیستید"

                    })

                    return


                player = game["players"][player_id]


                if game["winner"]:

                    self.send_json({

                        "error":
                            "بازی تمام شده"

                    })

                    return


                if game["turn"] != player:

                    self.send_json({

                        "error":
                            "نوبت شما نیست"

                    })

                    return


                if index < 0 or index > 8:

                    self.send_json({

                        "error":
                            "خانه نامعتبر"

                    })

                    return


                if game["board"][index] != "":

                    self.send_json({

                        "error":
                            "این خانه پر است"

                    })

                    return


                game["board"][index] = player


                winner = check_winner(
                    game["board"]
                )


                if winner:

                    game["winner"] = winner


                elif "" not in game["board"]:

                    game["winner"] = "draw"


                else:

                    if player == "X":

                        game["turn"] = "O"

                    else:

                        game["turn"] = "X"


                self.send_json(game)


            return



        # شروع دوباره

        if self.path == "/reset":

            with lock:

                game["board"] = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    ""
]

                game["turn"] = "X"

                game["winner"] = None


            self.send_json(game)

            return



        self.send_json({

            "error":
                "مسیر پیدا نشد"

        })



def check_winner(board):


    patterns = [

        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],

        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],

        [0, 4, 8],
        [2, 4, 6]

    ]


    for a, b, c in patterns:

        if (

            board[a] != ""

            and board[a] == board[b]

            and board[a] == board[c]

        ):

            return board[a]


    return None



class ThreadedServer(
    socketserver.ThreadingMixIn,
    socketserver.TCPServer
):

    allow_reuse_address = True



def cleaner():

    while True:

        time.sleep(10)

        now = time.time()


        with lock:

            remove = []


            for pid, player in online_players.items():

                if now - player["last_seen"] > 30:

                    remove.append(pid)


            for pid in remove:

                del online_players[pid]



threading.Thread(
    target=cleaner,
    daemon=True
).start()



print("🎮 Tic-Tac Plus Online Server")

print(
    f"🌐 Port: {PORT}"
)

print(
    "⛔ برای خاموش کردن Ctrl+C را بزنید."
)



with ThreadedServer(
    ("0.0.0.0", PORT),
    GameServer
) as server:

    server.serve_forever()
