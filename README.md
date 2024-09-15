# DR-JC03 BMS sensors support for Home Assistant

## Sensors

- State of health (SoH)
- State of charge (SoC)
- Energy
- Current
- Voltage
- Individual cell voltage (1-16)
- Environment temperature
- Cell temperature
- MOS temperature
- Temperatures 1-4

## Supported devices

This integration is only tested with a battery sold by PAPOOL on AliExpress.

According to [the reference project](https://github.com/christian1980nrw/DR-JC03-RS485-Switcher) a battery sold by another seller on the same platform turned out to be incompatible, despite seemingly having the same BMS.

## Installation

1. Clone/download the repository.
2. Copy the `dr_jc03` directory into your `custom_components` directory in your Home Assistant configuration directory.
3. Restart Home Assistant.

### Configuration

1. Go to the `Configuration` panel in your Home Assistant UI.
2. Press on `Integrations`.
3. Press the `+ ADD INTEGRATION` button.
4. Search for `DR-JC03` and press on it to set up the integration.

#### Options

- `entry_name`: The name of the virtual device that will provide all sensors. Default: **BMS**
- `serial_path`: The path to the serial device. Example: **/dev/ttyUSB0**
- `serial_baudrate`: The baudrate to use for the serial connection. Default: **9600**
- `update_interval`: The sensors update interval in seconds. Default: **5**
