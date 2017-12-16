





class MoveEntity(object):
    def __init__(self):
        self.MIN_AREA = 700            # excludes all contours less than or equal to this Area
        self.diff_window_on = False    # Show OpenCV image difference window
        self.thresh_window_on = False  # Show OpenCV image Threshold window
        self.SHOW_CIRCLE = True        # True= show circle False= show rectancle on biggest motion
        self.CIRCLE_SIZE = 5           # diameter of circle for SHOW_CIRCLE
        self.LINE_THICKNESS = 2        # thickness of bounding line in pixels
        self.font_scale = .5           # size opencv text
        self.WINDOW_BIGGER = 2         # Resize multiplier for Movement Status Window
                                       # if gui_window_on=True then makes opencv window bigger
                                       # # Note if the window is larger than 1 then a reduced frame rate will occur
        self.THRESHOLD_SENSITIVITY = 25
        self.BLUR_SIZE = 10