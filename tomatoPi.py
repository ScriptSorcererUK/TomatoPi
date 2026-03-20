from tkinter import *
from tkinter import ttk, font
import RPi.GPIO as GPIO
import time
import board
import adafruit_ltr390 as ltr390
from adafruit_seesaw.seesaw import Seesaw


# some numbers for checking stuff
MINIMUM_WETNESS = 500
MIN_LIGHT = 200
MAX_LIGHT = 1000
MIN_TEMP = 10
MAX_TEMP = 30
MIN_UV = 0
MAX_UV = 100


# set the pump pin
pin = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.LOW)

# make sensors
i2c = board.I2C()

try:
    ltr = ltr390.LTR390(i2c)   # light sensor (try so it doesn't crash)
except:
    ltr = None

try:
    ss = Seesaw(i2c, addr=0x36)   # soil sensor (same reason)
except:
    ss = None


# water the plant a bit
def make_it_wetter(*args):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(pin, GPIO.LOW)


# read all sensors + change face
def refresh_values(*args):

    got_lux = None
    got_uvi = None
    got_wet = None
    got_temp = None

    any_good = False   # if everything fails = sad face

    try:
        if ltr:
            got_lux = round(ltr.lux, 1)  # try so bad reads don't explode
            lux.set(got_lux)
            any_good = True
    except:
        pass

    try:
        if ltr:
            got_uvi = round(ltr.uvi)
            uvi.set(got_uvi)
            any_good = True
    except:
        pass

    try:
        if ss:
            got_wet = ss.moisture_read()
            wetness.set(got_wet)
            any_good = True
    except:
        pass

    try:
        if ss:
            got_temp = round(ss.get_temp(), 1)
            temp.set(got_temp)
            any_good = True
    except:
        pass

    # check if plant is "happy"
    try:   # try so bad values don't break the face

        if not any_good:
            face_label.configure(image=frownimg)
            return

        if (got_wet is not None and got_wet > MINIMUM_WETNESS and
            got_lux is not None and MIN_LIGHT <= got_lux <= MAX_LIGHT and
            got_temp is not None and MIN_TEMP <= got_temp <= MAX_TEMP and
            got_uvi is not None and MIN_UV <= got_uvi <= MAX_UV):
            face_label.configure(image=smileimg)
        else:
            face_label.configure(image=frownimg)

    except:
        pass


# refresh every 10 sec
def auto_refresh_loop():
    refresh_values()
    root.after(10000, auto_refresh_loop)   # 10 sec


# check soil every 10 mins and water if too dry
def auto_water_loop():
    try:   # try so it doesn’t freak out if no number
        w = int(wetness.get())
        if w < MINIMUM_WETNESS:
            make_it_wetter()
    except:
        pass

    root.after(600000, auto_water_loop)   # 10 mins


# make the window
root = Tk()
root.title("yababa")

s = ttk.Style()
s.configure('TLabel', font=('Arial', 25))
s.configure('TButton', font=('Arial', 25), padding=(0, 30))
s.configure('TFrame', relief=RIDGE)
s.configure('wet.TFrame', background='#7AC5CD')
s.configure('light.TFrame', background="#DEBB51")
s.configure('a.TFrame', background='#ff0000', relief='flat')

# pictures for the face
smileimg = PhotoImage(file='smile.png')
frownimg = PhotoImage(file='frown.png')

# big outer frame
mainframe = ttk.Frame(root, padding=5, style='a.TFrame')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))


# ---- wet stuff block ----
wetframe = ttk.Frame(mainframe, style="wet.TFrame", padding=(20, 100))
wetframe.grid(column=0, row=0, sticky='NSEW')

ttk.Label(wetframe, text="moisture: ").grid(column=0, row=0, sticky=W)

wetness = StringVar()
wetness.set(504)
ttk.Label(wetframe, textvariable=wetness).grid(column=1, row=0)

ttk.Label(wetframe, text="temperature: \n('C)").grid(column=2, row=0, sticky=E)

temp = StringVar()
temp.set(43)
ttk.Label(wetframe, textvariable=temp).grid(column=3, row=0)

ttk.Button(wetframe, text="water\nnow", command=make_it_wetter).grid(column=4, row=0, sticky=E)

wetframe.columnconfigure(2, weight=1)
wetframe.columnconfigure(4, weight=1)


# ---- face block ----
faceframe = ttk.Frame(mainframe, style="")
faceframe.grid(column=0, row=1, sticky='NSEW')

# face pic holder (start sad)
face_label = ttk.Label(faceframe, image=frownimg)
face_label.grid(column=0, row=0)

faceframe.columnconfigure(0, weight=1)


# ---- light sensor block ----
lightframe = ttk.Frame(mainframe, style='light.TFrame', padding=(20, 100))
lightframe.grid(column=0, row=2, sticky=(N, W, E, S))

ttk.Label(lightframe, text="lux: ").grid(column=0, row=0)

lux = StringVar()
lux.set(5617650)
ttk.Label(lightframe, textvariable=lux).grid(column=1, row=0)

ttk.Label(lightframe, text="uv\nindex: ").grid(column=2, row=0, sticky=E)

uvi = StringVar()
uvi.set(246054)
ttk.Label(lightframe, textvariable=uvi).grid(column=3, row=0)

ttk.Button(lightframe, text='refresh\nvalues', command=refresh_values).grid(column=4, row=0, sticky=E)

lightframe.columnconfigure(2, weight=1)
lightframe.columnconfigure(4, weight=1)


# window size stuff
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
mainframe.rowconfigure(1, weight=8)
mainframe.rowconfigure(2, weight=1)


# start auto refresh
root.after(10000, auto_refresh_loop)

# start auto watering
root.after(600000, auto_water_loop)

root.mainloop()