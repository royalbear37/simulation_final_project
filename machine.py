from database import Database



resources = Database(user="11302_SIM",
                        password="11302",
                        hostname="140.113.59.168")

resources.connect()

query = resources.execute_query(
    "SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_1")

query2 = resources.execute_query(
    "SELECT * FROM SIM_STUDENT. SIM_ALLOCATE_DISPATCH_2")

resources.close()

# print("Query 1 results:", query)
# print("Query 2 results:", query2)


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

#測試用 簡單易讀
# ETCH_machines = [(f"ETCH_{i}", 17, 3) for i in range(1, 17)]
# PHOTO_machines = [(f"PHOTO_{i}", 17, 3) for i in range(1, 19)]
# TF_machines = [(f"TF_{i}", 30, 4) for i in range(1, 19)]

#寫入oracle
def write_to_oracle(results):
    resources = Database(user="TEAM_13",
                        password="team13",
                        hostname="140.113.59.168")
    resources.connect()
    cursor = resources.connection.cursor()
    
    for result in results:
        instance = result[0]
        average_idle_time = result[1]
        staff_in_area1 = result[2]
        staff_in_area2 = result[3]
        staff_in_area3 = result[4]
        dispatch_in_area1 = result[5]
        dispatch_in_area2 = result[6]
        dispatch_in_area3 = result[7]

        cursor.execute("""
            INSERT INTO TEAM_13.RESULT_TEMPLATE (
                INSTANCE, AVERAGE_IDLE_TIME, STAFF_IN_AREA1, STAFF_IN_AREA2, STAFF_IN_AREA3,
                DISPATCH_IN_AREA1, DISPATCH_IN_AREA2, DISPATCH_IN_AREA3
            ) VALUES (
                :instance, :average_idle_time, :staff_in_area1, :staff_in_area2, :staff_in_area3,
                :dispatch_in_area1, :dispatch_in_area2, :dispatch_in_area3
            )
        """, {
            "instance": instance,
            "average_idle_time": average_idle_time,
            "staff_in_area1": staff_in_area1,
            "staff_in_area2": staff_in_area2,
            "staff_in_area3": staff_in_area3,
            "dispatch_in_area1": dispatch_in_area1,
            "dispatch_in_area2": dispatch_in_area2,
            "dispatch_in_area3": dispatch_in_area3
        })

    resources.connection.commit()
    cursor.close()
    resources.close()