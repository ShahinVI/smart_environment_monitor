#include "esp_mqtt_connect.h"
#include "dht11.h"
#include "env_passwords.h"

static const char *TAG2 = "MQTT_EXAMPLE";

uint32_t MQTT_CONNEECTED = 0;
static esp_mqtt_client_handle_t client;
static bool mqtt_connected = false;


/*
 * @brief Event handler registered to receive MQTT events
 *
 *  This function is called by the MQTT client event loop.
 *
 * @param handler_args user data registered to the event.
 * @param base Event base for the handler(always MQTT Base in this example).
 * @param event_id The id for the received event.
 * @param event_data The data for the event, esp_mqtt_event_handle_t.
 */
static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data) {
    esp_mqtt_event_handle_t event = event_data;
    esp_mqtt_client_handle_t client = event->client;
    int msg_id;

    switch ((esp_mqtt_event_id_t)event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG2, "MQTT_EVENT_CONNECTED");
            mqtt_connected = true;
            msg_id = esp_mqtt_client_subscribe(client, "/topic/test3", 0);
            ESP_LOGI(TAG2, "sent subscribe successful, msg_id=%d", msg_id);
            break;
        case MQTT_EVENT_DISCONNECTED:
            ESP_LOGI(TAG2, "MQTT_EVENT_DISCONNECTED");
            mqtt_connected = false;
            break;
        case MQTT_EVENT_SUBSCRIBED:
            ESP_LOGI(TAG2, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
            break;
        case MQTT_EVENT_PUBLISHED:
            ESP_LOGI(TAG2, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
            break;
        case MQTT_EVENT_DATA:
            ESP_LOGI(TAG2, "MQTT_EVENT_DATA");
            printf("TOPIC=%.*s\r\n", event->topic_len, event->topic);
            printf("DATA=%.*s\r\n", event->data_len, event->data);
            break;
        case MQTT_EVENT_ERROR:
            ESP_LOGI(TAG2, "MQTT_EVENT_ERROR");
            break;
        default:
            ESP_LOGI(TAG2, "Other event id:%d", event->event_id);
            break;
    }
}

static void mqtt_app_start()
{
    esp_mqtt_client_config_t mqttConfig = {
            .broker = {
                    .address = {
                            .uri = CONFIG_BROKER_URI//"mqtt://192.168.0.1:1883"
                    }
            }
    };

    client = esp_mqtt_client_init(&mqttConfig);
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler, client);
    esp_mqtt_client_start(client);
}

void Publisher_Task(void *params)
{
    while (1) {
        if (mqtt_connected) {
            if (DHT11_read().status == ESP_OK) {
                char payload[50];
                snprintf(payload, sizeof(payload), "Temperature: %d°C, Humidity: %d%%", DHT11_read().temperature, DHT11_read().humidity);
                esp_mqtt_client_publish(client, "/topic/esp32/sensor_data", payload, 0, 0, 0);
            } else {
                ESP_LOGE(TAG2, "Sensor read error!");
            }
        }
        vTaskDelay(15000 / portTICK_PERIOD_MS);
    }
}

void mqtt_main(void)
{
    mqtt_app_start();
    xTaskCreate(Publisher_Task, "Publisher_Task", 1024 * 5, NULL, 5, NULL);
}