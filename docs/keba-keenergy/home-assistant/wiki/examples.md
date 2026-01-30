# Examples

## Blueprints

### Set away date range

Sets the away date range of a KEBA KeEnergy control unit based on a calendar event when a specific keyword is found
in the event description.

![Blueprint to set away mode](../../../assets/blueprint-set-away-mode.png)
[Download blueprint](https://raw.githubusercontent.com/superbox-dev/keba_keenergy/refs/heads/main/blueprints/automation/keba_keenergy/set_away_date_range.yaml)

## Templates

A template sensor to get the delta from the heatpump source input and output:

```yaml
template:
  - sensor:
    - name: Heat pump source temperature delta
      unique_id: heat_pump_source_temperature_delta
      state: >-
        {% set input = states("sensor.keba_keenergy_12345678_heat_pump_source_input_temperature")|float(0) %}
        {% set output = states("sensor.keba_keenergy_12345678_heat_pump_source_output_temperature")|float(0) %}
        {{ (input - output)|round(2) }}
      icon: mdi:thermometer
      unit_of_measurement: °C
      device_class: temperature
      state_class: measurement
```

A template sensor to get the delta from the heat pump flow and return flow. This is also posible with the flow
and return flow sensor from the heat circuits (if available).

```yaml
template:
  - sensor:
    - name: Heat pump flow and return temperature delta
      unique_id: heat_pump_flow_and_return_temperature_delta
      state: >-
        {% set flow = states("sensor.keba_keenergy_12345678_heat_pump_flow_temperature")|float(0) %}
        {% set return_flow = states("sensor.keba_keenergy_12345678_heat_pump_return_flow_temperature")|float(0) %}
        {{ (flow - return_flow)|round(2) }}
      icon: mdi:thermometer
      unit_of_measurement: °C
      device_class: temperature
      state_class: measurement
```

## Visualizations

All visualisations required the [Lovelace Mini Graph Card](https://github.com/kalkih/mini-graph-card).

### Outdoor temperature

An awesome chart for your outdoor temperature. Charts line color is based on outdoor temperature value.

![Outdoor temperature chart](../../../assets/chart-outdoor-temperature.png)

```yaml
- type: custom:mini-graph-card
  name: Outdoor temperature
  entities:
    - entity: sensor.keba_keenergy_12345678_outdoor_temperature
      name: Temperature
  line_width: 3
  hour24: true
  points_per_hour: 12
  show:
    labels: false
    extrema: true
  color_thresholds:
    - value: -10
      color: "#0020E7"
    - value: 0
      color: "#008EE7"
    - value: 10
      color: "#00E7DD"
    - value: 20
      color: "#00E758"
    - value: 25
      color: "#BEE700"
    - value: 30
      color: "#E79700"
    - value: 35
      color: "#E73700"
```
