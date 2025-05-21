from gene import run_gene
from simulation import simulate_best_allocation_events




def pretty_priority_align(names, priorities):
    # 每個 array 一行顯示，區域名稱置中
    for name, arr in zip(names, priorities):
        print(f"{name:^5}區域的優先順序：[{', '.join(str(x) for x in arr)}]")

# 用法不變


def result(total_staff, sim_time, dispatch_rule):
    if dispatch_rule.upper() == 'GA':
        from dispatch_ga import run_full_ga_dispatch
        best_allocation, e_idle, p_idle, t_idle, total_idle, ga_priority_list = run_full_ga_dispatch(total_staff, sim_time)
        e_priority, p_priority, t_priority = ga_priority_list
        print(f"最佳分配為：{best_allocation}")
        pretty_priority_align(["ETCH", "PHOTO", "TF"], [e_priority, p_priority, t_priority])
        print(f"ETCH 區域的閒置時間：{e_idle}, PHOTO 區域的閒置時間：{p_idle}, TF 區域的閒置時間：{t_idle}")
        print(f"總閒置時間：{total_idle}")
    else:
        best_allocation, idle = run_gene(total_staff, sim_time, dispatch_rule)
        ga_priority_list = None
        print(f"最佳分配為：{best_allocation}")
        print(f"總閒置時間：{idle}")
    events = simulate_best_allocation_events(
        best_allocation, sim_time, dispatch_rule=dispatch_rule,
        ga_priority_list=ga_priority_list if dispatch_rule.upper() == 'GA' else None
    )
    # print("=== 各區域分配事件 ===")
    # for area, evlist in events.items():
    #     print(f"{area:<5} 區域：")
    #     for e in evlist:
    #         print(f"  時間 {e['assign_time']:>3}: 機台 {e['machine']:<6}，等待時間 {e['wait_time']:>3}")