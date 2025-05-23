# main.py
from result import result, compare_results_by_area 

if __name__ == "__main__":
    total_staff = int(input("請輸入總員工人數："))
    sim_time = int(input("請輸入模擬時間（分鐘）："))
    # dispatch_rule = input("請輸入派工規則（FIFO/LIFO/SPTF/GA）：").strip()

    # 取得多個 rule 的 result
    res1 = result(total_staff, sim_time, dispatch_rule='GA', ga_replacement='FIFO')
    res2 = result(total_staff, sim_time, dispatch_rule='GA', ga_replacement='LIFO')
    res3 = result(total_staff, sim_time, dispatch_rule='GA', ga_replacement='SPTF')
    res4 = result(total_staff, sim_time, dispatch_rule='FIFO')
    res5 = result(total_staff, sim_time, dispatch_rule='LIFO')
    res6 = result(total_staff, sim_time, dispatch_rule='SPTF')

    # 組成 list
    results = [res1, res2, res3, res4, res5, res6]

    # 丟進比較函式
    best = compare_results_by_area(results)

    print(best)