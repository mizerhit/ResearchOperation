from prettytable import PrettyTable
table = PrettyTable()

def Input(restrictions, variables):
    input_arr = list(map(str, str(input("Цены за единицу продукции каждого вида: 300x1 + x2 + 400x4 (пример) \n")).split()))
    for j in range(len(input_arr)):
        if input_arr[j] == '+':
            continue
        if input_arr[j] == '-':
            input_arr[j + 1] = ''.join([input_arr[j], input_arr[j + 1]])
            continue
        if input_arr[j].find("x") == 0:
            multipliers[int(input_arr[j][input_arr[j].find("x") + 1:])] = float(1)
        elif input_arr[j].find("x") == 1 and input_arr[j][0] == '-':
            multipliers[int(input_arr[j][input_arr[j].find("x") + 1:])] = float(-1)
        else:
            multipliers[int(input_arr[j][input_arr[j].find("x") + 1:])] = float(input_arr[j][:input_arr[j].find("x")])

    for i in range(restrictions):
        input_arr = list(map(str, str(input("Введите элементы таблицы ограничений C1, C2 и тд. и количество доступных ресурсов: 2x1 + x2 + 3x4 <= 100 (пример)\n")).split()))
        simplex_table[i][0] = float(input_arr[-1])
        for j in range(len(input_arr) - 1):
            if input_arr[j] == '+':
                continue
            if input_arr[j] == '-':
                input_arr[j + 1] = ''.join([input_arr[j], input_arr[j + 1]])
                continue
            if input_arr[j] == '<=' or input_arr[j] == '>=' or input_arr[j] == '=':
                inequalities.append(input_arr[j])
                continue
            if input_arr[j].find("x") == 0:
                simplex_table[i][int(input_arr[j][input_arr[j].find("x") + 1:])] = float(1)
            elif input_arr[j].find("x") == 1 and input_arr[j][0] == '-':
                simplex_table[i][int(input_arr[j][input_arr[j].find("x") + 1:])] = float(-1)
            else:
                simplex_table[i][int(input_arr[j][input_arr[j].find("x") + 1:])] = float(input_arr[j][:input_arr[j].find("x")])


def Adding_Var(restrictions, F_max):
    global multipliers
    global basis
    extended_form_variables = 0
    artificial_variables = 0
    for i in inequalities:
        if i != '=': extended_form_variables += 1
        if i == '>=': artificial_variables += 1

    new_variables = extended_form_variables + artificial_variables
    single_array = [0 for j in range(new_variables)]

    for i in range(restrictions):
        simplex_table[i] = simplex_table[i] + single_array
        if inequalities[i] == '<=':
            simplex_table[i][-new_variables + i] = 1.0
        if inequalities[i] == '>=':
            simplex_table[i][-new_variables + i] = -1.0
            simplex_table[i][-artificial_variables + i] = 1.0

    M = 10 ** 4
    if F_max: M = -10 ** 4
    multipliers += ([0 for i in range(extended_form_variables)] + [M for i in range(artificial_variables)])
    for i in range(restrictions):
        for j in range(len(simplex_table[i]) - new_variables, len(simplex_table[i])):
            if simplex_table[i][j] == 1.0:
                basis.append(j)


def Fill_Idx_Str(restrictions):
    for i in range(len(multipliers)):
        for j in range(restrictions):
            index_string[i] += (simplex_table[j][i] * multipliers[basis[j]])
        index_string[i] -= multipliers[i]


def Select_Main_Column(F_max) -> int:
    global there_negatives
    element_line = 0
    index_element = 0
    for i in range(1, len(index_string)):
        if F_max:
            if index_string[i] < element_line:
                element_line = index_string[i]
                index_element = i
        else:
            if index_string[i] > element_line:
                element_line = index_string[i]
                index_element = i
    if index_element == 0:
        there_negatives = False
    return index_element


def Select_Main_Line(restrictions) -> int:
    min_element_column = 10 ** 10
    index_min_element = 0
    for i in range(restrictions):
        if simplex_table[i][guide_column] > 0:
            elem = simplex_table[i][0] / simplex_table[i][guide_column]
            if elem >= 0 and elem < min_element_column:
                min_element_column = elem
                index_min_element = i
    return index_min_element

variables = int(input("Какое в вашей таблице кол-во кол-во столбцов: "))
restrictions = int(input("Какое в вашей таблице кол-во строк не считая цены за ед. изделия: "))
F_max = (str(input("Вы хотите максимизировать или минимизировать? Введите max или min: ")) == 'max')
multipliers = [0 for j in range(variables + 1)]
simplex_table = [[0 for j in range(variables + 1)] for i in range(restrictions)]
inequalities = []
basis = []
there_negatives = True
Input(restrictions, variables)
Adding_Var(restrictions, F_max)
index_string = [0 for i in range(len(multipliers))]
Fill_Idx_Str(restrictions)
guide_column = Select_Main_Column(F_max)
guide_line = Select_Main_Line(restrictions)

counter = 0
while there_negatives:
    counter += 1
    guide_line = Select_Main_Line(restrictions)
    guide_elem = simplex_table[guide_line][guide_column]
    table.add_rows(simplex_table)
    table.padding_width = 1
    table.header = False
    print("\n Таблица на ", counter, "шаге")
    print(table)
    
    basis[guide_line] = guide_column
    print("Индексы базисных переменных:")
    print(basis)
    new_simplex_table = [0 for x in range(restrictions)]
    for i in range(restrictions):
        new_simplex_table[i] = [0 for x in range(len(simplex_table[i]))]
        if i == guide_line:
            new_simplex_table[guide_line] = [x / guide_elem for x in simplex_table[guide_line]]
    for i in range(restrictions):
        if i != guide_line:
            for j in range(len(simplex_table[i])):
                new_simplex_table[i][j] = simplex_table[i][j] - (
                            new_simplex_table[guide_line][j] * simplex_table[i][guide_column])
    simplex_table = new_simplex_table
    index_string = [0 for i in range(len(multipliers))]
    Fill_Idx_Str(restrictions)
    guide_column = Select_Main_Column(F_max)

F = 0
for i in range(restrictions):
    F += (new_simplex_table[i][0] * multipliers[basis[i]])

print('Ответ при заданных условиях: F =', F)
