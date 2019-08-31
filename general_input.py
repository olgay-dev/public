def universal_input(input_invitation, error_messge, check_function):
    while True:
        s = input(input_invitation)
        res = check_function(s)
        if res == None:
            print(error_messge)
            continue
        break
    return res
