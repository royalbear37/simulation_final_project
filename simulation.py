import heapq
from collections import deque

def simulate_idle_time(area_machines, num_staff, simulation_time):
    """
    模擬單一區域的機台排程與人力分配，回傳 idle time 總和。
    - area_machines: List of tuples (name, proc_time, load_time)
    - num_staff: 分配到該區的員工數
    - simulation_time: 模擬總長度（分鐘）
    """

    if num_staff == 0:
        return sum(max(0, simulation_time - proc) for _, proc, _ in area_machines)

    event_queue = []
    machine_status = {}
    idle_time_total = 0
    staff_available = num_staff
    waiting_queue = deque()

    for m_name, proc_time, load_time in area_machines:
        heapq.heappush(event_queue, (proc_time, 'done', m_name))  # 初始直接加工
        machine_status[m_name] = {'proc': proc_time, 'load': load_time}

    while event_queue:
        now, evt, mname = heapq.heappop(event_queue)
        if now > simulation_time:
            continue

        if evt == 'done':
            m = machine_status[mname]
            if staff_available > 0:
                staff_available -= 1
                load_done = now + m['load']
                if load_done <= simulation_time:
                    heapq.heappush(event_queue, (load_done, 'start_proc', mname))
                else:
                    idle_time_total += simulation_time - now
            else:
                waiting_queue.append((now, mname))

            heapq.heappush(event_queue, (now, 'assign_waiting', None))

        elif evt == 'start_proc':
            m = machine_status[mname]
            proc_done = now + m['proc']
            if proc_done <= simulation_time:
                heapq.heappush(event_queue, (proc_done, 'done', mname))
            staff_available += 1

            heapq.heappush(event_queue, (now, 'assign_waiting', None))

        elif evt == 'assign_waiting':
            while staff_available > 0 and waiting_queue:
                wait_start, wait_mname = waiting_queue.popleft()
                print(f"Assigning {wait_mname} to staff at time {now}")
                idle_time_total += now - wait_start
                # print 機台 waitting time
                print(f"Machine {wait_mname} waiting time: {now - wait_start}")
                staff_available -= 1
                load_time = machine_status[wait_mname]['load']
                if now + load_time <= simulation_time:
                    heapq.heappush(event_queue, (now + load_time, 'start_proc', wait_mname))
                else:
                    idle_time_total += simulation_time - now



    return idle_time_total


# ========== 區域與機台設定 ==========
ETCH_machines = [("PR_1", 60, 3), ("PR_2", 60, 3)] + \
    [(f"DA_{i}", 17, 3) for i in range(1, 9)] + \
    [(f"85_{i}", 80, 2) for i in range(1, 4)] + \
    [(f"DP_{i}", 50, 2) for i in range(1, 5)]

PHOTO_machines = [(f"DA_{i}", 17, 3) for i in range(9, 14)] + \
    [("PR_3", 60, 3)] + [(f"94_{i}", 120, 2) for i in range(1, 8)] + \
    [("DA_1", 50, 3)] + [(f"DD_{i}", 50, 2) for i in range(1, 5)] + \
    [(f"HM_{i}", 10, 2) for i in range(1, 3)] + [("UM_1", 10, 2)]

TF_machines = [(f"DU_{i}", 60, 4) for i in range(1, 3)] + \
    [(f"MX_{i}", 30, 2) for i in range(1, 7)] + \
    [(f"DR_{i}", 60, 2) for i in range(1, 4)] + \
    [(f"85_{i}", 90, 2) for i in range(4, 7)] + \
    [("ST_1", 44, 2)] + [(f"85A_{i}", 72, 2) for i in range(1, 3)] + \
    [("PR_4", 60, 3)]

def total_idle_time(allocation, sim_time):
    e_idle = simulate_idle_time(ETCH_machines, allocation[0], sim_time)
    p_idle = simulate_idle_time(PHOTO_machines, allocation[1], sim_time)
    t_idle = simulate_idle_time(TF_machines, allocation[2], sim_time)
    return e_idle + p_idle + t_idle




