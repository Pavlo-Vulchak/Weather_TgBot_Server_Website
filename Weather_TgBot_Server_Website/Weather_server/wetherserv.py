import paho.mqtt.client as mqtt
import time
import json
from os import environ
import logging

FORMAT = '%(asctime)-15s %(name)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logging.basicConfig(level=logging.ERROR, format=FORMAT)
logger = logging.getLogger()

select_device_weather_bot = ""
select_device_weather_web = ""
device_list = []
status_device = {}
status_device_timer = {}
history = {}
timer = 600 

# TTN credentials
ttn_app_id = environ.get("TTN_APP_ID","define me")
ttn_tenant_id = environ.get("TTN_TENANT_ID","define me")
ttn_mqtt_username = ttn_app_id + "@" + ttn_tenant_id
ttn_mqtt_access_key = environ.get("TTN_ACCESS_KEY","define me")

# TTN server details
ttn_mqtt_broker_address = environ.get("TTN_MQTT_BROKER_URL","define me")
ttn_mqtt_broker_port = int(environ.get("TTN_MQTT_BROKER_PORT","define me"))

weather_bot_mqtt_broker_url = environ.get("WEATHER_MQTT_BROKER_URL","define me")
weather_bot_mqtt_username = environ.get("WEATHER_MQTT_USERNAME","define me")
weather_bot_mqtt_password = environ.get("WEATHER_MQTT_PASSWORD","define me")
weather_bot_mqtt_topic_sendTgBot = "measurements/WeatherTgBot"
weather_bot_mqtt_topic_sendWebSite = "measurements/WeatherWebSite"
weather_bot_mqtt_topic_ReciveRequest = "measurements/RequestSetting"
weather_bot_mqtt_broker_port = int(environ.get("WEATHER_MQTT_BROKER_PORT","define me"))

# Callback when the client receives a CONNACK response from the server
def on_connect_TTN(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to TTN")
        # Subscribe to the TTN application's uplink topic
        client.subscribe(f"v3/{ttn_app_id}@{ttn_tenant_id}/devices/+/up")
    else:
        logger.error("Connection to TTN failed. RC:", rc)

def on_connect_wether_bot_mqtt(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to Bot")
        client_mqtt_weather_bot_web.subscribe(weather_bot_mqtt_topic_ReciveRequest)
    else:
        logger.error("Connection to Bot failed. RC:", rc)



# Callback when a message is received from the TTN application's uplink topic
def on_message_TTN(client, userdata, msg):
    global select_device_weather_bot

    logger.info("Received message on topic {}:".format(msg.topic))
    logger.info(json.dumps(json.loads(msg.payload), indent=2))
    receive_msg = json.loads(msg.payload)
    
    history_data_weather = {
        "temperature": receive_msg["uplink_message"]["decoded_payload"]["temperature"],
        "humidity": receive_msg["uplink_message"]["decoded_payload"]["humidity"],
        "pressure": receive_msg["uplink_message"]["decoded_payload"]["pressure_real"],
        "other_info": {
            "absolut_pressure": receive_msg["uplink_message"]["decoded_payload"]["pressure"],
            "altitude": receive_msg["uplink_message"]["decoded_payload"]["real_altitude"],
            "rssi": receive_msg["uplink_message"]["rx_metadata"][0]["rssi"]
        },
        "device": receive_msg["end_device_ids"]["device_id"],
        "time_recived": receive_msg["received_at"]
    }
    #додавання даних для відповідного пристрою у словник history з сортування від старших до новішших
    # Допис попередніх даних для пристрою в масив
    try:
        tmp_history = history[history_data_weather["device"]]
    except KeyError:
        tmp_history = []
    # Додавання нових даних
    tmp_history.append({
            "temperature": history_data_weather["temperature"],
            "humidity": history_data_weather["humidity"],
            "pressure": history_data_weather["pressure"],
            "other_info": {
                "absolut_pressure": history_data_weather["other_info"]["absolut_pressure"],
                "altitude": history_data_weather["other_info"]["altitude"],
                "rssi": history_data_weather["other_info"]["rssi"]
            },
            "time_recived": history_data_weather["time_recived"]
        })
    history.update({
        history_data_weather["device"]: tmp_history
    })
    data_weatherBot = {
        "temperature": history_data_weather["temperature"],
        "humidity": history_data_weather["humidity"],
        "pressure": history_data_weather["pressure"]
    }

    status_device.update({
        history_data_weather["device"]: "Online"
    })
    status_device_timer.update({
        history_data_weather["device"]: timer
    })
    #print("History DB:")
    #print(json.dumps(history, indent=2))
    #print(len(history[history_data_weather["device"]]))
    try:
        device_list.index(history_data_weather["device"])
    except ValueError:
        device_list.append(history_data_weather["device"])

    if(select_device_weather_bot == ""):
        select_device_weather_bot = history_data_weather["device"]
        client_mqtt_weather_bot_web.publish(weather_bot_mqtt_topic_sendTgBot, json.dumps(data_weatherBot,indent=4))
        #client_mqtt_weather_bot_web.publish(weather_bot_mqtt_topic_sendWebSite, json.dumps(data_weatherBot,indent=4))
    elif(select_device_weather_bot == history_data_weather["device"]):
        client_mqtt_weather_bot_web.publish(weather_bot_mqtt_topic_sendTgBot, json.dumps(data_weatherBot,indent=4))
        #client_mqtt_weather_bot_web.publish(weather_bot_mqtt_topic_sendWebSite, json.dumps(data_weatherBot,indent=4))

def on_message_Wether_BotWeb(client, userdata, msg):
    global select_device_weather_bot
    logger.info("Received message on topic {}:".format(msg.topic))
    receive_msg = json.loads(msg.payload)
    sendler = receive_msg["sendler"]
    command_request = receive_msg["requestCommand"]
    if(command_request == "information"):
        if(select_device_weather_bot != ""):
            oldnew_data = history[select_device_weather_bot][len(history[select_device_weather_bot]) - 1]
            response_BotWeb = {
                "absolut_pressure": oldnew_data["other_info"]["absolut_pressure"],
                "altitude": oldnew_data["other_info"]["altitude"],
                "selected_device": select_device_weather_bot,
                "rssi": oldnew_data["other_info"]["rssi"],
                "timestep": oldnew_data["time_recived"],
                "status": status_device[select_device_weather_bot]
            }
        else:
            response_BotWeb = {
                "absolut_pressure": "nan",
                "altitude": "nan",
                "selected_device": "no_selected",
                "rssi": "nan",
                "timestep": "nan",
                "status": "no_device"
            }
    elif(command_request == "listDevices"):
        listdevice = []
        for device in device_list:
            listdevice.append({
                "name": device,
                "status": status_device[device]
            })
        response_BotWeb = {
            "list_devices": listdevice
        }
    elif(command_request == "changeDevice"):
        select_device_weather_bot = receive_msg["data"]
        oldnew_data = history[select_device_weather_bot][len(history[select_device_weather_bot]) - 1]
        response_BotWeb = {
            "temperature": oldnew_data["temperature"],
            "humidity": oldnew_data["humidity"],
            "pressure": oldnew_data["pressure"]
        }
    elif(command_request == "sendMessage"):
        oldnew_data = history[select_device_weather_bot][len(history[select_device_weather_bot]) - 1] 
        str_data = receive_msg["data"]
        response_BotWeb = {
            "temperature": oldnew_data["temperature"],
            "humidity": oldnew_data["humidity"],
            "pressure": oldnew_data["pressure"],
            "message": str_data
        }

    if(sendler == "TgBot"):
        client_mqtt_weather_bot_web.publish(weather_bot_mqtt_topic_sendTgBot, json.dumps(response_BotWeb,indent=4))
    elif(sendler == "WebServ"):
        client_mqtt_weather_bot_web.publish(weather_bot_mqtt_topic_sendWebSite, json.dumps(response_BotWeb,indent=4))
    

# Create an MQTT client instance
client = mqtt.Client()

# Set the callbacks
client.on_connect = on_connect_TTN
client.on_message = on_message_TTN

# Set TTN credentials
client.username_pw_set(ttn_mqtt_username, password=ttn_mqtt_access_key)

# Connect to the TTN server
client.connect(ttn_mqtt_broker_address, ttn_mqtt_broker_port)

# Start the MQTT loop in a non-blocking way
client.loop_start()

client_mqtt_weather_bot_web = mqtt.Client()
client_mqtt_weather_bot_web.on_connect = on_connect_wether_bot_mqtt
client_mqtt_weather_bot_web.on_message = on_message_Wether_BotWeb
client_mqtt_weather_bot_web.tls_set()
client_mqtt_weather_bot_web.username_pw_set(weather_bot_mqtt_username, password=weather_bot_mqtt_password)
client_mqtt_weather_bot_web.connect(weather_bot_mqtt_broker_url, weather_bot_mqtt_broker_port)
client_mqtt_weather_bot_web.loop_start()

# Keep the script running
try:
    while True:
        for device in device_list:
            if(status_device[device] == "Online"):
                status_device_timer[device] = status_device_timer[device] - 1
                if(status_device_timer[device] == 0):
                    status_device[device] = "Offline"
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Disconnected. Exiting...")
    client_mqtt_weather_bot_web.disconnect()
    client_mqtt_weather_bot_web.loop_stop()
    client.disconnect()
    client.loop_stop()