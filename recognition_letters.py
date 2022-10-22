from os import chdir
from textwrap import fill
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from collections import defaultdict

def count_lakes_and_bays(prop):
    b = ~prop.image
    lb = label(b)
    regs = regionprops(lb)

    count_lakes = 0 # Внутренняя пустая часть буквы
    count_bays = 0  # Внешняя пустая часть буквы
    for reg in regs:
        flag = True
        for y, x in reg.coords:
            if (y == 0 or
                x == 0 or
                y == prop.image.shape[0] - 1 or
                x == prop.image.shape[1] - 1):
                flag = False # Сброс флага - нашли внешнюю часть
                break
        if flag:
            count_lakes += 1
        else:
            count_bays += 1

    return count_lakes, count_bays

def has_vline(image):   # Есть хотя бы одна вертикальная линия
    return 1. in image.mean(0)

def filling_factor(image):  # Заполненность относительно размера
    return image.sum() / image.size

def distance(prop):
    cy, cx = prop.centroid
    return ((cy - prop.image.shape[0] // 2) ** 2 + (cx - prop.image.shape[1] // 2) ** 2) ** 0.5

def recognize(image):
    result = defaultdict(lambda : 0)
    labeled = label(image)
    props = regionprops(labeled)

    for prop in props:
        lakes, bays = count_lakes_and_bays(prop)
        if np.all(prop.image):
            result["-"] += 1
        elif lakes == 2:  # B or 8
            if has_vline(prop.image[ : , : 1]):
                result["B"] += 1
            else:
                result["8"] += 1
        elif lakes == 1:    # A or P or D or 0
            if bays == 3:
                result["A"] += 1
            elif bays == 2: # P or D
                cy, _ = prop.centroid
                cy /= prop.image.shape[0]
                if cy < 4.5:
                    result["P"] += 1
                else:
                    result["D"] += 1
            else:
                result["0"] += 1
        elif lakes == 0:    # 1 or / or X or * or W
            if has_vline(prop.image):
                result["1"] += 1
            elif bays == 2:
                result["/"] += 1
            elif bays == 4 and (filling_factor(prop.image[-1 : : 1]) > 0.35):   # Дополнительно проверяем на отличие от звездочки (*)
                result["X"] += 1
            else:
                if (filling_factor(prop.image[ : 1]) > 0.35):
                    result["W"] += 1
                else:
                    result["*"] += 1
        else:
            result["uknown"] += 1
    
    return result

# ----------- main code -----------

image = plt.imread("alphabet.png")
image = np.mean(image, 2)   # Усредняем пиксели
image[image > 0] = 1    # Теперь бинарное (все пиксели == 1)

_ , total_letters = label(image, return_num=True)
print(f"Всего объектов: {total_letters}")

rec_res = recognize(image)
recognized_characters = 0

for key, value in rec_res.items():
    print(f"{key} -> {value}")
    recognized_characters += value

print(f"Процент распознанных символов: {recognized_characters / total_letters * 100}%")

# check

print("Проверка значений...")

check_dict = {'A': 21, 'B': 25, '8': 23, '0': 10, 
              '1': 31, 'W': 12, 'X': 15, '*': 22, 
              '-': 20, '/': 21}

is_correct = True
count_errors = 0
for key, value in check_dict.items():
    if rec_res[key] != check_dict[key]:
        print(f"Incorrect value! ({key} -> {rec_res[key]} != {check_dict[key]}) <---> delta (процент лишних) -> {(rec_res[key] - check_dict[key]) / check_dict[key] * 100}%")
        is_correct = False
        count_errors += 1

if is_correct:
    print("Все значения совпадают")
else:
    print(f"Процент ошибок (от общего числа ключей): {count_errors / len(check_dict.keys()) * 100}%")

plt.figure("Графон 4к")
plt.imshow(image)
plt.show()

 #? Отладочные инструкции
 
#  (prop.image[ : 1].sum() == prop.image[-1 : : 1].sum())):# and
#  (filling_factor(image) )):
# print(filling_factor(prop))
# print(distance(prop))
# plt.imshow(prop.image)
# plt.show()
# print(filling_factor(prop.image[-1 : : 1]))