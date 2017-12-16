




class CanvasImg(object):
    
    CanvasImg.CAMERA_WIDTH = 352    # default = 320 PiCamera image width can be greater if quad core RPI
    CanvasImg.CAMERA_HEIGHT = 288   # default = 240 PiCamera image height
    CanvasImg.CAMERA_HFLIP = False  # True=flip camera image horizontally
    CanvasImg.CAMERA_VFLIP = False  # True=flip camera image vertically
    CanvasImg.CAMERA_ROTATION = 0   # Rotate camera image valid values 0, 90, 180, 270
    CanvasImg.CAMERA_FRAMERATE = 25 # default = 25 lower for USB Web Cam. Try different settings

    def __init__(self):

        self.x_center = CAMERA_WIDTH/2
        self.y_center = CAMERA_HEIGHT/2
        self.x_max = CAMERA_HEIGHT
        self.y_max = CAMERA_WIDTH
        self.x_buf = CAMERA_WIDTH/10
        self.y_buf = CAMERA_HEIGHT/10

    def crossed_x_centerline(self, enter, leave, movelist):
        xbuf = 20  # buffer space on either side of x_center to avoid extra counts
        # Check if over center line then count
        if len(movelist) > 1:  # Are there two entries
            if movelist[0] <= self.x_center and  movelist[-1] > self.x_center + self.x_buf:
                leave += 1
                movelist = []
            elif movelist[0] > self.x_center and  movelist[-1] < self.x_center - self.x_buf:
                enter += 1
                movelist = []
        return enter, leave, movelist

    def crossed_y_centerline(self, enter, leave, movelist):
        # Check if over center line then count
        if len(movelist) > 1:  # Are there two entries
            if movelist[0] <= self.y_center and  movelist[-1] > self.y_center + self.y_buf:
                leave += 1
                movelist = []
            elif movelist[0] > self.y_center and  movelist[-1] < self.y_center - self.y_buf:
                enter += 1
                movelist = []
        return enter, leave, movelist