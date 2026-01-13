# sample_code/bad_code.py
import os
import sys
import sys

def f(a, b):
    x = a + b
    y = a + b
    z = a + b
    return x + y + z

def very_long_function():
    total = 0
    for i in range(100):
        if i % 2 == 0:
            total += i
        else:
            total -= i
    for j in range(50):
        total += j
    for k in range(30):
        total += k
    for m in range(20):
        total += m
    return total
