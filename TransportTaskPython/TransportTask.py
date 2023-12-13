from typing import List
import tqdm
import time

EPSILON = 0.001
INFINITY = 10000

def add_fictitious_points(units_consumed: List[int], units_supplied: List[int], transportation_costs: List[List[int]]):
    for _ in tqdm.tqdm(range(50)):
        time.sleep(0.1)
    if sum(units_consumed) < sum(units_supplied):
        shortage = sum(units_supplied) - sum(units_consumed)
        units_consumed.append(shortage)
        transportation_costs.extend([[0] * len(units_consumed) for _ in range(len(units_supplied))])
    elif sum(units_consumed) > sum(units_supplied):
        surplus = sum(units_consumed) - sum(units_supplied)
        units_supplied.append(surplus)
        transportation_costs.append([0] * len(units_consumed))


def find_reference_plan(units_supplied: List[int], units_consumed: List[int], transportation_costs: List[List[int]]):
    copy_sup = units_supplied.copy()
    copy_con = units_consumed.copy()
    reference_plan = [[0] * len(units_consumed) for _ in range(len(units_supplied))]

    for supplier_idx in range(len(copy_sup)):
        if copy_sup[supplier_idx] > 0:
            for consumer_idx in range(len(copy_con)):
                if copy_sup[supplier_idx] > 0 and copy_con[consumer_idx] > 0:
                    elem_plan = min(copy_sup[supplier_idx], copy_con[consumer_idx])
                    reference_plan[supplier_idx][consumer_idx] = elem_plan
                    copy_sup[supplier_idx] -= elem_plan
                    copy_con[consumer_idx] -= elem_plan

    return reference_plan


def is_degeneracy(matrix: List[List[int]]) -> bool:
    positive_elem_plan = sum(1 for row in matrix for elem in row if elem > 0)
    return len(units_supplied) + len(units_consumed) - 1 != positive_elem_plan


def delete_columns(matrix: List[List[int]], columns: List[int], rows: List[int]) -> List[int]:
    deleted_array = []
    for n in columns:
        count_non_zero = 0
        for m in rows:
            if matrix[m][n] != 0:
                count_non_zero += 1
                if count_non_zero > 1:
                    break
        if count_non_zero <= 1:
            deleted_array.append(n)
    return deleted_array


def delete_rows(matrix: List[List[int]], columns: List[int], rows: List[int]) -> List[int]:
    deleted_array = []
    for m in rows:
        count_non_zero = 0
        for n in columns:
            if matrix[m][n] != 0:
                count_non_zero += 1
                if count_non_zero > 1:
                    break
        if count_non_zero <= 1:
            deleted_array.append(m)
    return deleted_array


def find_cycle(matrix: List[List[int]]) -> List[List[int]]:
    columns = [x for x in range(len(matrix[0]))]
    rows = [x for x in range(len(matrix))]
    cycle = False
    while not cycle and (len(columns) > 1 and len(rows) > 1):
        array = delete_columns(matrix, columns, rows)
        if not array:
            cycle = True
        for j in array:
            columns.remove(j)

        array = delete_rows(matrix, columns, rows)
        if array and not cycle:
            cycle = False
        for j in array:
            rows.remove(j)
    if cycle:
        cycle_coordinates = []
        for x in rows:
            if len(cycle_coordinates) == 0:
                for y in columns:
                    if matrix[x][y] != 0:
                        cycle_coordinates.append([x, y])
                        break
        while cycle_coordinates[0] != cycle_coordinates[-1] or len(cycle_coordinates) < 3:
            if len(cycle_coordinates) % 2 != 0:
                x = cycle_coordinates[-1][0]
                old_y = cycle_coordinates[-1][1]
                for y in columns:
                    if y != old_y and matrix[x][y] != 0:
                        cycle_coordinates.append([x, y])
            else:
                y = cycle_coordinates[-1][1]
                old_x = cycle_coordinates[-1][0]
                for x in rows:
                    if x != old_x and matrix[x][y] != 0:
                        cycle_coordinates.append([x, y])
        cycle_coordinates.pop()
        return cycle_coordinates


def fix_degeneracy(plan: List[List[int]]) -> List[List[int]]:
    for m in range(len(plan)):
        for n in range(len(plan[m])):
            if plan[m][n] == 0:
                plan[m][n] = 0.001
                if not is_degeneracy(plan) and not find_cycle(plan):
                    return plan
                else:
                    plan[m][n] = 0


def calculate_potentials(plan: List[List[int]]) -> List[List[int]]:
    array_u = [0] + [INFINITY for _ in range(1, len(plan))]
    array_v = [INFINITY for _ in range(len(plan[0]))]
    while INFINITY in array_u or INFINITY in array_v:
        for u in range(len(array_u)):
            if array_u[u] != INFINITY:
                for v in range(len(array_v)):
                    if plan[u][v] != 0 and array_v[v] == INFINITY:
                        array_v[v] = array_u[u] + transportation_costs[u][v]
        for v in range(len(array_v)):
            if array_v[v] != INFINITY:
                for u in range(len(array_u)):
                    if plan[u][v] != 0 and array_u[u] == INFINITY:
                        array_u[u] = array_v[v] - transportation_costs[u][v]
    return array_u, array_v


def find_min_elem_matrix(matrix: List[List[int]]) -> List[int]:
    x, y = 0, 0
    min_elem = matrix[x][y]
    for m in range(len(matrix)):
        for n in range(len(matrix[m])):
            if min_elem > matrix[m][n]:
                min_elem = matrix[m][n]
                x, y = m, n
    return [min_elem, x, y]


def complete_evaluation_matrix(plan: List[List[int]]) -> List[List[int]]:
    evaluation_matrix = [[n for n in transportation_costs[m]] for m in range(len(transportation_costs))]
    array_u, array_v = calculate_potentials(plan)
    for m in range(len(plan)):
        for n in range(len(plan[m])):
            evaluation_matrix[m][n] = evaluation_matrix[m][n] + array_u[m] - array_v[n]
    return evaluation_matrix


def convert_plan(old_plan: List[List[int]], x: int, y: int) -> List[List[int]]:
    old_plan[x][y] = 1
    cycle = find_cycle(old_plan)
    new_plan = [[n for n in old_plan[m]] for m in range(len(old_plan))]
    old_plan[x][y] = 0
    minus = 0
    theta = INFINITY
    for j in range(len(cycle)):
        if cycle[j][0] == x and cycle[j][1] == y:
            minus = (j - 1) % 2
            break
    for j in range(minus, len(cycle), 2):
        theta = min(old_plan[cycle[j][0]][cycle[j][1]], theta)
    for j in range((minus + 1) % 2, len(cycle), 2):
        new_plan[cycle[j][0]][cycle[j][1]] = old_plan[cycle[j][0]][cycle[j][1]] + theta
    for j in range(minus, len(cycle), 2):
        new_plan[cycle[j][0]][cycle[j][1]] = old_plan[cycle[j][0]][cycle[j][1]] - theta
    return new_plan


def calculate_goal_function(reference_plan: List[List[int]], transportation_costs: List[List[int]]) -> int:
    goal_function = 0
    for m in range(len(reference_plan)):
        for n in range(len(reference_plan[m])):
            goal_function += (reference_plan[m][n] * transportation_costs[m][n])
    return int(goal_function)


def optimize_plan():
    global reference_plan
    if is_degeneracy(reference_plan):
        fix_degeneracy(reference_plan)
    evaluation_matrix = complete_evaluation_matrix(reference_plan)
    while find_min_elem_matrix(evaluation_matrix)[0] < 0:
        coord_x, coord_y = find_min_elem_matrix(evaluation_matrix)[1], find_min_elem_matrix(evaluation_matrix)[2]
        reference_plan = convert_plan(reference_plan, coord_x, coord_y)
        if is_degeneracy(reference_plan):
            fix_degeneracy(reference_plan)
        evaluation_matrix = complete_evaluation_matrix(reference_plan)


def main():
    global reference_plan
    global units_supplied
    global units_consumed
    global transportation_costs

    units_supplied = list(map(int, input("Через пробел введите количества товаров хранящихся в каждой точке (Пример: 10 5 6 7):\n").split()))
    units_consumed = list(map(int, input("Через пробел введите количества товаров требующихся в каждой точке (Пример: 20 50 40):\n").split()))
    transportation_costs = [list(map(int, input("Также через пробел введите цены транспортирвок: \n").split())) for _ in
                            range(len(units_supplied))]

    add_fictitious_points(units_consumed, units_supplied, transportation_costs)
    reference_plan = find_reference_plan(units_supplied, units_consumed, transportation_costs)

    optimize_plan()
    print("Минимальные затраты на транспортировку равны ", calculate_goal_function(reference_plan, transportation_costs))


if __name__ == "__main__":
    main()
