from machine import Pin, SoftI2C
import time
from DIYables_Pico_Keypad import Keypad
from lib_lcd1602_2004_with_i2c import LCD

# --- PIN KONFIG ---
Magnetkontakte = [Pin(i, Pin.IN) for i in [4, 5, 6, 7]]
Tuerkontakte = [Pin(i, Pin.IN) for i in [15, 16, 17, 18]]
Bewegungsmelder = [Pin(i, Pin.IN) for i in [3, 46, 10]]
Sabotage = Pin(21, Pin.IN)
Sirene = Pin(47, Pin.OUT)

# --- LCD & KEYPAD ---
lcd = LCD(SoftI2C(scl=Pin(9), sda=Pin(8), freq=50000))
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

# --- CODES ---
SCHALTCODE = "1234"
ALARMCODE = "5678"

# --- FUNKTIONEN ---
def lcd_print(text, y=0, x=0):
    lcd.puts(text, y, x)
    print(text)

def alle_kontakte_geschlossen():
    for kontakt in Magnetkontakte + Tuerkontakte:
        if kontakt.value() == 1:
            return False
    return Sabotage.value() == 0

def fehlerhafte_kontakte():
    for idx, kontakt in enumerate(Magnetkontakte + Tuerkontakte):
        if kontakt.value() == 1:
            lcd.clear()
            lcd_print("Fehler", 0, 0)
            lcd_print(f"Kontakt {idx+1}", 1, 0)
            time.sleep(2)
    if Sabotage.value() == 1:
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
    global zustand, anlage_scharf, alarm_aktiv, code
    if code_typ == "SCHALTEN" and code == SCHALTCODE:
        anlage_scharf = True
        lcd.clear()
        lcd_print("Anlage scharf!", 0, 0)
    elif code_typ == "UNSCHARF":
        if alarm_aktiv and code == ALARMCODE:
            alarm_aktiv = False
            anlage_scharf = False
            Sirene.value(0)
            lcd.clear()
            lcd_print("Alarm aus", 0, 0)
        elif not alarm_aktiv and code == SCHALTCODE:
            anlage_scharf = False
            lcd.clear()
            lcd_print("Anlage unscharf", 0, 0)
        else:
            lcd.clear()
            lcd_print("Falscher Code", 0, 0)
    else:
        lcd.clear()
        lcd_print("Falscher Code", 0, 0)
    zustand = "IDLE"
    code = ""

def alarm_ueberwachen():
    global alarm_aktiv
    if not anlage_scharf:
        return
    for sensor in Bewegungsmelder:
        if sensor.value() == 1:
            alarm_aktiv = True
            Sirene.value(1)
            lcd.clear()
            lcd_print("ALARM!!!", 0, 0)
            break

# --- HAUPTSCHLEIFE ---
def main():
    global zustand, code, previous_key

    lcd.clear()
    lcd_print("Taste A oder B", 0, 0)

    while True:
        key = keypad.get_key()

        # Nur reagieren, wenn neue Taste gedrückt wurde
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

        previous_key = key  # Aktualisiere den letzten Tastenzustand

        alarm_ueberwachen()
        time.sleep(0.02)  # 20 ms Abtastzeit

if __name__ == "__main__":
    main()
