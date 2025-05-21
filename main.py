# main.py

from gene import run_gene

if __name__ == "__main__":
    total_staff = int(input("請輸入總員工人數："))
    sim_time = int(input("請輸入模擬時間（分鐘）："))
    dispatch_rule = input("請輸入派工規則（fifo/lifo/sptf）：").strip()
    
    best_allocation, idle = run_gene(total_staff, sim_time, dispatch_rule)
    print(f"最佳分配為：{best_allocation}，總 idle time = {idle}")
