def send_com(command, conn):
    '''
    Sends a serial command, and return

    :param command: a string representing the command you'd like to send
    :param conn: an open serial.Serial connection
    :returns: the serial object's response
    '''
    conn.flushInput()
    conn.flushOutput()
    conn.write(command.encode())
    response = conn.readline().decode()
    return response

def parse_scientific(num):
    '''
    Parses an input string of the format "x..xEx..x", and returns its numerical equivalent

    :param num: a string in scientific notation
    :returns: the input string evaluated as a number
    '''
    parts = num.split("E")
    exp = 10**(int(parts[1]))
    val = float(parts[0])
    return val * exp

def calc_per_diff(a, b):
    '''
    Calculates the percent difference between a and b
    '''
    c = (b - a) / a
    print("\n\n Difference: " + str(c) + "\n\n")
    return c
