import time
from logic import *

# фоновое задание для обновления доступности нюка
while True:
    all_nukes = get_all_nukes()
    for nuke in all_nukes:
        if ping_nuke(nuke.ip):
            sql_exchange_ping(nuke.id, "1")
        else:
            sql_exchange_ping(nuke.id, "0")
    time.sleep(5)

