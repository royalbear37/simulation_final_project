import heapq
from collections import deque

def _simulate_assign_events(area_machines, num_staff, simulation_time, dispatch_rule, ga_priority):
    """
    只回傳 assign events，不印也不計算 idle time
    """

    from simulation import ETCH_machines, PHOTO_machines, TF_machines

    wait_start_dict = {}
    load_start_dict = {}
    assign_events = []

    if num_staff == 0:
        return []

    event_queue = []
    machine_status = {}
    staff_available = num_staff
    waiting_queue = deque()

    for m_name, proc_time, load_time in area_machines:
        heapq.heappush(event_queue, (proc_time, 'done', m_name))
        machine_status[m_name] = {'proc': proc_time, 'load': load_time}

    def assign_waiting(now):
        nonlocal staff_available
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
                priority_index = {name: i for i, (name, _, _) in enumerate(area_machines)}
                idx, (wait_start, wait_mname) = min(
                    enumerate(waiting_queue),
                    key=lambda x: ga_priority[priority_index[x[1][1]]]
                )
                waiting_queue.remove((wait_start, wait_mname))
            else:
                raise ValueError("Unknown dispatch_rule")

            wait_start_dict[wait_mname] = wait_start
            staff_available -= 1
            load_time = machine_status[wait_mname]['load']
            if now + load_time <= simulation_time:
                heapq.heappush(event_queue, (now + load_time, 'start_proc', wait_mname))
                load_start_dict[wait_mname] = now
            # 不記錄 idle time

    while event_queue:
        now, evt, mname = heapq.heappop(event_queue)
        if now > simulation_time:
            continue

        if evt == 'done':
            m = machine_status[mname]
            if mname not in wait_start_dict:
               waiting_queue.append((now, mname))
            assign_waiting(now)


        elif evt == 'start_proc':
            m = machine_status[mname]
            assign_time = load_start_dict.pop(mname, now)
            if mname in wait_start_dict:
                wait_start = wait_start_dict.pop(mname)
                wait_time = max(0, assign_time - wait_start)
            else:
                wait_start = assign_time
                wait_time = 0
            assign_events.append({
                'assign_time': assign_time,
                'machine': mname,
                'wait_time': wait_time
            })
            staff_available += 1
            proc_done = now + m['proc']
            if proc_done <= simulation_time:
                heapq.heappush(event_queue, (proc_done, 'done', mname))
            assign_waiting(now)

    return assign_events

def simulate_best_allocation_events(allocation, sim_time, dispatch_rule='FIFO', ga_priority_list=None):
    """
    只需 allocation, sim_time，回傳三區 assign events 結果。
    ga_priority_list: 若為 GA，則為 [e_priority, p_priority, t_priority]，否則為 None
    回傳: {'ETCH': [...], 'PHOTO': [...], 'TF': [...]}
    """

    from simulation import ETCH_machines, PHOTO_machines, TF_machines

    events = {}
    if dispatch_rule.upper() == 'GA' and ga_priority_list is not None:
        e_priority, p_priority, t_priority = ga_priority_list
    else:
        e_priority = p_priority = t_priority = None

    events['ETCH'] = _simulate_assign_events(ETCH_machines, allocation[0], sim_time, dispatch_rule, e_priority)
    events['PHOTO'] = _simulate_assign_events(PHOTO_machines, allocation[1], sim_time, dispatch_rule, p_priority)
    events['TF'] = _simulate_assign_events(TF_machines, allocation[2], sim_time, dispatch_rule, t_priority)
    return events
