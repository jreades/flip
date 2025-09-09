class textblock:
    lines = list()
    x     = str()
    y     = str()
    size  = int()
    color = str()
    font  = str()
    style = str()

    def __init__(self, txt:str, halign:str="center", valign:str="middle", size:int=12, font:str="Hanken Grotesk", style:str="Regular"):
        self.lines = txt.split("\n") if "\n" in txt else [txt]
        self.size = size
        self.h_align = halign
        self.v_align = valign
        self.font = font
        self.style = style
        self.position = position(0, 0)

class position:

    def __init__(self, x:float, y:float):

        self.x = x
        self.y = y
    
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

class tposition(position):

    # Notice!!!! Bottom-left is (0,0) in ffmpeg
    # But not seemingly for drawtext???
    left   = float(0)
    top    = float(0)

    center = '(main_w-text_w)/2'
    middle = '(main_h-text_h)/2'

    right  = '(main_w-text_w)'
    bottom = '(main_h-text_h)'

    def get_x(self):
        if self.x == 0:
            return(f"{self.left}")
        elif self.x == 0.5:
            return(f"{self.center}")
        elif self.x == 1:
            return(f"{self.right}")
        else:
            return(f"(main_w*{self.x:0.2f})")

    def get_y(self):
        if self.y == float(0):
            return(f"{self.bottom}")
        elif self.y == float(0.5):
            return(f"{self.middle}")
        elif self.y == float(1):
            return(f"{self.top}")
        else:
            return(f"(main_h*{self.y:0.4f})") # -(text_h/2)

    def __init__(self, x:float, y:float):
        super().__init__(x, y)

class iposition(position):

    # Notice!!!! Bottom-left is (0,0) in ffmpeg
    # But not seemingly for drawtext???
    left   = float(0)
    bottom = float(0)

    center = '(main_w-overlay_w)/2'
    middle = '(main_h-overlay_h)/2'

    right = '(main_w-overlay_w)'
    top   = '(main_h-overlay_h)'

    def get_x(self) -> str:
        if self.x == 0:
            return(f"{self.left}")
        elif self.x == 0.5:
            return(f"{self.center}")
        elif self.x == 1:
            return(f"{self.right}")
        else:
            return(f"(main_w*{self.x:0.2f})")

    def get_y(self) -> str:
        if self.y == 0:
            return(f"{self.bottom}")
        elif self.y == 0.5:
            return(f"{self.middle}")
        elif self.y == 1:
            return(f"{self.top}")
        else:
            #return(f"(h+overlay_h/2)*{self.y:0.2f}")
            return(f"(main_h*{self.y:0.4f})") # -(overlay_h/2)

    def __init__(self, x:float, y:float):
        super().__init__(x, y)

class overlay: 
    
    def __init__(self, x:str, y:str, shortest:bool):
        self.x = x
        self.y = y
        self.shortest = shortest

    def __repr__(self):
        return f'overlay=x={self.x}:y={self.y}{":shortest=1" if self.shortest else ""}'

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

class img_fade(fade):

    def __repr__(self):
        return f'fade={"in" if self.fadein else "out"}:st={self.start:0.2f}:d={self.duration:0.2f}:alpha={self.alpha}'
    
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

class cross_fader(txt_fade):

    fade_in = None
    fade_out = None

    def __init__(self, fi:txt_fade, fo:txt_fade):
        self.fade_in  = fi
        self.fade_out = fo

    def __repr__(self):
        return f'{self.last_rep(self.last_rep(str(self.fade_in),"1)",""),"))",",")}' \
             + f'{self.last_rep(str(self.fade_out),"0))","0))))")}'
    
    def last_rep(self, src:str, rep:str, sub:str):
        return src[::-1].replace(rep[::-1],sub[::-1],1)[::-1] if src.endswith(rep) else src


class scene: 
    rate  = 30 # fps
    size  = (1280,720)
    color = "white"

    length   = None

class intro(scene):

    def __init__(self, scl:float):
        self.length   = scl

    def __repr__(self):
        return f'color={self.color}:s={"x".join([str(x) for x in list(self.size)])}'

class outro(scene):

    color="black"

    def __init__(self, scl:float):
        self.length   = scl

    def __repr__(self):
        return f'color={self.color}:s={"x".join([str(x) for x in list(self.size)])}'

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
        self.halign = halign if halign != "" else None
        self.valign = valign if valign != "" else None

    def add_fader(self, f:txt_fade):
        self.fader = f

    def __repr__(self):
        return f"drawtext=fontfile='{self.font}\\:style={self.style}':text='{self.label}':" \
             + f"fontcolor={self.color}:fontsize={self.size}:x={self.x}:y={self.y}" \
             + (f":text_align={'L' if self.halign == 'left' else 'R'}+{'B' if self.valign == 'bottom' else 'T'}:fix_bounds=true" if self.halign is not None else "") \
             + (f":alpha='{str(self.fader)}'," if self.fader else "")
