import urllib
import urllib.request
#import base64
import io
from PIL import ImageTk, Image

class WebImage:
    def __init__(self, url):
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        #self.image = tk.PhotoImage(data=base64.encodebytes(raw_data))
        image = Image.open(io.BytesIO(raw_data)).resize((100, 100))
        self.image = ImageTk.PhotoImage(image)

    def get(self):
        return self.image