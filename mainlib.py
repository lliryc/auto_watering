import machine as m
import time
import network
import config
import utime
from umqtt.simple import MQTTClient

def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(config.WIFI_ID, config.WIFI_PWD)
    while not sta_if.isconnected():
        time.sleep(1)
        pass
    return sta_if.isconnected()

def send_values(values):
    client_id = config.MQTT_CLIENT_ID
    url = config.MQTT_URL
    user_id =  config.MQTT_USER_ID
    mqqt_key = config.MQTT_KEY
    write_key = config.MQTT_WRITE_KEY
    client = MQTTClient(client_id=client_id, server=url, user=user_id, password=mqqt_key, ssl=False)
    client.connect()
    credentials = bytes("channels/{:s}/publish/{:s}".format(config.MQTT_CHANNEL_ID, write_key), 'utf-8')
    payload = bytes("field1={:.1f}&field2={:.1f}".format(values[0], values[1]), 'utf-8')
    client.publish(credentials, payload)
    client.disconnect()
    time.sleep(3)

def pump(sec):
    m.Pin(5, m.Pin.OUT)
    time.sleep(sec)
    m.Pin(5, m.Pin.IN)

def is_dry():
    adc = m.ADC(0)
    v = adc.read()
    if v > config.TRIGGER_SOIL:
        return True
    return False

def deep_sleep():
    rtc = m.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=m.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, 60 * 60 * 1000)
    m.deepsleep()


def main_step():
    time_tuple = utime.localtime()
    if time_tuple[3] % 3 == 0:
        adc = m.ADC(0)
        moisture_level = adc.read()
        watering = 0
        if moisture_level > config.TRIGGER_SOIL:
            pump(config.PUMP_SEC)
            watering = 1
        if connect_wifi():
            send_values([moisture_level, watering])