import serial
import time

class ArduinoAlert:
    """
    Manages serial communication with Arduino to control
    a physical buzzer for drowsiness/distraction alerts.
    """
    def __init__(self, port='COM7', baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.arduino = None
        self.buzzer_on = False
        self.connect()

    def connect(self):
        """
        Establishes serial connection with Arduino.
        """
        try:
            self.arduino = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset/initialize
            print(f"✅ Connected to Arduino on {self.port}")
        except Exception as e:
            print(f"❌ Could not connect to Arduino: {e}")
            self.arduino = None

    def buzzer_on_signal(self):
        """
        Sends signal to turn buzzer ON (only if not already on).
        """
        if self.arduino and not self.buzzer_on:
            try:
                self.arduino.write(b'1')
                self.buzzer_on = True
            except Exception as e:
                print(f"⚠️ Error sending signal: {e}")

    def buzzer_off_signal(self):
        """
        Sends signal to turn buzzer OFF (only if currently on).
        """
        if self.arduino and self.buzzer_on:
            try:
                self.arduino.write(b'0')
                self.buzzer_on = False
            except Exception as e:
                print(f"⚠️ Error sending signal: {e}")

    def update(self, alert_triggered):
        """
        Call this every frame with True/False depending on
        whether any alert condition is active.
        """
        if alert_triggered:
            self.buzzer_on_signal()
        else:
            self.buzzer_off_signal()

    def close(self):
        """
        Safely closes the serial connection.
        """
        if self.arduino:
            self.buzzer_off_signal()
            self.arduino.close()
            print("✅ Arduino connection closed")