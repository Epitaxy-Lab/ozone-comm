def send_com(command, conn):
    '''
    Sends a serial command, and return

    :param command: a string representing the command you'd like to send
    :param conn: an open serial.Serial connection
    :returns: the serial object's response
    '''
    conn.write(command.encode())
    response = conn.readline().decode()
    return response

def run_pi_keyboard():
    '''
    Bring up an onscreen keyboard on a Raspberry Pi
    '''
    os.system("matchbox-keyboard")

def parse_scientific(num):
    '''
    Parse
    '''
    parts = num.split("E")
    return float(parts[0]) * 10**(int(parts[1]))

def calc_per_diff(a, b):
    c = (b - a) / a
    print("\n\n Difference: " + str(c) + "\n\n")
    return c
