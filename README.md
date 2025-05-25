# Документация проекта

## Авторы
Голышев Артём<br>
Федотюк Екатерина<br>
Бажал Дарий<br>
Ян Цзунхао<br>
Гуань Хаоюань

## Руководитель
Куклин Егор Вадимович

## Описание проекта
Цель проекта — разработка SCADA-системы для визуализации и управления моделью промышленной линии по обработке и фасовке фишек, включающей 7 программируемых логических контроллеров (ПЛК). SCADA-система реализована в среде MasterSCADA 4D и обеспечивает интерфейс оператора (ЧМИ) для мониторинга состояния установки, управления ею, а также отображения данных с контроллеров.

Дополнительно разработан OPC UA сервер на Python, который также выполняет роль преобразователя протокола. Он взаимодействует с ПЛК по протоколу Easy IP и распределяет полученную от них информацию в OPC UA теги. Для удобства развертывания и кроссплатформенности, были созданы Docker-контейнеры для OPC UA сервера и для masterscada runtime (masterplc), куда загружается проект SCADA-системы.

## Используемое ПО и протоколы
- FST 4.0
- MasterSCADA 4D
- Matrikon OPC Explorer
- UA Expert
- OPC DA
- OPC UA

## Оборудование станций
- [Disributing & Testing](https://github.com/fu1m3n/315_line_docs/blob/main/list_of_components/DISTRIBUTING_TESTING.md);
- [Processing & Handling](https://github.com/fu1m3n/315_line_docs/blob/main/list_of_components/PROCESSING_HANDLIND.md);
- [Handling & Sorting](https://github.com/fu1m3n/315_line_docs/blob/main/list_of_components/HANDLING_SORTING.md).

## Этапы разработки

### Проектирование интерфейса
1. Были спроектированы и реализованы пользовательские интерфейсы (окна) для каждой из шести подсистем установки. Интерфейсы включают в себя графические элементы, отображающие действия исполнительных механизмов и датчиков (например, вращение, сверление, наличие фишки и др.), а также навигационные элементы, позволяющие переключаться между экранами
2. Были выявлены необходимые теги, отражающие состояния оборудования, и произведена их привязка к соответствующим элементам интерфейса. Это обеспечило корректную визуализацию в SCADA по реальным сигналам, получаемым от контроллеров через OPC-сервер
3. Для каждой станции была написана управляющая логика на языке ST (Structured Text)
4. После настройки интерфейса и логики была выполнена проверка SCADA-системы в режиме подключения, который предоставляет MasterSCADA 4D. Это позволило убедиться в корректной работе визуальных компонентов и их связи с тегами

### Создание OPC UA сервера на Python
- Изучение спецификаций протокола EasyIP
- Написание формирователя запросов и парсера ответа в соответствии с требованиями протокола
- Написание серверной части программы
- Тестирование в работе с контроллером
- Распараллеливание программы для работы с несколькими контроллерами и тестирование

### Контейнеризация 
- Написание docker-файлов для обоих контейнеров
- Загрузка образов на Docker Hub
- Скачивание образов на ПК и загрузка SCADA-проекта в masterplc
- Запуск контейнеров на ПК для тестирования работоспособности

### Тестирование
- Проверка связи с сервером
- Проверка корректности отображения информации и функционирования ЧМИ

## Ожидаемые результаты
- Полноценная SCADA-система, отображающая текущие состояния всех участков линии:
  * Визуализация действий каждой из станций
  * Сбор статистики по фишкам (по цветам, количеству)
- Стабильный обмен данными между SCADA и контроллерами через OPC UA-сервер
- Упрощённый процесс развёртывания системы за счёт контейнеризации
- Подготовленная документация и демонстрационная среда

## Структура установки и SCADA

### Структура установки
Модель промышленной линии состоит из трёх станций, каждая из которых имеет две подстанции с отдельными ПЛК (Festo FEC FC640). Вся установка построена на базе оборудования Festo и используется для демонстрации процессов автоматизации.

#### Станция 1
*Distributing*:
- Магазин с фишками
- Манипулятор для переноса фишек на платформу

*Testing*:
- Платформа с датчиками и толкателями:
    * Определение цвета
    * Сортировка: черные — в буфер, красные и серебристые — на тележку
- Скат для перемещения фишек на тележку
- Скат для бракованных фишек

#### Станция 2
*Handling*:
- Манипулятор для захвата и переноса фишек

*Processing*:
- Круговой конвейер
- Датчик положения фишки
- Сверлильный станок

#### Станция 3
*Handling 2*:
- Манипулятор для переноса фишек

*Sorting*:
- Конвейер
- Скаты по цветам
- Сбрасыватели для направления фишек

Контроллеры каждой станции обмениваются данными с главным контроллером, который координирует их работу, а также отвечает за управление конвейером, проходящим через всю установку.

### Логика экранов SCADA
Каждый экран содержит названия подсекций станции и 2 кнопки для навигации между окнами системы. По клику мыши происходит переход на следующее/предыдущее окно.

#### First Station (Distributing + Testing)
Отображение действий:
- Наличие фишки в магазин
- Перенос фишки на платформу
- Подъём/спуск платформы
- Сброс фишки (на тележку или в буфер)

Индикаторы:
- Тележка подъехала
- Обнаружена бракованная фишка

Используемые теги:
- `DISTR_AW0` – перенос фишки
- `DISTR_A0_0` – фишка в магазине
- `TESTING_AW0` – передвижение платформы
- `TESTING_EW0` – сброс фишек на тележку/ в буфер; определение бракованных фишек
- `CONVEER_EW10` – тележка у станции

<img width="936" alt="image" src="https://github.com/user-attachments/assets/bc05d22b-2e0c-4ea7-bd4d-3d7ca0713744" />

<img width="936" alt="image" src="https://github.com/user-attachments/assets/e81510bf-1513-4305-a22d-619451ef3112" />

#### Second Station (Handling + Processing)
Отображение действий:
- Перенос фишки
- Вращение платформы
- Детекция перевёрнутой фишки
- Сверление

Индикаторы:
- Наличие тележки

Используемые теги:
- `HANDLING_TV0` – перенос фишки
- `PROCESSING_AW0` – вращение платформы; проверка положения; сверление
- `PROCESSING_EW0` – тележка у станции

<img width="936" alt="image" src="https://github.com/user-attachments/assets/0d2c3faa-7118-4524-88b0-c703278764b5" />

<img width="936" alt="image" src="https://github.com/user-attachments/assets/87f162e1-6d6e-489c-95bf-c56bd4c3ad47" />


#### Third Station (Handling 2 + Sorting)
Отображение действий:
- Перенос фишки
- Визуализация сортировки

Индикаторы:
- Цвет фишки: красный, серебристый
- Счётчик фишек по цветам
- Тележка подъехала

Используемые теги:
- `HANDLING2_TV0` – перенос фишки
- `SORTING_EW0` – цвет фишки; сортировка
- `CONVEER_EW14` – тележка у станции

<img width="936" alt="image" src="https://github.com/user-attachments/assets/986a7e45-af29-41ab-a31f-5d88abaaecff" />

<img width="936" alt="image" src="https://github.com/user-attachments/assets/82a8ae3b-7c37-4d4d-90f3-3eaaab714ede" />

## Структура и реализация OPC UA сервера

### Введение
Код программы на языке Python находится [здесь](https://github.com/fu1m3n/315_line_docs/blob/main/OPC%20UA%20server%20for%20EasyIP).

При создании данной программы информация о протоколе Easy IP бралась из следующих файлов документации:
- [Automating_with_FST](https://github.com/fu1m3n/315_line_docs/blob/main/Docs/Automating_with_FST.pdf);
- [Festo Software Tool_1](https://github.com/fu1m3n/315_line_docs/blob/main/Docs/Festo%20Software%20Tool_1.pdf);
- [Festo Software Tool_2](https://github.com/fu1m3n/315_line_docs/blob/main/Docs/Festo%20Software%20Tool_2.pdf).

В качестве информационного ресурса и основы для парсера использовался код открытой библиотеки EasyIP на Python, находящийся в репозитории по ссылке https://github.com/birchroad/fstlib/tree/master/src.

> [!IMPORTANT]
> Для данной версии севера используется библиотека `opcua`, так как c при реализации с библиотекой `asyncua` не получилось корректно работать с MasterSCADA 4D 1.3 (при компиляции проекта возникала ошибка «отказ внешних устройств», хотя теги выгружались корректно). В будущем рекомендуется пересмотреть используемую библиотеку в сторону асинхронной, так как это должно быть более производительным решением. Также в данной версии не предусмотрена обработка запроса на запись информации в тег (переменную контроллера), а только запрос информации от контроллеров, сложность здесь заключается не в формировании соответствующего пакета, а в организации работы программы по запросу от MasterSCADA. У нас не было времени на реализацию этого, так что настоятельно рекомендуется это сделать.

### Разбор и пояснения к коду
Далее будут поясняться нетривиальные части кода, смысл которых непрозрачен исходя из комментария к строчкам.

#### 1. Конфигурация контроллеров
Список, содержащий имена и сетевые параметры (IP-адрес и порт) для контроллеров, с которыми будет работать сервер. Каждый контроллер будет опрашиваться отдельно в своём потоке.

```python
CONTROLLERS = [
    {"name": "DISTRIBUTING", "ip": "10.1.1.1", "port": 995},
    {"name": "TESTING", "ip": "10.1.1.2", "port": 995},
    {"name": "PROCESSING", "ip": "10.1.1.3", "port": 995},
    {"name": "HANDLING", "ip": "10.1.1.4", "port": 995}
    {"name": "CONVEER", "ip": "10.1.1.6", "port": 995},
    {"name": "SORTING", "ip": "10.1.1.7", "port": 995},
    {"name": "HANDLING2", "ip": "10.1.1.8", "port": 995}
]
```
#### 2.	Класс EasyIPPacket
Этот класс реализует структуру пакета протокола Festo EasyIP. Он позволяет упаковывать запросы и распаковывать полученные от контроллера пакеты.

Формат заголовка: `HEADER_FORMAT = "<B B H H B B H H B B H H H"`.

Описание структуры заголовка пакета EasyIP:
- `B` — unsigned char (1 байт);
- `H` — unsigned short (2 байта).

Методы:
- `__init__()` — инициализирует поля заголовка и загружает данные, если передан пакет;
- `unpack(data)` — распаковывает заголовок и payload из пришедших байт;
- `pack()` — собирает заголовок и payload в бинарный пакет для отправки.

```python
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
```

#### 3.	Формирование имен тегов
Функция формирует имя тега OPC UA на основе типа данных EasyIP и смещения (`offset` показывает смещение байта данных в общей пришедшей пачке). Она содержит `type_map`, где названию тега ставится в соответствие номер его `data_type`, указываемого в пакете запроса. Это позволяет корректно именовать теги при парсинге пакета, присланного контроллером, по полученным в нем данным.

```python
def tag_name_from_type_offset(data_type, offset):
    type_map = {1: "MW", 2: "EW", 3: "AW", 5: "TV"}
    prefix = type_map.get(data_type, f"T{data_type}")
    return f"{prefix}{offset}"
```
#### 4.	Формирование запроса
Функция формирует запрос EasyIP для чтения 64 слов одного типа данных (MW/EW/AW/TV) начиная с адреса 0.
- `counter` — счётчик запросов;
- `index1` — индекс (обычно 0);
- `req_type` — запрашиваемый тип данных (имеется в виду `data_type` тега).

```python
def build_easyip_request(counter, index1, req_type):
    packet = EasyIPPacket()
    packet.flags = 0x00
    packet.counter = counter
    packet.index1 = index1
    packet.reqdata_type = req_type
    packet.reqdata_size = 64
    packet.reqdata_offset_server = 0
    return packet.pack()
```
#### 5.	Парсинг полученного ответа
В этой функции происходит разбор пакета. Payload считывается в цикле в соответствии с запрашиваемым количеством слов (по полю `reqdata_size`). В этом же цикле вносится информация из заголовка о типе данных и смещении конкретного байта для последующего формирования названия тега. Всё это записывается в список `values`.
```python
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
```
#### 6.	Функция опроса контроллера
Функция работает в бесконечном цикле, постоянно опрашивая контроллер.

- `with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:` — создаёт сокет для работы с UDP портом.

Затем в цикле `for` осуществляется перебор требуемых типов данных, для которых будут формироваться запросы. Потом формируется запрос и отправляется в соответствии с адресом и портом контроллера.

- `data, _ = sock.recvfrom(2048)` – получение ответа от контроллера.

Затем ответ парсится с помощью функции в список `values`. Далее в цикле формируются имена тегов в соответствии с полученными данными.

Далее начинается бесконечный цикл опроса. Конструкция `try except` обрабатывает ошибку: отсутствие ответа от контроллера в течение заданного времени.

- `opc_tags[full_tag].set_value(ua.Variant(value, ua.VariantType.UInt16))` – здесь обновляется значение тега на сервере.

Эта часть кода необходима для получения данных о конкретных битах из байт данных от контроллера, так как они тоже используются как переменные. Биты А0-А15 соответствуют входному слову AW0, которое состоит из 2-х байт. Будущим студентам рекомендуется вынести эту процедуру в отдельную функцию.

```python
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
```
#### 7. Запуск OPC UA сервера и создание тегов
- `server = Server()` – создается объект сервера.

Далее задается адрес сервера и регистрируется собственное пространство имен.
- `objects = server.get_objects_node()` - Получается папка `objects`, где будут создаваться теги и группы (по контроллерам).
- `opc_tags = {}` - создается словарь для хранения тегов.

Далее идет цикл для всех контроллеров, которые были заданы в конфигурации.
- `ctrl_node = objects.add_object(idx, controller["name"])` – создается папка в OPC UA сервере с именем контроллера, внутри которой уже будут добавляться его теги.

Далее в цикле для всех `data_type` создается по 64 тега (все это только для одного контроллера).
- `node = ctrl_node.add_variable(idx, tag_name, 0, ua.VariantType.UInt16)` – создается переменная (тег).
- `opc_tags[full_tag] = node` – добавляется ссылка на тег в словарь тегов `opc_tags`.

Далее идет отдельное создание переменных под биты А.
- `threading.Thread(target=poll_controller, args=(controller, opc_tags, idx, ctrl_node), daemon=True).start()` – здесь самое важное: для каждого контроллера запускается отдельный поток с опросом, который выполняет функцию `poll_controller`. Данный поток завершается вместе с основным потоком (процессом).
- `server.start()` - запускает OPC UA сервер. Сервер начинает слушать по заданному адресу и порту.

```python
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
```
#### 8.	Главная функция
Запускает сервер и оставляет главный поток в бесконечном цикле. В это время сервер работает, параллельно опрашивая несколько контроллеров.

```python
if __name__ == "__main__":
    start_opcua_server()
    while True:
        time.sleep(1)
```
