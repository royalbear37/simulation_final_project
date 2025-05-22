import numpy as np
from simulation import simulate_idle_time, ETCH_machines, PHOTO_machines, TF_machines

def run_ga_for_area(area_machines, num_staff, sim_time, num_chrome=60, num_iter=100, Pc=0.75, Pm=0.05):
    """
    對指定機台區域執行 GA 最佳化，最小化 idle time。
    - area_machines: List of (name, proc_time, load_time)
    - num_staff: 該區人數
    - sim_time: 模擬時間
    - return: 最佳排序（List[int]）, 最佳 idle time
    """
    num_bit = len(area_machines)

    def initPop():
        return [np.random.permutation(num_bit) for _ in range(num_chrome)]

    def fitFunc(chrom):
        return -simulate_idle_time(area_machines, num_staff, sim_time, dispatch_rule='GA', ga_priority=chrom)

    def evaluatePop(pop):
        return [fitFunc(c) for c in pop]

    def selection(pop, fit):
        return [pop[j] if fit[j] > fit[k] else pop[k]
                for j, k in (np.random.choice(num_chrome, 2, replace=False) for _ in range(num_chrome))]

    def crossover_uniform(parents):
        offspring = []
        for _ in range(int(Pc * num_chrome / 2)):
            mask = np.random.randint(2, size=num_bit)
            j, k = np.random.choice(len(parents), 2, replace=False)
            p1, p2 = parents[j].copy(), parents[k].copy()
            remain1, remain2 = list(p1.copy()), list(p2.copy())
            for m in range(num_bit):
                if mask[m] == 1:
                    remain2.remove(p1[m])
                    remain1.remove(p2[m])
            t = 0
            for m in range(num_bit):
                if mask[m] == 0:
                    p1[m] = remain2[t]
                    p2[m] = remain1[t]
                    t += 1
            offspring.append(p1)
            offspring.append(p2)
        return offspring

    def mutation(pop):
        for _ in range(int(Pm * len(pop) * num_bit)):
            r = np.random.randint(len(pop))
            j, k = np.random.choice(num_bit, 2, replace=False)
            pop[r][j], pop[r][k] = pop[r][k], pop[r][j]

    def sortPop(pop, fit):
        idx = np.argsort(fit)[::-1]
        return [pop[i] for i in idx], [fit[i] for i in idx]

    def replace(pop, fit, offspring, offspring_fit):
        combined = pop + offspring
        combined_fit = fit + offspring_fit
        return sortPop(combined, combined_fit)[0][:num_chrome], sortPop(combined, combined_fit)[1][:num_chrome]

    # GA 主流程
    pop = initPop()
    pop_fit = evaluatePop(pop)

    for i in range(num_iter):
        parents = selection(pop, pop_fit)
        offspring = crossover_uniform(parents)
        mutation(offspring)
        offspring_fit = evaluatePop(offspring)
        pop, pop_fit = replace(pop, pop_fit, offspring, offspring_fit)
        # print(pop[0])
        # print(f"[GA] Iter {i+1:3d} | Best idle = {-pop_fit[0]}")

    best = pop[0]
    best_idle = -fitFunc(best)

    # print(f"[GA] Best priority = {best.tolist()}")
    # print(f"[GA] Best idle = {best_idle}")
    return best.tolist(), best_idle


def run_full_ga_dispatch(total_staff, sim_time):
    """
    先用 gene 找 allocation，再對三區分別用 GA 派工，最後計算 idle time。
    """
    from gene import run_gene  # 避免循環 import
    best_allocation, _ = run_gene(total_staff, sim_time, 'LIFO')  # 或 'FIFO'
    e_staff, p_staff, t_staff = best_allocation

    e_priority, _ = run_ga_for_area(ETCH_machines, e_staff, sim_time)
    p_priority, _ = run_ga_for_area(PHOTO_machines, p_staff, sim_time)
    t_priority, _ = run_ga_for_area(TF_machines, t_staff, sim_time)

    ga_priority_list = [e_priority, p_priority, t_priority]

    e_idle = simulate_idle_time(ETCH_machines, e_staff, sim_time, dispatch_rule='GA', ga_priority=e_priority)
    p_idle = simulate_idle_time(PHOTO_machines, p_staff, sim_time, dispatch_rule='GA', ga_priority=p_priority)
    t_idle = simulate_idle_time(TF_machines, t_staff, sim_time, dispatch_rule='GA', ga_priority=t_priority)

    return best_allocation, e_idle, p_idle, t_idle, e_idle + p_idle + t_idle, ga_priority_list