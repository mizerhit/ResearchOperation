from prettytable import PrettyTable

table = PrettyTable()

global count

print("Здравствуйте, я программа помогающая найти лучший план перевозки продуцкции c минимальными для вас затратами.")

def fictitious_points():
    if sum(number_units_consumers) < sum(number_units_suppliers):
        number_units_consumers.append(sum(number_units_suppliers) - sum(number_units_consumers))
        for i in range(len(number_units_suppliers)):
            transportation_costs[i].append(0)
    if sum(number_units_consumers) > sum(number_units_suppliers):
        number_units_suppliers.append(sum(number_units_consumers) - sum(number_units_suppliers))
        transportation_costs.append([0 for _ in range(len(number_units_consumers))])


def reference_plan_search():
    copy_sup = number_units_suppliers
    copy_con = number_units_consumers
    for m in range(len(copy_sup)):
        if copy_sup[m] > 0:
            for n in range(len(copy_con)):
                if copy_sup[m] > 0:
                    if copy_con[n] > 0:
                        elem_plan = min(copy_sup[m], copy_con[n])
                        reference_plan[m][n] = elem_plan
                        copy_sup[m] -= elem_plan
                        copy_con[n] -= elem_plan


def degeneracy(matrix) -> bool:
    positive_elem_plan = 0
    for m in range(len(number_units_suppliers)):
        for n in range(len(number_units_consumers)):
            if matrix[m][n] > 0:
                positive_elem_plan += 1
    return len(number_units_suppliers) + len(number_units_consumers) - 1 != positive_elem_plan


def delete_columns(matrix, columns, rows):
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


def delete_rows(matrix, columns, rows):
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


def cycle_search(matrix):
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
        if array:
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


def fight_against_degeneracy(plan):
    for m in range(len(plan)):
        for n in range(len(plan[m])):
            if plan[m][n] == 0:
                plan[m][n] = 0.001
                if not cycle_search(plan):
                    return plan
                else:
                    plan[m][n] = 0


def potential_calculation(plan):
    array_u = [0] + [10000 for _ in range(1, len(plan))]
    array_v = [10000 for _ in range(len(plan[0]))]
    while 10000 in array_u or 10000 in array_v:
        for u in range(len(array_u)):
            if array_u[u] != 10000:
                for v in range(len(array_v)):
                    if plan[u][v] != 0 and array_v[v] == 10000:
                        array_v[v] = array_u[u] + transportation_costs[u][v]
        for v in range(len(array_v)):
            if array_v[v] != 10000:
                for u in range(len(array_u)):
                    if plan[u][v] != 0 and array_u[u] == 10000:
                        array_u[u] = array_v[v] - transportation_costs[u][v]
    return array_u, array_v


def min_elem_matrix(matrix):
    x, y = 0, 0
    min_elem = matrix[x][y]
    for m in range(len(matrix)):
        for n in range(len(matrix[m])):
            if min_elem > matrix[m][n]:
                min_elem = matrix[m][n]
                x, y = m, n
    return [min_elem, x, y]


def evaluation_matrix_completion(plan):
    evaluation_matrix = [[n for n in transportation_costs[m]] for m in range(len(transportation_costs))]
    array_u, array_v = potential_calculation(plan)
    for m in range(len(plan)):
        for n in range(len(plan[m])):
            evaluation_matrix[m][n] = evaluation_matrix[m][n] + array_u[m] - array_v[n]
    return evaluation_matrix


def plan_conversion(old_plan, x, y):
    old_plan[x][y] = 1
    cycle = cycle_search(old_plan)
    new_plan = [[n for n in old_plan[m]] for m in range(len(old_plan))]
    old_plan[x][y] = 0
    minus = 0
    theta = 10000
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


def goal_function_calculation():
    global reference_plan
    global transportation_costs
    goal_function = 0
    for m in range(len(reference_plan)):
        for n in range(len(reference_plan[m])):
            goal_function += (reference_plan[m][n] * transportation_costs[m][n])
    return int(goal_function)


count = 1
def plan_optimization():
    global count
    global reference_plan
    while degeneracy(reference_plan):
        fight_against_degeneracy(reference_plan)
    evaluation_matrix = evaluation_matrix_completion(reference_plan)
    
    while min_elem_matrix(evaluation_matrix)[0] < 0:
        coord_x, coord_y = min_elem_matrix(evaluation_matrix)[1], min_elem_matrix(evaluation_matrix)[2]
        reference_plan = plan_conversion(reference_plan, coord_x, coord_y)
        table.clear()
        table.padding_width = 1
        table.header = False
        for k in range(len(reference_plan)):
            table.add_row(reference_plan[k])
        count += 1
        print("Матрица перевозок на ", count, " шагу")
        print(table)
        while degeneracy(reference_plan):
            fight_against_degeneracy(reference_plan)
        evaluation_matrix = evaluation_matrix_completion(reference_plan)
    
number_units_suppliers = list(map(int, input("Введите количество единиц продукции поставщиков: ").split()))
number_units_consumers = list(map(int, input("Введите количество единиц продукции потребителей: ").split()))
transportation_costs = [list(map(int, input(f"Введите стоимость перевозки из {i + 1} склада во все магазины: \n").split())) for i in range(len(number_units_suppliers))]
print("\n \n")


fictitious_points()
reference_plan = [[0 for n in range(len(number_units_consumers))] for m in range(len(number_units_suppliers))]
reference_plan_search()

table.clear()
table.padding_width = 1
table.header = False
        
for k in range(len(reference_plan)):
    table.add_row(reference_plan[k])
print("Матрица перевозок на ", count, " шагу")
print(table)
plan_optimization()
print("\n Минимальные затраты на перевозку:", goal_function_calculation())
