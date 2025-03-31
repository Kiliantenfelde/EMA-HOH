from machine import Pin
import time
from keypad import Keypad  # Externes Keypad-Modul wird benötigt
from lcd_i2c import LCD    # Externes LCD-Modul wird benötigt

# Pin Konfiguration
Magnetkontakte = [Pin(i, Pin.IN) for i in [4, 5, 6, 7]]
Tuerkontakte = [Pin(i, Pin.IN) for i in [15, 16, 17, 18]]
Bewegungsmelder = [Pin(i, Pin.IN) for i in [3, 46, 10]]
Sabotage = Pin(35, Pin.IN)
Sirene = Pin(36, Pin.OUT)
ROW_PINS = [43, 44, 1, 2]
COLUMN_PINS = [42, 41, 40, 39]

# LCD Display Initialisierung
lcd = LCD(8, 9)
lcd.clear()

# Keypad Initialisierung
keypad = Keypad(ROW_PINS, COLUMN_PINS)

# Sicherheitscodes
SCHALTCODE = "1234"
ALARMCODE = "5678"

# Zustand der Anlage
anlage_scharf = False
alarm_aktiv = False

def alle_kontakte_geschlossen():
    """Überprüft, ob alle Magnet- und Türkontakte geschlossen sind."""
    for kontakt in Magnetkontakte + Tuerkontakte:
        if kontakt.value() == 1:
            return False
    return Sabotage.value() == 0  # Sabotagekontakt muss geschlossen sein

def fehlerhafte_kontakte():
    """Ermittelt und gibt fehlerhafte Kontakte auf dem LCD aus."""
    lcd.clear()
    for idx, kontakt in enumerate(Magnetkontakte + Tuerkontakte):
        if kontakt.value() == 1:
            lcd.print(f"Fehler: Kontakt {idx+1}")
            time.sleep(2)
    if Sabotage.value() == 1:
        lcd.print("Fehler: Sabotage")
        time.sleep(2)

def code_eingeben():
    """Fordert den Benutzer zur Codeeingabe auf."""
    lcd.clear()
    lcd.print("Code eingeben:")
    code = ""
    while len(code) < 4:
        key = keypad.get_key()
        if key:
            code += key
            lcd.print("*")
            time.sleep(0.5)
    return code

def scharf_schalten():
    global anlage_scharf
    if not alle_kontakte_geschlossen():
        fehlerhafte_kontakte()
        return
    
    code = code_eingeben()
    if code == SCHALTCODE:
        anlage_scharf = True
        lcd.clear()
        lcd.print("Anlage scharf!")
    else:
        lcd.clear()
        lcd.print("Falscher Code")

def unscharf_schalten():
    global anlage_scharf, alarm_aktiv
    code = code_eingeben()
    if alarm_aktiv and code == ALARMCODE:
        alarm_aktiv = False
        anlage_scharf = False
        Sirene.value(0)
        lcd.clear()
        lcd.print("Alarm aus")
    elif not alarm_aktiv and code == SCHALTCODE:
        anlage_scharf = False
        lcd.clear()
        lcd.print("Anlage unscharf")
    else:
        lcd.clear()
        lcd.print("Falscher Code")

def alarm_ueberwachen():
    global alarm_aktiv
    while anlage_scharf:
        for sensor in Bewegungsmelder:
            if sensor.value() == 1:
                alarm_aktiv = True
                Sirene.value(1)
                lcd.clear()
                lcd.print("ALARM!!!")
                return
        time.sleep(0.5)

def main():
    while True:
        lcd.print("Taste druecken")
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
