from gene import run_gene
from event import simulate_best_allocation_events
from simulation import simulate_idle_time
import matplotlib
import matplotlib.pyplot as plt




def pretty_priority_align(names, priorities):
    # 每個 array 一行顯示，區域名稱置中
    for name, arr in zip(names, priorities):
        print(f"{name:^5}區域的順序編號：[{', '.join(str(x) for x in arr)}]")

# 用法不變


def result(total_staff, sim_time, dispatch_rule, ga_replacement=None):
    if dispatch_rule.upper() == 'GA':
        from dispatch_ga import run_ga_for_area
        from machine import ETCH_machines, PHOTO_machines, TF_machines
        # 步驟1：先用 LIFO 找 allocation
        first_allocation, _ = run_gene(total_staff, sim_time, ga_replacement)
        e_staff, p_staff, t_staff = first_allocation

        # 步驟2：用這組 allocation 找 GA priority
        e_priority, _ = run_ga_for_area(ETCH_machines, e_staff, sim_time)
        p_priority, _ = run_ga_for_area(PHOTO_machines, p_staff, sim_time)
        t_priority, _ = run_ga_for_area(TF_machines, t_staff, sim_time)
        ga_priority_list = [e_priority, p_priority, t_priority]

        # 步驟3：用這組 priority 再用 gene 找 allocation（這次 gene 評分時要帶入 ga_priority_list）
        best_allocation, _ = run_gene(total_staff, sim_time, 'GA', ga_priority_list=ga_priority_list)
        e_staff, p_staff, t_staff = best_allocation

        # 步驟4：用 best_allocation + ga_priority_list 計算 idle time
        e_idle = simulate_idle_time(ETCH_machines, e_staff, sim_time, dispatch_rule='GA', ga_priority=e_priority)
        p_idle = simulate_idle_time(PHOTO_machines, p_staff, sim_time, dispatch_rule='GA', ga_priority=p_priority)
        t_idle = simulate_idle_time(TF_machines, t_staff, sim_time, dispatch_rule='GA', ga_priority=t_priority)
        total_idle = e_idle + p_idle + t_idle
        # print各種dispatch_rule的結果
        # print("="*40)
        # print(f"dispatch_rule: {dispatch_rule.upper()}")
        # print(f"ga_replacement: {ga_replacement.upper()}")
        # print(f"最佳分配為：{best_allocation}")
        # pretty_priority_align(["ETCH", "PHOTO", "TF"], [e_priority, p_priority, t_priority])
        # print(f"ETCH 區域的閒置時間：{e_idle}, PHOTO 區域的閒置時間：{p_idle}, TF 區域的閒置時間：{t_idle}")
        # print(f"總閒置時間：{total_idle}")
        # print("="*40)
        # 顯示各區域的分配事件
        # events = simulate_best_allocation_events(
        #     best_allocation, sim_time, dispatch_rule=dispatch_rule,
        #     ga_priority_list=ga_priority_list if dispatch_rule.upper() == 'GA' else None
        # )
        # print("=== 各區域分配事件 ===")
        # for area, evlist in events.items():
        #     print(f"{area:<5} 區域：")
        #     for e in evlist:
        #         print(f"  時間 {e['assign_time']:>5}: 機台 {e['machine']:<8}，等待時間 {e['wait_time']:>3}")
        return {
            "dispatch_rule": dispatch_rule.upper(),
            "ga_replacement": ga_replacement.upper() if ga_replacement else None,
            "ga_priority": [e_priority, p_priority, t_priority],
            "ETCH": {"staff": e_staff, "idle_time": e_idle},
            "PHOTO": {"staff": p_staff, "idle_time": p_idle},
            "TF": {"staff": t_staff, "idle_time": t_idle},
            "total_idle": total_idle,
            "allocation": best_allocation
        }
    else:
        best_allocation, idle = run_gene(total_staff, sim_time, dispatch_rule)
        e_staff, p_staff, t_staff = best_allocation
        ga_priority_list = None
        from machine import ETCH_machines, PHOTO_machines, TF_machines
        e_idle = simulate_idle_time(ETCH_machines, e_staff, sim_time, dispatch_rule=dispatch_rule)
        p_idle = simulate_idle_time(PHOTO_machines, p_staff, sim_time, dispatch_rule=dispatch_rule)
        t_idle = simulate_idle_time(TF_machines, t_staff, sim_time, dispatch_rule=dispatch_rule)
        # print各種dispatch_rule的結果
        # print("="*40)
        # print(f"dispatch_rule: {dispatch_rule.upper()}")
        # print(f"最佳分配為：{best_allocation}")
        # print(f"ETCH 區域的閒置時間：{e_idle}, PHOTO 區域的閒置時間：{p_idle}, TF 區域的閒置時間：{t_idle}")
        # print(f"總閒置時間：{idle}")
        # print("="*40)

        # 顯示各區域的分配事件
        # events = simulate_best_allocation_events(
        #     best_allocation, sim_time, dispatch_rule=dispatch_rule,
        #     ga_priority_list=ga_priority_list if dispatch_rule.upper() == 'GA' else None
        # )
        # print("=== 各區域分配事件 ===")
        # for area, evlist in events.items():
        #     print(f"{area:<5} 區域：")
        #     for e in evlist:
        #         print(f"  時間 {e['assign_time']:>3}: 機台 {e['machine']:<6}，等待時間 {e['wait_time']:>3}")
        return {
            "dispatch_rule": dispatch_rule.upper(),
            "ga_replacement": None,
            "ETCH": {"staff": e_staff, "idle_time": e_idle},
            "PHOTO": {"staff": p_staff, "idle_time": p_idle},
            "TF": {"staff": t_staff, "idle_time": t_idle},
            "total_idle": idle,
            "allocation": best_allocation
        }




def compare_results_by_area(results):
    import itertools
    areas = ['ETCH', 'PHOTO', 'TF']

    area_choices = []
    for area in areas:
        choices = []
        for res in results:
            # 新增: 若是GA，帶入該區priority
            priority = None
            if res['dispatch_rule'] == 'GA' and 'ga_priority' in res:
                # res['ga_priority'] 是 [e_priority, p_priority, t_priority]
                idx = areas.index(area)
                priority = res['ga_priority'][idx]
            choices.append({
                "dispatch_rule": res['dispatch_rule'],
                "ga_replacement": res.get('ga_replacement', None),
                "staff": res[area]['staff'],
                "idle_time": res[area]['idle_time'],
                "allocation": res['allocation'],
                "ga_priority": priority
            })
        area_choices.append(choices)

    best = None
    min_total_idle = float('inf')
    best_combo = None

    total_staff_sum = sum(results[0]['allocation'])

    for combo in itertools.product(*area_choices):
        allocation = [combo[0]['staff'], combo[1]['staff'], combo[2]['staff']]
        if sum(allocation) != total_staff_sum:
            continue  # 跳過人數不符的組合
        dispatch_rules = [combo[0]['dispatch_rule'], combo[1]['dispatch_rule'], combo[2]['dispatch_rule']]
        e_idle = combo[0]['idle_time']
        p_idle = combo[1]['idle_time']
        t_idle = combo[2]['idle_time']
        total_idle = e_idle + p_idle + t_idle
        if total_idle < min_total_idle:
            min_total_idle = total_idle
            best_combo = combo
            best = {
                'ETCH': {
                    "dispatch_rule": dispatch_rules[0],
                    "ga_replacement": combo[0]['ga_replacement'],
                    "staff": allocation[0],
                    "idle_time": e_idle,
                    "ga_priority": combo[0].get('ga_priority', None)
                },
                'PHOTO': {
                    "dispatch_rule": dispatch_rules[1],
                    "ga_replacement": combo[1]['ga_replacement'],
                    "staff": allocation[1],
                    "idle_time": p_idle,
                    "ga_priority": combo[1].get('ga_priority', None)
                },
                'TF': {
                    "dispatch_rule": dispatch_rules[2],
                    "ga_replacement": combo[2]['ga_replacement'],
                    "staff": allocation[2],
                    "idle_time": t_idle,
                    "ga_priority": combo[2].get('ga_priority', None)
                },
                'total_idle': round(total_idle/55, 4),
                'allocation': allocation
            }

    return best



def plot_gantt(best_combo, sim_time):
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    matplotlib.rcParams['axes.unicode_minus'] = False

    from machine import ETCH_machines, PHOTO_machines, TF_machines
    from event import _simulate_assign_events

    area_map = {
        'ETCH': ETCH_machines,
        'PHOTO': PHOTO_machines,
        'TF': TF_machines
    }

    for area in ['ETCH', 'PHOTO', 'TF']:
        area_info = best_combo[area]
        machines = area_map[area]
        staff = area_info['staff']
        dispatch_rule = area_info['dispatch_rule']
        ga_priority = area_info.get('ga_priority', None)

        print(f"處理 {area} 區域，分配人數: {staff}, dispatch_rule: {dispatch_rule}, ga_priority: {ga_priority}")

        events = _simulate_assign_events(
            machines, staff, sim_time, dispatch_rule, ga_priority
        )

        # 依機台分組
        machine_events = {}
        for e in events:
            m = str(e['machine'])
            machine_events.setdefault(m, []).append(e)
        # 依 assign_time 排序
        for evlist in machine_events.values():
            evlist.sort(key=lambda x: x['assign_time'])

        # 畫所有機台
        # machine_names = sorted(list(machine_events.keys()))
        machine_names = [str(m[0]) for m in machines]

        fig, ax = plt.subplots(figsize=(16, max(4, len(machine_names)*0.7)))
        yticks = []
        yticklabels = []
        y = 0

        for mname in machine_names:
            evlist = machine_events.get(mname, [])
            evlist.sort(key=lambda x: x['assign_time'])
            for m in machines:
                if str(m[0]) == mname:
                    init_done = m[1] 
                    proc = m[1]
                    load = m[2]
                    break
            if not evlist:
                ax.barh(y, init_done, left=0, color='gray', edgecolor='black', alpha=0.7, height=0.6)
                ax.barh(y, sim_time - init_done, left=init_done, color='red', edgecolor='black', alpha=0.7, height=0.6)
            else:
                if init_done > 0:
                    ax.barh(y, init_done, left=0, color='gray', edgecolor='black', alpha=0.7, height=0.6)
                last_done = init_done
                for e in evlist:
                    assign = e['assign_time']
                    if assign > last_done:
                        ax.barh(y, assign - last_done, left=last_done, color='red', edgecolor='black', alpha=0.7, height=0.6)
                    if assign + proc + load <= sim_time:
                        ax.barh(y, proc + load, left=assign, color='gray', edgecolor='black', alpha=0.7, height=0.6)
                        last_done = assign + proc + load
                    else:
                        end = sim_time - assign
                        ax.barh(y, end, left=assign, color='gray', edgecolor='black', alpha=0.7, height=0.6)
                        last_done = sim_time
                if last_done < sim_time:
                    ax.barh(y, sim_time - last_done, left=last_done, color='red', edgecolor='black', alpha=0.7, height=0.6)
            yticks.append(y)
            yticklabels.append(mname)
            y += 1

        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels, fontsize=14)
        ax.set_xlabel("Time", fontsize=16)
        ax.set_title(f"Gantt Chart - {area} area", fontsize=18)
        ax.tick_params(axis='x', labelsize=14)
        ax.grid(True, axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()




