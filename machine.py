from database import Database

print("Program started")

resources = Database(user="11302_SIM",
                        password="11302",
                        hostname="140.113.59.168")

resources.connect()

query = resources.execute_query(
    "SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_1")

query2 = resources.execute_query(
    "SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_2")

resources.close()

print("Query 1 results:", query)
print("Query 2 results:", query2)


layout = {}

for row in query:
    # print(row)
    instance = row[0]
    area = row[1]
    machine = row[2]
    processing_time = row[3]
    load_unload_time = row[4]

    if instance not in layout:
        layout[instance] = {}

    if area not in layout[instance]:
        layout[instance][area] = []

    layout[instance][area].append({
        "machine": machine,
        "processing_time": processing_time,
        "load_unload_time": load_unload_time
    })

ETCH_machines = [(d["machine"], d["processing_time"], d["load_unload_time"]) for d in layout["1"]["ETCH"]]
PHOTO_machines = [(d["machine"], d["processing_time"], d["load_unload_time"]) for d in layout["1"]["PHOTO"]]
TF_machines = [(d["machine"], d["processing_time"], d["load_unload_time"]) for d in layout["1"]["TF"]]
