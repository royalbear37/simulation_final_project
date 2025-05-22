import heapq
from collections import deque

def simulate_idle_time(area_machines, num_staff, simulation_time, dispatch_rule='fifo', ga_priority=None):
    """
    模擬單一區域的機台排程與人力分配，回傳 idle time 總和。
    - area_machines: List of tuples (name, proc_time, load_time)
    - num_staff: 分配到該區的員工數
    - simulation_time: 模擬總長度（分鐘）
    """

    simulate_idle_time.wait_start_dict = {}
    simulate_idle_time.load_start_dict = {}

    if num_staff == 0:
        return sum(max(0, simulation_time - proc) for _, proc, _ in area_machines)

    event_queue = []
    machine_status = {}
    idle_time_total = 0
    staff_available = num_staff
    waiting_queue = deque()

    for m_name, proc_time, load_time in area_machines:
        heapq.heappush(event_queue, (proc_time, 'done', m_name))
        machine_status[m_name] = {'proc': proc_time, 'load': load_time}


    def assign_waiting(now):
        nonlocal idle_time_total, staff_available
        while staff_available > 0 and waiting_queue:
            if dispatch_rule.upper() == 'FIFO':
                wait_start, wait_mname = waiting_queue.popleft()
            elif dispatch_rule.upper() == 'LIFO':
                wait_start, wait_mname = waiting_queue.pop()
            elif dispatch_rule.upper() == 'SPTF':
                idx, (wait_start, wait_mname) = min(
                    enumerate(waiting_queue),
                    key=lambda x: machine_status[x[1][1]]['proc']
                )
                waiting_queue.remove((wait_start, wait_mname))
            elif dispatch_rule.upper() == 'GA':
                if ga_priority is None:
                    raise ValueError("GA priority must be provided for GA dispatch rule")
                # priority_index 用來對應機台名稱到排序 index
                priority_index = {name: i for i, (name, _, _) in enumerate(area_machines)}
                idx, (wait_start, wait_mname) = min(
                    enumerate(waiting_queue),
                    key=lambda x: ga_priority[priority_index[x[1][1]]]
                )
                waiting_queue.remove((wait_start, wait_mname))
            else:
                raise ValueError("Unknown dispatch_rule")

            # 只記錄正確的 wait_start
            simulate_idle_time.wait_start_dict[wait_mname] = wait_start
            idle_time = max(0, now - wait_start)  # 防止負數
            idle_time_total += idle_time
            staff_available -= 1
            load_time = machine_status[wait_mname]['load']
            # 在安排 start_proc 事件時記錄上料開始時間
            if now + load_time <= simulation_time:
                heapq.heappush(event_queue, (now + load_time, 'start_proc', wait_mname))
                simulate_idle_time.load_start_dict[wait_mname] = now  # 記錄上料開始時間
            else:
                idle_time_total += simulation_time - now

    while event_queue:
        now, evt, mname = heapq.heappop(event_queue)
        if now > simulation_time:
            continue

        # 暫存當前時間所有事件
        current_events = [(now, evt, mname)]
        while event_queue and event_queue[0][0] == now:
            current_events.append(heapq.heappop(event_queue))

        for _, evt, mname in current_events:
            if evt == 'done':
                if mname not in simulate_idle_time.wait_start_dict:
                    waiting_queue.append((now, mname))
            elif evt == 'start_proc':
                m = machine_status[mname]
                assign_time = simulate_idle_time.load_start_dict.pop(mname, now)
                if hasattr(simulate_idle_time, 'wait_start_dict') and mname in simulate_idle_time.wait_start_dict:
                    wait_start = simulate_idle_time.wait_start_dict.pop(mname)
                    wait_time = max(0, assign_time - wait_start)
                proc_done = now + m['proc']
                if proc_done <= simulation_time:
                    heapq.heappush(event_queue, (proc_done, 'done', mname))
                staff_available += 1

        # 在處理完當前時間點所有事件後，再做一次 assign
        assign_waiting(now)

    return idle_time_total


# ========== 區域與機台設定 ==========

#測試用 簡單易讀
# ETCH_machines = [(f"DA_{i}", 17, 3) for i in range(1, 6)]
# PHOTO_machines = [(f"DB_{i}", 17, 3) for i in range(1, 5)]
# TF_machines = [(f"DU_{i}", 60, 4) for i in range(1, 6)]


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

def total_idle_time(allocation, sim_time, dispatch_rule='FIFO', ga_priority_list=None):
    if ga_priority_list is not None:
        e_priority, p_priority, t_priority = ga_priority_list
    else:
        e_priority = p_priority = t_priority = None
    e_idle = simulate_idle_time(ETCH_machines, allocation[0], sim_time, dispatch_rule=dispatch_rule, ga_priority=e_priority)
    p_idle = simulate_idle_time(PHOTO_machines, allocation[1], sim_time, dispatch_rule=dispatch_rule, ga_priority=p_priority)
    t_idle = simulate_idle_time(TF_machines, allocation[2], sim_time, dispatch_rule=dispatch_rule, ga_priority=t_priority)
    
    return e_idle + p_idle + t_idle