from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, WindowProperties, ClockObject
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectEntry, DirectButton
import socket
import threading

HOST = "PUT_YOUR_WINDOWS_IP_HERE"  # Set to your server IP
PORT = 12345

class GameClient(ShowBase):
    def __init__(self):
        super().__init__()

        # Disable default mouse control so we can do our own
        self.disableMouse()

        # Access the global clock properly (fixes import error)
        self.globalClock = ClockObject.getGlobalClock()

        self.center_mouse()

        self.username = None
        self.role = None
        self.sock = None

        self.accept("escape", self.userExit)

        self.build_login_ui()

    def center_mouse(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        self.win.movePointer(0,
                             int(self.win.getProperties().getXSize() / 2),
                             int(self.win.getProperties().getYSize() / 2))

    def build_login_ui(self):
        self.login_frame = DirectFrame(frameColor=(0, 0, 0, 0.5),
                                       frameSize=(-0.5, 0.5, -0.3, 0.3),
                                       pos=(0, 0, 0))
        self.label_user = DirectLabel(text="Username:",
                                      scale=0.07,
                                      pos=(-0.4, 0, 0.1),
                                      parent=self.login_frame)
        self.entry_user = DirectEntry(text="", scale=0.07,
                                     pos=(-0.1, 0, 0.1),
                                     parent=self.login_frame,
                                     focus=True,
                                     command=self.enter_pressed)
        self.label_pass = DirectLabel(text="Password:",
                                      scale=0.07,
                                      pos=(-0.4, 0, -0.05),
                                      parent=self.login_frame)
        self.entry_pass = DirectEntry(text="", scale=0.07,
                                     pos=(-0.1, 0, -0.05),
                                     parent=self.login_frame,
                                     obscured=True,
                                     command=self.enter_pressed)
        self.login_button = DirectButton(text="Login",
                                        scale=0.07,
                                        pos=(0, 0, -0.2),
                                        parent=self.login_frame,
                                        command=self.attempt_login)

        self.login_message = DirectLabel(text="",
                                         scale=0.05,
                                         pos=(0, 0, -0.3),
                                         parent=self.login_frame)

    def enter_pressed(self, textEntered):
        self.attempt_login()

    def attempt_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if not username or not password:
            self.login_message["text"] = "Please enter username and password."
            return

        threading.Thread(target=self.connect_and_login, args=(username, password), daemon=True).start()

    def connect_and_login(self, username, password):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)  # 10 sec timeout to avoid hangs
            self.sock.connect((HOST, PORT))

            login_str = f"{username}|{password}"
            self.sock.sendall(login_str.encode())

            response = self.sock.recv(1024).decode()
            if response.startswith("OK|"):
                self.username = username
                self.role = response.split("|")[1]
                self.login_success()
            else:
                self.login_message["text"] = "Login failed: " + response.split("|")[1]
                self.sock.close()
                self.sock = None

        except Exception as e:
            self.login_message["text"] = f"Connection error: {e}"

    def login_success(self):
        # Remove login UI
        self.login_frame.destroy()
        self.login_message.destroy()

        self.setup_game()

        threading.Thread(target=self.listen_server, daemon=True).start()

    def setup_game(self):
        self.title = DirectLabel(text=f"Logged in as {self.username} ({self.role})",
                                 scale=0.07,
                                 pos=(0, 0, 0.9))

        self.accept("w", self.move, [Vec3(0, 1, 0)])
        self.accept("s", self.move, [Vec3(0, -1, 0)])
        self.accept("a", self.move, [Vec3(-1, 0, 0)])
        self.accept("d", self.move, [Vec3(1, 0, 0)])

        self.taskMgr.add(self.mouse_look_task, "MouseLook")

    def move(self, direction):
        self.camera.setPos(self.camera.getPos() + direction)

    def mouse_look_task(self, task):
        if self.mouseWatcherNode.hasMouse():
            mw = self.mouseWatcherNode
            x = mw.getMouseX()
            y = mw.getMouseY()

            self.camera.setH(self.camera.getH() - x * 100 * self.globalClock.getDt())
            self.camera.setP(self.camera.getP() - y * 100 * self.globalClock.getDt())

            self.center_mouse()

        return task.cont

    def listen_server(self):
        try:
            while True:
                data = self.sock.recv(1024)
                if not data:
                    print("Server disconnected")
                    break
                msg = data.decode()
                print(f"Server says: {msg}")

                # Here you can update UI/chat as needed

        except Exception as e:
            print(f"Lost connection: {e}")


app = GameClient()
app.run()
