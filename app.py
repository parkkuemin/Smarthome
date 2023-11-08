from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask import session, url_for, abort, redirect
from urllib.parse import urlencode, unquote
from dotenv import load_dotenv
import RPi.GPIO as GPIO
import Adafruit_BMP.BMP085 as BMP085
import time
from gpiozero import LEDBoard
import threading

app = Flask(__name__)

sensor = BMP085.BMP085()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

SERVO_PIN = 12
TRIG = 23
ECHO = 24
LED_PIN = 18
LED_PIN_MAIN = 6
LED_PIN_KIT = 13
LED_PIN_IN = 19
LED_PIN_TV = 26
button_open = 16
button_close = 20

leds = LEDBoard(6, 13, 19, 26)

led_states = {
    'white': 0,
    'green': 0,
    'yellow': 0,
    'blue': 0
}

air_conditioner_state = 0

GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(LED_PIN_MAIN, GPIO.OUT)
GPIO.setup(LED_PIN_KIT, GPIO.OUT)
GPIO.setup(LED_PIN_IN, GPIO.OUT)
GPIO.setup(LED_PIN_TV, GPIO.OUT)
GPIO.setup(button_open, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_close, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)

servo = GPIO.PWM(SERVO_PIN, 50)



def main_loop():
    try:
        while True:
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)

            while GPIO.input(ECHO) == 0:
                start = time.time()
            while GPIO.input(ECHO) == 1:
                stop = time.time()
            check_time = stop - start

            distance = check_time * 34300 / 2
            if distance <= 20:
                GPIO.output(LED_PIN, GPIO.HIGH)
                print("현관LED ON")
                time.sleep(2)
                GPIO.output(LED_PIN, GPIO.LOW)
            else:
                GPIO.output(LED_PIN, GPIO.LOW)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        
temperature = sensor.read_temperature() #온도값을 읽어와 변수에 저장
pressure = sensor.read_pressure() #기압값을 읽어와 변수에 저장
altitude = sensor.read_altitude() #고도값을 읽어와 변수에 저장


servo.start(0)
# 모터 제어 함수
def control_motor():
    try:
        while True:
            if GPIO.input(button_open) == GPIO.HIGH:
                servo.ChangeDutyCycle(12.5)
                print("Door open")
                time.sleep(1)
            elif GPIO.input(button_close) == GPIO.HIGH:
                servo.ChangeDutyCycle(2)
                print("Door close")                
                time.sleep(1)
            else:
                servo.ChangeDutyCycle(0)
                time.sleep(0)
    except KeyboardInterrupt:
        pass
    finally:
        servo.stop()
        GPIO.cleanup()
# 모터 제어 스레드 시작
motor_thread = threading.Thread(target=control_motor)
motor_thread.daemon = True
motor_thread.start()


@app.route('/')
def index():
    return render_template('index.html', temperature=temperature, pressure=pressure, altitude=altitude, led_states=led_states)

@app.route('/control_led_pin/<int:led_state>')
def control_led_pin(led_state):
    if led_state == 1:
        GPIO.output(LED_PIN, GPIO.HIGH)
        return "LED_PIN turned on"
    elif led_state == 0:
        GPIO.output(LED_PIN, GPIO.LOW)
        return "LED_PIN turned off"
    else:
        return "Invalid LED_PIN state"

@app.route('/get_sensor_data')
def get_sensor_data():
    data = {
        'temperature': temperature,
        'pressure': pressure,
        'altitude': altitude
    }
    return jsonify(data)

@app.route('/air_conditioner/<int:state>')
def air_conditioner(state):
    global air_conditioner_state
    air_conditioner_state = state

    air_conditioner_pin = 25

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(air_conditioner_pin, GPIO.OUT)

    if air_conditioner_state == 1:
        GPIO.output(air_conditioner_pin, GPIO.HIGH)
    else:
        GPIO.output(air_conditioner_pin, GPIO.LOW)
    return redirect(url_for('index'))

@app.route('/<color>/<int:state>')
def led_switch(color, state):
    led_states[color] = state
    leds.value = tuple(led_states.values())
    return redirect(url_for('index'))

@app.route('/all/<int:state>')
def all_on_off(state):
    if state == 0:
        for key in led_states:
            led_states[key] = 0
    elif state == 1:
        for key in led_states:
            led_states[key] = 1
    leds.value = tuple(led_states.values())
    return redirect(url_for('index'))

if __name__ == '__main__':
    main_loop_thread = threading.Thread(target=main_loop)
    main_loop_thread.start()
    app.run(host='0.0.0.0', debug=True)
