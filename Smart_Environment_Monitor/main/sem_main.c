/* Simple Read Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "sdkconfig.h"
#include "esp_system.h"
#include "esp_log.h"

#include "dht11.h"
#include "esp_wifi_connect.h"
#include "esp_mqtt_connect.h"



struct dht11_reading sensor_dht_var;

void app_main()
{
    wifi_main();

    DHT11_init(GPIO_NUM_4);

    mqtt_main();
    while(1) {
        //printf("Temperature is %d \n", DHT11_read().temperature);
        //printf("Humidity is %d\n", DHT11_read().humidity);
        //printf("Status code is %d\n", DHT11_read().status);

        //int16_t temperature = 0;
        //int16_t humidity = 0;
        //sensor_dht_var=DHT11_read();
        //if (sensor_dht_var.status == ESP_OK) {
        //    ESP_LOGI("DHT", "Temperature: %d°C, Humidity: %d%%", sensor_dht_var.temperature, sensor_dht_var.humidity);
        //} else {
        //    ESP_LOGE("DHT", "Sensor error!");
        //}


        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
}