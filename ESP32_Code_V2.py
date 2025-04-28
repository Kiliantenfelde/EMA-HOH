from machine import Pin, SoftI2C
import time
from DIYables_Pico_Keypad import Keypad
from lib_lcd1602_2004_with_i2c import LCD

# Pin Konfiguration
Magnetkontakte = [Pin(i, Pin.IN) for i in [4, 5, 6, 7]]
Tuerkontakte = [Pin(i, Pin.IN) for i in [15, 16, 17, 18]]
Bewegungsmelder = [Pin(i, Pin.IN) for i in [3, 46, 10]]
Sabotage = Pin(21, Pin.IN)
Sirene = Pin(47, Pin.OUT)
scl_pin = 9
sda_pin = 8
#Keypad Konfiguration
ROW_PINS = [40, 39, 38, 48]
COLUMN_PINS = [1, 2, 42, 41]
NUM_ROWS = 4
NUM_COLS = 4
KEYMAP = ['1', '2', '3', 'A',
          '4', '5', '6', 'B',
          '7', '8', '9', 'C',
          '*', '0', '#', 'D']


# LCD Display Initialisierung
lcd = LCD(SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000))
lcd.clear()

# Keypad Initialisierung
keypad = Keypad(KEYMAP, ROW_PINS, COLUMN_PINS, NUM_ROWS, NUM_COLS)
keypad.set_debounce_time(400) # 400ms, addjust it if it detects twice for single press

# Sicherheitscodes
SCHALTCODE = "1234"
ALARMCODE = "5678"

# Zustand der Anlage
anlage_scharf = False
alarm_aktiv = False

def alle_kontakte_geschlossen():
    """Überprüft, ob alle Magnet- und Türkontakte geschlossen sind."""
    print("alle_kontakte_geschlossen")
    for kontakt in Magnetkontakte + Tuerkontakte:
        if kontakt.value() == 1:
            return False
    return Sabotage.value() == 0  # Sabotagekontakt muss geschlossen sein

def fehlerhafte_kontakte():
    """Ermittelt und gibt fehlerhafte Kontakte auf dem LCD aus."""
    print("fehlerhafte_kontakte")
    for idx, kontakt in enumerate(Magnetkontakte + Tuerkontakte):
        if kontakt.value() == 1:
            lcd.clear()
            lcd.puts("Fehler", 0, 0)
            lcd.puts(f"Kontakt {idx+1}", 1, 0)
            time.sleep(2)

    if Sabotage.value() == 1:
        lcd.clear()
        lcd.puts("Fehler", 0, 0)
        lcd.puts("Sabotage", 1, 0)
        time.sleep(2)

def code_eingeben():
    """Fordert den Benutzer zur Codeeingabe auf."""
    print("code_eingeben")
    lcd.clear()
    lcd.puts("Code eingeben")
    code = ""
    while len(code) < 4:
        key = keypad.get_key()
        if key:
            code += key
            lcd.puts("*")
            time.sleep(0.5)
    return code

def scharf_schalten():
    global anlage_scharf
    print("scharf_schalten")
    if not alle_kontakte_geschlossen():
        fehlerhafte_kontakte()
        return
    
    code = code_eingeben()
    if code == SCHALTCODE:
        anlage_scharf = True
        lcd.clear()
        lcd.puts("Anlage scharf!")
    else:
        lcd.clear()
        lcd.puts("Falscher Code")

def unscharf_schalten():
    global anlage_scharf, alarm_aktiv
    print("unscharf_schalten")
    code = code_eingeben()
    if alarm_aktiv and code == ALARMCODE:
        alarm_aktiv = False
        anlage_scharf = False
        Sirene.value(0)
        lcd.clear()
        lcd.puts("Alarm aus")
    elif not alarm_aktiv and code == SCHALTCODE:
        anlage_scharf = False
        lcd.clear()
        lcd.puts("Anlage unscharf")
    else:
        lcd.clear()
        lcd.puts("Falscher Code")

def alarm_ueberwachen():
    global alarm_aktiv
    print("alarm_ueberwachen")
    while anlage_scharf:
        for sensor in Bewegungsmelder:
            if sensor.value() == 1:
                alarm_aktiv = True
                Sirene.value(1)
                lcd.clear()
                lcd.puts("ALARM!!!")
                return
        time.sleep(0.5)

def main():
    while True:
        print("Main")
        lcd.puts("Taste druecken", 0, 0)
        key = keypad.get_key()
        if key == "A":  # Taste für Scharfstellung
            scharf_schalten()
        elif key == "B":  # Taste für Unscharfschaltung
            unscharf_schalten()
        if anlage_scharf:
            alarm_ueberwachen()
        time.sleep(1)

if __name__ == "__main__":
    main()

