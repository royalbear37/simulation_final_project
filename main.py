# main.py
from machine import query2
from result import result, compare_results_by_area, plot_gantt
from machine import write_to_oracle


if __name__ == "__main__":
    
    columns = [
        "instance",
        "average_idle_time",
        "staff_in_area1",
        "staff_in_area2",
        "staff_in_area3",
        "dispatch_in_area1",
        "dispatch_in_area2",
        "dispatch_in_area3",
    ]

    output_rows = []

    for row in query2:
        instance = row[0]
        total_staff = int(row[1])
        sim_time = int(row[2]) // 60  # 轉成分鐘

        # 跑所有規則
        res1 = result(total_staff, sim_time, dispatch_rule='GA', ga_replacement='FIFO')
        res2 = result(total_staff, sim_time, dispatch_rule='GA', ga_replacement='LIFO')
        res3 = result(total_staff, sim_time, dispatch_rule='GA', ga_replacement='SPTF')
        res4 = result(total_staff, sim_time, dispatch_rule='FIFO')
        res5 = result(total_staff, sim_time, dispatch_rule='LIFO')
        res6 = result(total_staff, sim_time, dispatch_rule='SPTF')

        results = [res1, res2, res3, res4, res5, res6]
        best = compare_results_by_area(results)
        plot_gantt(best, sim_time)
        output_row = [
            instance,
            best.get("total_idle", ""),                       # average_idle_time
            best["ETCH"]["staff"],                            # staff_in_area1
            best["PHOTO"]["staff"],                           # staff_in_area2
            best["TF"]["staff"],                              # staff_in_area3           
            best["ETCH"]["dispatch_rule"],     # dispatch_in_area1               
            best["PHOTO"]["dispatch_rule"],    # dispatch_in_area3                                      
            best["TF"]["dispatch_rule"],      # dispatch_in_area2               
        ]
        output_rows.append(output_row)

    # print(output_rows)

    # write_to_oracle(output_rows)

    # 印出表頭（每欄寬度 18）
    print("{:<10}{:<18}{:<15}{:<15}{:<15}{:<18}{:<18}{:<18}".format(
        "instance", "average_idle_time", "staff_in_area1", "staff_in_area2", "staff_in_area3",
        "dispatch_in_area1", "dispatch_in_area2", "dispatch_in_area3"
    ))

    # 印出每一行
    for row in output_rows:
        print("{:<10}{:<18}{:<15}{:<15}{:<15}{:<18}{:<18}{:<18}".format(*row))

    

