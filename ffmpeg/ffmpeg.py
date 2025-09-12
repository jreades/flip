# An abstract position class to provide a common interface
# for text and image positions in ffmpeg filters. There is
# some confusion around whether the `y` is somehow inverted
# between drawtext and overlay filters, so we have separate
# subclasses for each. They also have different ways of 
# handling the width/height of the text/image.
class position:

    def __init__(self, x:float, y:float):

        self._x = x
        self._y = y
    
    def get_x(self):
        raise NotImplementedError(
            "Subclasses must implement abstract method"
        )

    def get_y(self):
        raise NotImplementedError(
            "Subclasses must implement abstract method"
        )

    def __repr__(self):
        return f'x={self.get_x()}:y={self.get_y()}'

# Text position subclass. Notice that the origin (0,0) is bottom-left
# in ffmpeg, but not seemingly for drawtext? And height/width are based
# on the text box.
class txt_position(position):

    left   = float(0)
    top    = float(0)

    center = '(main_w-text_w)/2'
    middle = '(main_h-text_h)/2'

    right  = '(main_w-text_w)'
    bottom = '(main_h-text_h)'

    # If working with this as a class.
    def get_x(self):
        if self._x == 0:
            return(f"{self.left}")
        elif self._x == 0.5:
            return(f"{self.center}")
        elif self._x == 1:
            return(f"{self.right}")
        else:
            return(f"(main_w*{self._x:0.2f})")

    # If working with this as a non-instantiated class.
    @classmethod
    def x(cls, x:float):
        if x == 0:
            return(f"{cls.left}")
        elif x == 0.5:
            return(f"{cls.center}")
        elif x == 1:
            return(f"{cls.right}")
        else:
            return(f"(main_w*{x:0.4f})")

    def get_y(self):
        if self._y == float(0):
            return(f"{self.bottom}")
        elif self._y == float(0.5):
            return(f"{self.middle}")
        elif self._y == float(1):
            return(f"{self.top}")
        else:
            return(f"(main_h*{self._y:0.4f})") # -(text_h/2)

    @classmethod
    def y(cls, y:float):
        if y == float(0):
            return(f"{cls.bottom}")
        elif y == float(0.5):
            return(f"{cls.middle}")
        elif y == float(1):
            return(f"{cls.top}")
        else:
            return(f"(main_h*{y:0.4f})") # -(text_h/2)

    def __init__(self, x:float, y:float):
        super().__init__(x, y)

# The image position subclass. Notice that the origin (0,0) is bottom-left
class img_position(position):

    left   = float(0)
    bottom = float(0)

    center = '(main_w-overlay_w)/2'
    middle = '(main_h-overlay_h)/2'

    right = '(main_w-overlay_w)'
    top   = '(main_h-overlay_h)'

    def get_x(self) -> str:
        if self._x == 0:
            return(f"{self.left}")
        elif self._x == 0.5:
            return(f"{self.center}")
        elif self._x == 1:
            return(f"{self.right}")
        else:
            return(f"(main_w*{self._x:0.2f})")

    @classmethod
    def x(cls, x:float) -> str:
        if x == 0:
            return(f"{cls.left}")
        elif x == 0.5:
            return(f"{cls.center}")
        elif x == 1:
            return(f"{cls.right}")
        else:
            return(f"(main_w*{x:0.4f})")
    
    def get_y(self) -> str:
        if self._y == 0:
            return(f"{self.bottom}")
        elif self._y == 0.5:
            return(f"{self.middle}")
        elif self._y == 1:
            return(f"{self.top}")
        else:
            #return(f"(h+overlay_h/2)*{self.y:0.2f}")
            return(f"(main_h*{self._y:0.4f})") # -(overlay_h/2)

    @classmethod
    def y(cls, y:float) -> str:
        if y == 0:
            return(f"{cls.bottom}")
        elif y == 0.5:
            return(f"{cls.middle}")
        elif y == 1:
            return(f"{cls.top}")
        else:
            #return(f"(h+overlay_h/2)*{y:0.2f}")
            return(f"(main_h*{y:0.4f})")
    
    def __init__(self, x:float, y:float):
        super().__init__(x, y)

# Handles the overlay filter, which is mainly used
# for adding images to a video.
class overlay: 
    
    def __init__(self, x:str, y:str, shortest:bool):
        self.x = x
        self.y = y
        self.shortest = shortest

    def __repr__(self):
        return f'overlay=x={self.x}:y={self.y}{":shortest=1" if self.shortest else ""}'

# Handles the fade filter, which is used for both
# images and text. The implementations are different
# for each, so we have separate subclasses.
class fade:
    fadein   = bool()
    duration = float()
    start    = float()
    alpha    = int()

    def __init__(self, fadein:bool, duration:float, start:float, alpha:int=1):
        self.fadein   = fadein
        self.duration = duration
        self.start    = start
        self.alpha    = alpha

# This is for fading images in and out. The code is relatively
# easy to parse by reading the parameters.
class img_fade(fade):

    def __repr__(self):
        return f'fade={"in" if self.fadein else "out"}:st={self.start:0.2f}:d={self.duration:0.2f}:alpha={self.alpha}'

# This is for fading text in and out. The code is a bit
# more complex, as it uses ffmpeg's expression evaluation
# capabilities. 
class txt_fade(fade):

    def __repr__(self):
        end_point = self.start + self.duration
        if self.fadein:
            if self.duration == 0:
                return f"if(lt(t,{self.start:0.2f}),0,1)"
            else:
                return f"if(lt(t,{self.start:0.2f}),0,if(lt(t,{end_point:0.2f}),(t-{self.start:0.2f})/{self.duration:0.2f}))"
        else:
            if self.duration == 0:
                return f"if(lt(t,{self.start:0.2f}),1,0)"
            else:
                return f"if(lt(t,{self.start:0.2f}),1,if(lt(t,{end_point:0.2f}),({self.duration:0.2f}-(t-{self.start:0.2f}))/{self.duration:0.2f},0))"

# This is for cross-fading text, which is a combination
# of a fade-in and a fade-out. The code is a bit more
# complex, as it uses ffmpeg's expression evaluation
# capabilities.
class cross_fader(txt_fade):

    fade_in = None
    fade_out = None

    # Pass in instances of txt_fade
    def __init__(self, fi:txt_fade, fo:txt_fade):
        self.fade_in  = fi
        self.fade_out = fo

    # Insert the fade-in and fade-out expressions
    # into the filter expression.
    def __repr__(self):
        return f'{self.last_rep(self.last_rep(str(self.fade_in),"1)",""),"))",",")}' \
             + f'{self.last_rep(str(self.fade_out),"0))","0))))")}'
    
    def last_rep(self, src:str, rep:str, sub:str):
        return src[::-1].replace(rep[::-1],sub[::-1],1)[::-1] if src.endswith(rep) else src

# A simple scene class to hold the basic parameters
# for the scene, such as length, color, size, and rate.
class scene: 

    length   = None

    def __init__(self, scl:float, color:str="black", size:tuple=(1280,720), rate:int=30):
        self.length   = scl
        self.color    = color
        self.size     = size
        self.rate     = rate

    def __repr__(self):
        return f'color={self.color}:s={"x".join([str(x) for x in list(self.size)])}'

# This is for adding text to a video using the drawtext
# filter. It supports fading in and out using the txt_fade
# class. Font and style should be reasonably intuitive 
# compared to many of the examples I found online.
class text:

    fader = None

    def __init__(self, text:str, x:str, y:str, size:int, color:str, 
                 font:str, style:str="Regular", halign:str="", valign:str=""):
        self.label = text
        self.x = x
        self.y = y
        self.size = size
        self.font = font
        self.color = color
        self.style = style
        self.halign = halign if halign != "" else 'left'
        self.valign = valign if valign != "" else 'center'

    def add_fader(self, f:txt_fade):
        self.fader = f

    # Add the filter expression.
    def __repr__(self):
        return f"drawtext=fontfile='{self.font}\\:style={self.style}':text='{self.label}':" \
             + f"fontcolor={self.color}:fontsize={self.size}:x={self.x}:y={self.y}" \
             + (f":text_align={'L' if self.halign == 'left' else 'R'}+{'B' if self.valign == 'bottom' else 'T'}:fix_bounds=true" if self.halign is not None else "") \
             + (f":alpha='{str(self.fader)}'," if self.fader else "")
