"""Support for sensors exposed by the DR-JC03 BMS through RS485."""

from .const import (
    SENSOR_KEY_SOH,
    SENSOR_KEY_SOC,
    SENSOR_KEY_ENERGY,
    SENSOR_KEY_CURRENT,
    SENSOR_KEY_VOLTAGE,
    SENSOR_KEY_CELL_VOLTAGE,
    SENSOR_KEY_ENV_TEMP,
    SENSOR_KEY_CELL_TEMP,
    SENSOR_KEY_MOS_TEMP,
    SENSOR_KEY_TEMP,

    WAIT_TIME,
)

from asyncio import (
    create_task,
    sleep,
    wait_for,

    IncompleteReadError,
    LimitOverrunError,

    StreamReader,
    StreamWriter,
)
import logging

_LOGGER = logging.getLogger(__name__)

payloads = [
    "~22014A42E00201FD28\r",
    "~22014A42E00201FD28\r",
    "~22014A42E00201FD28\r", # Try 3 times the normal request, maybe it was just a fragmented packet.
    "~22014A4D0000FD8E\r", # Use 3 different requests like the original Windows software is doing (maybe BMS reset?).
    "~22014A510000FDA0\r",
    "~22014A47E00201FD23\r", # Start from the beginning after this.
]

def chksum_data(str):
    result = 0
    for datacheck in str:
        result = result + ord(datacheck)
    result = result ^ 0xFFFF
    return result + 1

def Lchksum(value):
    value = value & 0x0FFF
    n1 = value & 0xF
    n2 = (value >> 4) & 0xF
    n3 = (value >> 8) & 0xF
    chksum = ((n1 + n2 + n3) & 0xF) ^ 0xF
    chksum = chksum + 1
    return value + (chksum << 12)

def process_data(data):
    if len(data) < 10:
        _LOGGER.error("Invalid data length.")
        return

    received_chksum = int(data[-4:], 16)
    calc_chksum = chksum_data(data[2:-4])

    if calc_chksum != received_chksum:
        _LOGGER.error("Checksum error. Calculated: {}, Received: {}".format(calc_chksum, received_chksum))
        return

    _LOGGER.debug("Checksum is ok.")

    data = data[:-4]
    for i in range(0, len(data), 4):
        _LOGGER.debug("Received 4 bytes of data: " + data[i:i+4])

def CID2_decode(CID2):
    if CID2 == '00':
        _LOGGER.debug("CID2 response ok.")
        return 0
    elif CID2 == '01':
        _LOGGER.error("VER error.")
    elif CID2 == '02':
        _LOGGER.error("CHKSUM error.")
    elif CID2 == '03':
        _LOGGER.error("LCHKSUM error.")
    elif CID2 == '04':
        _LOGGER.error("CID2 invalid.")
    elif CID2 == '05':
        _LOGGER.error("Command format error.")
    elif CID2 == '06':
        _LOGGER.error("INFO data invalid.")
    elif CID2 == '90':
        _LOGGER.error("ADR error.")
    elif CID2 == '91':
        _LOGGER.error("Battery communication error.")

    return -1

def extract_battery_info(data):
    voltage = int(data[6:10], base=16)
    capacity = int(data[124:128], base=16)

    info = {}

    info[SENSOR_KEY_SOH] = int(data[114:118], base=16) / 1
    info[SENSOR_KEY_SOC] = int(data[2:6], base=16) / 100
    info[SENSOR_KEY_ENERGY] = voltage * capacity / 100 / 100 / 1000
    info[SENSOR_KEY_CURRENT] = int(data[106:110], base=16)
    info[SENSOR_KEY_VOLTAGE] = voltage / 100
    info[SENSOR_KEY_ENV_TEMP] = int(data[76:80], base=16) / 10
    info[SENSOR_KEY_CELL_TEMP] = int(data[80:84], base=16) / 10
    info[SENSOR_KEY_MOS_TEMP] = int(data[84:88], base=16) / 10
    info[SENSOR_KEY_TEMP.format(1)] = int(data[90:94], base=16) / 10
    info[SENSOR_KEY_TEMP.format(2)] = int(data[94:98], base=16) / 10
    info[SENSOR_KEY_TEMP.format(3)] = int(data[98:102], base=16) / 10
    info[SENSOR_KEY_TEMP.format(4)] = int(data[102:106], base=16) / 10

    if info[SENSOR_KEY_CURRENT] > 32767:
        info[SENSOR_KEY_CURRENT] = -(32768 - (info[SENSOR_KEY_CURRENT] - 32768))
    info[SENSOR_KEY_CURRENT] /= 100

    _LOGGER.debug("--------------------------------")
    _LOGGER.debug(f"SOH:       {info[SENSOR_KEY_SOH]}%")
    _LOGGER.debug(f"SOC:       {info[SENSOR_KEY_SOC]}%")
    _LOGGER.debug(f"Capacity:  {capacity / 100}Ah remaining")
    _LOGGER.debug(f"Energy:    {info[SENSOR_KEY_ENERGY]}kWh remaining")
    _LOGGER.debug(f"Current:   {info[SENSOR_KEY_CURRENT]}A")
    _LOGGER.debug(f"Voltage:   {info[SENSOR_KEY_VOLTAGE]}V")
    _LOGGER.debug(f"Env Temp:  {info[SENSOR_KEY_ENV_TEMP]}°C")
    _LOGGER.debug(f"Cell Temp: {info[SENSOR_KEY_CELL_TEMP]}°C")
    _LOGGER.debug(f"MOS Temp:  {info[SENSOR_KEY_MOS_TEMP]}°C")
    _LOGGER.debug(f"Temp 1:    {info[SENSOR_KEY_TEMP.format(1)]}°C")
    _LOGGER.debug(f"Temp 2:    {info[SENSOR_KEY_TEMP.format(2)]}°C")
    _LOGGER.debug(f"Temp 3:    {info[SENSOR_KEY_TEMP.format(3)]}°C")
    _LOGGER.debug(f"Temp 4:    {info[SENSOR_KEY_TEMP.format(4)]}°C")
    _LOGGER.debug("--------------------------------")

    for i in range(1, 17):
        info[SENSOR_KEY_CELL_VOLTAGE.format(i)] = int(data[(i - 1) * 4 + 12: i * 4 + 12], base=16) / 1000
        _LOGGER.debug(f"Cell {i}: {info[SENSOR_KEY_CELL_VOLTAGE.format(i)]}V")

    _LOGGER.debug("--------------------------------")

    return info

async def send_payload(stream: StreamWriter, payload: str):
    stream.write(data=payload.encode())
    await stream.drain()
    _LOGGER.debug(f"Request sent: {payload}")

async def recv_response(stream: StreamReader):
    try:
        buf = await stream.readuntil(b'\r')
    except (IncompleteReadError, LimitOverrunError) as e:
        _LOGGER.error(e)
        return None

    try:
        response = buf.decode()
    except Exception as e:
        _LOGGER.error(e)
        return None

    _LOGGER.debug(f"Response received: {response}")

    return response

async def get_info(in_stream: StreamReader, out_stream: StreamWriter):
    while True:
        try:
            if get_info.payload_index >= len(payloads):
                get_info.payload_index = 0
                return None
        except AttributeError:
            get_info.payload_index = 0

        task = create_task(send_payload(out_stream, payloads[get_info.payload_index]))
        try:
            await wait_for(task, WAIT_TIME)
        except TimeoutError as e:
            _LOGGER.error(e)
            return None

        task = create_task(recv_response(in_stream))
        try:
            rcv = await wait_for(task, WAIT_TIME)
        except TimeoutError as e:
            _LOGGER.error(e)
            return None

        if rcv is None:
            return None

        valid_data = True

        try:
            CID2 = rcv[7:9]
            if CID2_decode(CID2) == -1:
                valid_data = False
        except:
            valid_data = False

        try:
            LENID = int(rcv[9:13], base=16)
            length = LENID & 0x0FFF
            if Lchksum(length) == LENID:
                _LOGGER.debug("Data length ok.")
            else:
                _LOGGER.error("Data length error.")
                valid_data = False
        except:
            valid_data = False

        try:
            chksum = int(rcv[len(rcv)-5:], base=16)
            calculated_chksum = chksum_data(rcv[1:len(rcv)-5])
            if calculated_chksum == chksum:
                _LOGGER.debug("Checksum ok.")
            else:
                _LOGGER.error("Checksum error. Calculated: {}, Received: {}".format(calculated_chksum, chksum))
                valid_data = False

        except Exception as e:
            _LOGGER.error("Exception during checksum calculation: {}".format(e))
            valid_data = False

        if valid_data:
            data = rcv[13:len(rcv)-5]
            if len(data) >= 118:
                get_info.payload_index = 0
                return extract_battery_info(data)

        _LOGGER.error("Invalid data format")

        get_info.payload_index += 1

        await sleep(WAIT_TIME)
