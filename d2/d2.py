def sum_to(n):
    total = 0
    number = 1

    while number <= n:
        total = total + number
        number += 1
    return total 
print(sum_to(5))
print(sum_to(10))
print(sum_to(100))


def identity(x):
    return x    
def square(x):
    return x * x
def cube(x):
    return x * x * x
def sum_terms(n,term):
    total = 0
    number = 1

    while number <= n:
        if number % 2 == 0:
            total = total + term(number)
        number += 1
    return total
print(sum_terms(5,identity))
print(sum_terms(5,square))
print(sum_terms(5,cube))