from cog import BasePredictor, Input, Path, ConcatenateIterator
from daily import *
from PIL import Image
import time
import os
import psutil

class Predictor(BasePredictor):

    def netstat(self):
        pid = os.getpid()
        process = psutil.Process(pid)
        connections = process.connections(kind='inet')
        print("------------- NETSTAT ------------")
        for conn in connections:
            if not conn.raddr:
                continue
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}"
            protocol = "TCP" if conn.type == 1 else "UDP" if conn.type == 2 else conn.type
            print(f"{laddr} -> {raddr} ({protocol})")
        print("----------------------------------")

    def setup(self):
        Daily.init()
        self.client = CallClient()

    def predict(self,
        base_url: str = Input(description="Meeting base URL", default="https://replicate-ps.daily.co"),
        room: str = Input(description="Room ID to join", default="test"),
    ) -> ConcatenateIterator[str]:
        self.client.join(f'{base_url}/{room}')
        self.camera = Daily.create_camera_device("test-camera",
            width = 1024,
            height = 1024,
            color_format = "RGB"
        )
        self.client.update_inputs({
            "camera": {
                "isEnabled": True,
                "settings": {
                    "deviceId": "test-camera"
                }
            }
        })
        im = Image.open("test.png").resize((1024, 1024))
        while True:
            self.camera.write_frame(im.tobytes())
            self.netstat()
            time.sleep(5)

