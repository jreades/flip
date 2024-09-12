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
    font  = "Barlow"
    color = "4f3d57"
    fader    = None

    def __init__(self, text:str, x:str, y:str, size:int):
        self.label = text
        self.x = x
        self.y = y
        self.size = size

    def add_fader(self, f:txt_fade):
        self.fader = f

    def __repr__(self):
        return f"drawtext=font='{self.font}':text='{self.label}':" \
             + f"fontcolor={self.color}:fontsize={self.size}:x={self.x}:y={self.y}" \
             + (f":alpha='{str(self.fader)}'," if self.fader else "")


#SHOWLEN=0.75+$STARTIN+$FADEIN
#STOPAT=$SHOWLEN+$FADEOUT
#INTROLEN=$STOPAT+0.05
