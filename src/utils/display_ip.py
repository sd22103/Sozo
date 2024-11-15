from common_functions import LCD
import smbus
import time
import ipget

def main():
    bus = smbus.SMBus(1)
    lcd = LCD(bus)
    target_ip = ipget.ipget()
    text_line1 = "ip"
    text_line2 = target_ip.ipaddr("eth0")


    lcd.set_cursor(0, 0)
    lcd.print_text(text_line1)

    lcd.set_cursor(0, 1)
    lcd.print_text(text_line2)

    time.sleep(10)
    lcd.send(LCD.CLEAR_DISPLAY, 1)

if __name__ == "__main__":
    main()