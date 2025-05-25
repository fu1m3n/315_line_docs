# -*- coding: utf-8 -*-
import socket
import struct
import time
from opcua import Server, ua
import threading

# Конфиг контроллеров: имя и IP-адрес
CONTROLLERS = [
    {"name": "DISTRIBUTING", "ip": "10.1.1.1", "port": 995},
    {"name": "TESTING", "ip": "10.1.1.2", "port": 995},
    {"name": "PROCESSING", "ip": "10.1.1.3", "port": 995},
    {"name": "HANDLING", "ip": "10.1.1.4", "port": 995}
]

POLL_INTERVAL = 0.01  # период опроса в секундах

# EasyIP Packet класс
class EasyIPPacket:
    HEADER_FORMAT = "<B B H H B B H H B B H H H"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, data=None):
        self.flags = 0
        self.error = 0
        self.counter = 0
        self.index1 = 0
        self.spare1 = 0
        self.senddata_type = 0
        self.senddata_size = 0
        self.senddata_offset = 0
        self.spare2 = 0
        self.reqdata_type = 0
        self.reqdata_size = 0
        self.reqdata_offset_server = 0
        self.reqdata_offset_client = 0
        self.payload = b""
        if data:
            self.unpack(data)

    def unpack(self, data):
        header = struct.unpack(self.HEADER_FORMAT, data[:self.HEADER_SIZE])
        (self.flags, self.error, self.counter, self.index1, self.spare1,
         self.senddata_type, self.senddata_size, self.senddata_offset,
         self.spare2, self.reqdata_type, self.reqdata_size,
         self.reqdata_offset_server, self.reqdata_offset_client) = header
        self.payload = data[self.HEADER_SIZE:]

    def pack(self):
        header = struct.pack(self.HEADER_FORMAT,
                             self.flags, self.error, self.counter, self.index1, self.spare1,
                             self.senddata_type, self.senddata_size, self.senddata_offset,
                             self.spare2, self.reqdata_type, self.reqdata_size,
                             self.reqdata_offset_server, self.reqdata_offset_client)
        return header + self.payload

# функция для формирования имени тега по типу и смещению
def tag_name_from_type_offset(data_type, offset):
    type_map = {1: "MW", 2: "EW", 3: "AW", 5: "TV"}
    prefix = type_map.get(data_type, f"T{data_type}")
    return f"{prefix}{offset}"

# формирование запроса
def build_easyip_request(counter, index1, req_type):
    packet = EasyIPPacket()
    packet.flags = 0x00
    packet.counter = counter
    packet.index1 = index1
    packet.reqdata_type = req_type
    packet.reqdata_size = 64
    packet.reqdata_offset_server = 0
    return packet.pack()

# парсинг полученного пакета
def parse_easyip_packet(data):
    packet = EasyIPPacket(data)
    values = []
    for i in range(packet.reqdata_size):
        byte_index = i * 2
        if byte_index + 2 <= len(packet.payload):
            value = struct.unpack_from("<H", packet.payload, byte_index)[0]
            position = (packet.reqdata_type, packet.reqdata_offset_server + i)
            values.append((position, value))
    return values

# функция опроса контроллера
def poll_controller(controller, opc_tags, idx, ctrl_node):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1.0)
        counter = 1
        while True:
            try:
                for data_type in [1, 2, 3, 5]:  # 1=MW, 2=EW, 3=AW, 5=TV
                    request = build_easyip_request(counter, 0, data_type)
                    sock.sendto(request, (controller["ip"], controller["port"]))
                    data, _ = sock.recvfrom(2048)
                    values = parse_easyip_packet(data)

                    for (pos, value) in values:
                        d_type, d_offset = pos
                        tag_name = tag_name_from_type_offset(d_type, d_offset)
                        full_tag = f"{controller['name']}_{tag_name}"

                        if full_tag in opc_tags:
                            opc_tags[full_tag].set_value(ua.Variant(value, ua.VariantType.UInt16))

                        # если это AW0 — раскладываем биты A0…A15
                        if d_type == 3 and d_offset == 0:
                            for bit in range(16):
                                bit_value = bool((value >> bit) & 1)
                                bit_tag = f"A{bit}"
                                full_bit_tag = f"{controller['name']}_{bit_tag}"
                                if full_bit_tag in opc_tags:
                                    opc_tags[full_bit_tag].set_value(ua.Variant(bit_value, ua.VariantType.Boolean))

                counter += 1

            except socket.timeout:
                print(f"Timeout: no response from {controller['name']}")
            time.sleep(POLL_INTERVAL)

# запуск OPC UA сервера и создание тегов
def start_opcua_server():
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840")
    uri = "http://easyip.festo/opcua/"
    idx = server.register_namespace(uri)
    objects = server.get_objects_node()

    opc_tags = {}
    for controller in CONTROLLERS:
        ctrl_node = objects.add_object(idx, controller["name"])

        for data_type in [1, 2, 3, 5]:
            for offset in range(64):
                tag_name = tag_name_from_type_offset(data_type, offset)
                full_tag = f"{controller['name']}_{tag_name}"
                node = ctrl_node.add_variable(idx, tag_name, 0, ua.VariantType.UInt16)
                node.set_writable()
                opc_tags[full_tag] = node

        # создаём биты A0…A15
        for bit in range(16):
            bit_tag = f"A{bit}"
            full_bit_tag = f"{controller['name']}_{bit_tag}"
            node = ctrl_node.add_variable(idx, bit_tag, False, ua.VariantType.Boolean)
            node.set_writable()
            opc_tags[full_bit_tag] = node

        threading.Thread(target=poll_controller, args=(controller, opc_tags, idx, ctrl_node), daemon=True).start()

    server.start()
    print("OPC UA server running at opc.tcp://0.0.0.0:4840")

if __name__ == "__main__":
    start_opcua_server()
    while True:
        time.sleep(1)

