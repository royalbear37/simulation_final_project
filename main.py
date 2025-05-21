# main.py
from result import result

if __name__ == "__main__":
    total_staff = int(input("請輸入總員工人數："))
    sim_time = int(input("請輸入模擬時間（分鐘）："))
    dispatch_rule = input("請輸入派工規則（FIFO/LIFO/SPTF/GA）：").strip()

    result(total_staff, sim_time, dispatch_rule)