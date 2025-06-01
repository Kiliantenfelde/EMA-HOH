from machine import Pin, SoftI2C
import time
from DIYables_Pico_Keypad import Keypad
from lib_lcd1602_2004_with_i2c import LCD

# --- PIN KONFIG ---
Magnetkontakte = [Pin(i, Pin.IN) for i in [4]]
Tuerkontakte = [Pin(i, Pin.IN) for i in [15]]
Bewegungsmelder = [Pin(i, Pin.IN) for i in [16]]

Sabotage = Pin(5, Pin.IN, Pin.PULL_UP)  # inverse Logik: 0 = ausgelöst
Sirene = Pin(21, Pin.OUT)

# --- LCD & KEYPAD ---
lcd = LCD(SoftI2C(scl=Pin(9), sda=Pin(8), freq=100000))
lcd.clear()

ROW_PINS = [40, 39, 38, 48]
COLUMN_PINS = [1, 2, 42, 41]
KEYMAP = ['1','2','3','A',
          '4','5','6','B',
          '7','8','9','C',
          '*','0','#','D']
keypad = Keypad(KEYMAP, ROW_PINS, COLUMN_PINS, 4, 4)

# --- ZUSTÄNDE ---
anlage_scharf = False
alarm_aktiv = False
zustand = "IDLE"
code = ""
code_typ = None
previous_key = None
bewegung_zustand_alt = [sensor.value() for sensor in Bewegungsmelder]
sabotage_unscharf_aktiv = False

# --- CODES ---
SCHALTCODE = "1234"
ALARMCODE = "5678"

# --- FUNKTIONEN ---
def lcd_print(text, y=0, x=0):
    lcd.puts(text, y, x)
    print(text)

def alle_kontakte_geschlossen():
    for kontakt in Magnetkontakte + Tuerkontakte:
        if kontakt.value() == 0:
            return False
    for sensor in Bewegungsmelder:
        if sensor.value() == 1:
            return False
    return Sabotage.value() == 1  # bei Pull-Up: 1 = normal, 0 = Sabotage

def fehlerhafte_kontakte():
    for idx, kontakt in enumerate(Magnetkontakte + Tuerkontakte):
        if kontakt.value() == 0:
            lcd.clear()
            lcd_print("Fehler", 0, 0)
            lcd_print(f"Kontakt {idx+1}", 1, 0)
            time.sleep(2)
    for idx, sensor in enumerate(Bewegungsmelder):
        if sensor.value() == 1:
            lcd.clear()
            lcd_print("Fehler", 0, 0)
            lcd_print("Bewegung erkannt", 1, 0)
            time.sleep(2)
    if Sabotage.value() == 0:
        lcd.clear()
        lcd_print("Fehler", 0, 0)
        lcd_print("Sabotage", 1, 0)
        time.sleep(2)

def start_codeeingabe(typ):
    global zustand, code, code_typ
    code = ""
    code_typ = typ
    lcd.clear()
    lcd_print("Code eingeben", 0, 0)
    zustand = "CODE"

def verarbeite_code():
    global zustand, anlage_scharf, alarm_aktiv, code, sabotage_unscharf_aktiv
    if code_typ == "SCHALTEN" and code == SCHALTCODE:
        anlage_scharf = True
        Sirene.value(0)
        sabotage_unscharf_aktiv = False
        lcd.clear()
        lcd_print("Anlage ist", 0, 0)
        lcd_print("scharf", 1, 0)
    elif code_typ == "UNSCHARF":
        if alarm_aktiv and code == ALARMCODE:
            alarm_aktiv = False
            anlage_scharf = False
            Sirene.value(0)
            sabotage_unscharf_aktiv = False
            lcd.clear()
            lcd_print("Alarm aus", 0, 0)
        elif not alarm_aktiv and code == SCHALTCODE:
            anlage_scharf = False
            Sirene.value(0)
            sabotage_unscharf_aktiv = False
            lcd.clear()
            lcd_print("Anlage ist", 0, 0)
            lcd_print("unscharf", 1, 0)
        else:
            lcd.clear()
            lcd_print("Falscher Code", 0, 0)
    else:
        lcd.clear()
        lcd_print("Falscher Code", 0, 0)
    zustand = "IDLE"
    code = ""

def alarm_ueberwachen():
    global alarm_aktiv, bewegung_zustand_alt, sabotage_unscharf_aktiv
    for i, sensor in enumerate(Bewegungsmelder):
        aktuelle_bewegung = sensor.value()
        if not bewegung_zustand_alt[i] and aktuelle_bewegung:
            if anlage_scharf:
                alarm_aktiv = True
                Sirene.value(1)
                lcd.clear()
                lcd_print("ALARM!!!", 0, 0)
                lcd_print("Bewegung", 1, 0)
            else:
                print("Bewegung erkannt im unscharfen Zustand")
            return
        bewegung_zustand_alt[i] = aktuelle_bewegung
    for sensor in Magnetkontakte + Tuerkontakte:
        if sensor.value() == 0:
            if anlage_scharf and not alarm_aktiv:
                alarm_aktiv = True
                Sirene.value(1)
                lcd.clear()
                lcd_print("ALARM!!!", 0, 0)
                lcd_print("Kontakt", 1, 0)
            elif not anlage_scharf:
                print("Kontakt geöffnet im unscharfen Zustand")
            return
    if Sabotage.value() == 0:
        if anlage_scharf and not alarm_aktiv:
            alarm_aktiv = True
            Sirene.value(1)
            lcd.clear()
            lcd_print("ALARM!!!", 0, 0)
            lcd_print("Sabotage!", 1, 0)
        elif not anlage_scharf and not alarm_aktiv:
            alarm_aktiv = True
            Sirene.value(1)
            lcd.clear()
            lcd_print("SABOTAGE", 0, 0)
            lcd_print("Taste B -> quit", 1, 0)

def main():
    global zustand, code, previous_key
    lcd.clear()
    lcd_print("Taste A oder B", 0, 0)
    lcd_print("unscharf", 1, 0)
    while True:
        key = keypad.get_key()
        if key != previous_key:
            if key is not None:
                print(f"Taste gedrückt: {key}")
                if zustand == "IDLE":
                    if key == "A":
                        if alle_kontakte_geschlossen():
                            start_codeeingabe("SCHALTEN")
                        else:
                            fehlerhafte_kontakte()
                            lcd.clear()
                            lcd_print("Taste A/B", 0, 0)
                            lcd_print("scharf" if anlage_scharf else "unscharf", 1, 0)
                    elif key == "B":
                        start_codeeingabe("UNSCHARF")
                elif zustand == "CODE":
                    if key in "0123456789" and len(code) < 4:
                        code += key
                        lcd.puts("*")
                        print("*")
                    if len(code) == 4:
                        verarbeite_code()
                        lcd.clear()
                        lcd_print("Taste A/B", 0, 0)
                        lcd_print("scharf" if anlage_scharf else "unscharf", 1, 0)
        previous_key = key
        alarm_ueberwachen()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
