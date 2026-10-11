def sum_to(n):
    total = 0
    number = 1

    while number <= n:
        total = total + number
        number += 1
    return total 
print(sum_to(5))