from gene import run_gene
from event import simulate_best_allocation_events




def pretty_priority_align(names, priorities):
    # 每個 array 一行顯示，區域名稱置中
    for name, arr in zip(names, priorities):
        print(f"{name:^5}區域的順序編號：[{', '.join(str(x) for x in arr)}]")

# 用法不變


def result(total_staff, sim_time, dispatch_rule, ga_replacement=None):
    if dispatch_rule.upper() == 'GA':
        from dispatch_ga import run_ga_for_area, ETCH_machines, PHOTO_machines, TF_machines
        # 步驟1：先用 LIFO 找 allocation
        first_allocation, _ = run_gene(total_staff, sim_time, ga_replacement)
        e_staff, p_staff, t_staff = first_allocation

        # 步驟2：用這組 allocation 找 GA priority
        e_priority, _ = run_ga_for_area(ETCH_machines, e_staff, sim_time)
        p_priority, _ = run_ga_for_area(PHOTO_machines, p_staff, sim_time)
        t_priority, _ = run_ga_for_area(TF_machines, t_staff, sim_time)
        ga_priority_list = [e_priority, p_priority, t_priority]

        # 步驟3：用這組 priority 再用 gene 找 allocation（這次 gene 評分時要帶入 ga_priority_list）
        best_allocation, _ = run_gene(total_staff, sim_time, 'LIFO', ga_priority_list=ga_priority_list)
        e_staff, p_staff, t_staff = best_allocation

        # 步驟4：用 best_allocation + ga_priority_list 計算 idle time
        from simulation import simulate_idle_time
        e_idle = simulate_idle_time(ETCH_machines, e_staff, sim_time, dispatch_rule='GA', ga_priority=e_priority)
        p_idle = simulate_idle_time(PHOTO_machines, p_staff, sim_time, dispatch_rule='GA', ga_priority=p_priority)
        t_idle = simulate_idle_time(TF_machines, t_staff, sim_time, dispatch_rule='GA', ga_priority=t_priority)
        total_idle = e_idle + p_idle + t_idle

        print("="*40)
        print(f"dispatch_rule: {dispatch_rule.upper()}")
        print(f"ga_replacement: {ga_replacement.upper()}")
        print(f"最佳分配為：{best_allocation}")
        pretty_priority_align(["ETCH", "PHOTO", "TF"], [e_priority, p_priority, t_priority])
        print(f"ETCH 區域的閒置時間：{e_idle}, PHOTO 區域的閒置時間：{p_idle}, TF 區域的閒置時間：{t_idle}")
        print(f"總閒置時間：{total_idle}")
        print("="*40)
    else:
        print("="*40)
        best_allocation, idle = run_gene(total_staff, sim_time, dispatch_rule)
        ga_priority_list = None
        print(f"dispatch_rule: {dispatch_rule.upper()}")
        print(f"最佳分配為：{best_allocation}")
        print(f"總閒置時間：{idle}")
        print("="*40)

    events = simulate_best_allocation_events(
        best_allocation, sim_time, dispatch_rule=dispatch_rule,
        ga_priority_list=ga_priority_list if dispatch_rule.upper() == 'GA' else None
    )
    print("=== 各區域分配事件 ===")
    for area, evlist in events.items():
        print(f"{area:<5} 區域：")
        for e in evlist:
            print(f"  時間 {e['assign_time']:>3}: 機台 {e['machine']:<6}，等待時間 {e['wait_time']:>3}")