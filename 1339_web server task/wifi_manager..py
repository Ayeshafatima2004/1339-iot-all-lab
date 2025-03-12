import network
import time

def connect_to_wifi(ssid, password, timeout=10):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        print(f"Connecting to WiFi: {ssid} ...")
        sta.connect(ssid, password)
        start = time.ticks_ms()
        while not sta.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
                print("Connection timed out.")
                return None
            time.sleep(1)
    print("Connected to WiFi. IP:", sta.ifconfig()[0])
    return sta.ifconfig()[0]

def start_access_point(ap_ssid="ESP32-AP", ap_password="12345678"):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ap_ssid, password=ap_password, authmode=network.AUTH_WPA_WPA2_PSK)
    print(f"Access Point started with SSID: {ap_ssid} and Password: {ap_password}")
    print("AP IP address:", ap.ifconfig()[0])
    return ap.ifconfig()[0]

