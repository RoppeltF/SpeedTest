
import sys
import threading
try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:
    pystray = None

def _create_image():
    # simple 64x64 icon
    img = Image.new('RGB', (64, 64), color=(0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((8, 8, 56, 56), fill=(30, 144, 255))
    return img

class TrayApp:
    def __init__(self, on_show, on_quit):
        self.on_show = on_show
        self.on_quit = on_quit
        self.icon = None

    def start(self):
        if pystray is None:
            return
        image = _create_image()
        menu = pystray.Menu(
            pystray.MenuItem('Show', lambda _: self.on_show()),
            pystray.MenuItem('Quit', lambda _: self.on_quit())
        )
        self.icon = pystray.Icon('SpeedTest', image, 'SpeedTest', menu)
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()

