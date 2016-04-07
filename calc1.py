# eval 3+5

NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
OPERATOR = ['+', '-', '*', '/']


def calc(s):
    result = 0
    state = 0
    i = 0
    op = None
    while i < len(s):
        print i
        if s[i] == ' ':
            i += 1
            continue
        if state == 0:
            j = 0
            while s[i+j] in NUMBER:
                j += 1
                if i + j == len(s):
                    break
            num = int(s[i:i+j])
            if not op:
                result = num
            if op == '+':
                result += num
            if op == '-':
                result -= num
            if op == '*':
                result *= num
            if op == '/':
                result /= num
            i += j
            state = 1
            continue
        if state == 1 and s[i] in OPERATOR:
            state = 0
            op = s[i]
            i += 1
            continue
    return result

print calc(" 30 +5 * 10  ")
