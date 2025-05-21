import numpy as np
from simulation import total_idle_time

# ==== 參數設定 ====
NUM_JOB = 3              # 分配給三區的員工數（例如 [3, 4, 4]）

NUM_ITERATION = 20
NUM_CHROME = 20
NUM_BIT = NUM_JOB

Pc = 0.75
Pm = 0.2

NUM_PARENT = NUM_CHROME
NUM_CROSSOVER = int(Pc * NUM_CHROME / 2)
NUM_CROSSOVER_2 = NUM_CROSSOVER * 2
NUM_MUTATION = int(Pm * NUM_CHROME * NUM_BIT)

np.random.seed(0)

# ==== 工具函數 ====
def initPop():
    p = []
    while len(p) < NUM_CHROME:
        x = np.random.randint(0, TOTAL_STAFF + 1, size=NUM_BIT)
        if sum(x) == TOTAL_STAFF:
            p.append(x)
    return p

def fitFunc(x, sim_time, dispatch_rule):
    # 適應度為 -idle_time（越小越好）
    return -total_idle_time(list(x), sim_time, dispatch_rule=dispatch_rule)

def evaluatePop(p, sim_time, dispatch_rule):
    return [fitFunc(ind, sim_time, dispatch_rule) for ind in p]

def selection(p, p_fit):
    selected = []
    for _ in range(NUM_PARENT):
        i, j = np.random.choice(NUM_CHROME, 2, replace=False)
        selected.append(p[i] if p_fit[i] > p_fit[j] else p[j])
    return selected

def crossover_uniform(p):
    children = []
    for _ in range(NUM_CROSSOVER):
        j, k = np.random.choice(NUM_PARENT, 2, replace=False)
        mask = np.random.randint(2, size=NUM_BIT)
        raw1 = np.where(mask, p[j], p[k])
        raw2 = np.where(mask, p[k], p[j])
        for raw in [raw1, raw2]:
            ratio = raw / np.sum(raw)
            adjusted = np.floor(ratio * TOTAL_STAFF).astype(int)
            diff = TOTAL_STAFF - np.sum(adjusted)
            while diff != 0:
                i = np.argmax(ratio - adjusted / TOTAL_STAFF) if diff > 0 else np.argmax(adjusted)
                step = 1 if diff > 0 else -1
                adjusted[i] += step
                diff -= step
            children.append(adjusted.copy())
    return children

def mutation(p):
    for _ in range(NUM_MUTATION):
        row = np.random.randint(NUM_CROSSOVER_2)
        i, j = np.random.choice(NUM_BIT, 2, replace=False)
        if p[row][i] > 0:
            p[row][i] -= 1
            p[row][j] += 1
    # 強制注入新血染色體
    for _ in range(int(NUM_CHROME/3)):  # 每代注入 2 個隨機新染色體
        fresh = np.random.multinomial(TOTAL_STAFF, [1/NUM_BIT] * NUM_BIT)
        p[np.random.randint(len(p))] = fresh

def sortChrome(a, a_fit):
    zipped = list(zip(a_fit, a))
    zipped.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in zipped], [x[0] for x in zipped]

def replace(p, p_fit, a, a_fit):
    merged = p + a
    merged_fit = p_fit + a_fit
    merged, merged_fit = sortChrome(merged, merged_fit)
    return merged[:NUM_CHROME], merged_fit[:NUM_CHROME]


def run_gene(total_staff, sim_time, dispatch_rule):
    global TOTAL_STAFF
    TOTAL_STAFF = total_staff

    pop = initPop()
    pop_fit = evaluatePop(pop, sim_time, dispatch_rule)

    best_outputs = [np.max(pop_fit)]
    mean_outputs = [np.mean(pop_fit)]

    for i in range(NUM_ITERATION):
        parent = selection(pop, pop_fit)
        offspring = crossover_uniform(parent)
        mutation(offspring)
        offspring_fit = evaluatePop(offspring, sim_time, dispatch_rule)
        pop, pop_fit = replace(pop, pop_fit, offspring, offspring_fit)

        best_outputs.append(np.max(pop_fit))
        mean_outputs.append(np.mean(pop_fit))
    best = pop[0].tolist()
    return best, -pop_fit[0]
