class PID_ff():
    '''
    Custom PID loop class designed to tackle the unique problem of controlling ozone flow through a valve.

    Incorporates a "ramp time" scheme, where the system does not immediately try to reach the intended setpoint -- preventing large erratic jumps.
    '''


    def __init__(self, P, I, D, set, sample_time, ramp_time):
        '''
        Initializes custom PID loop.

        :param P: desired proportional term
        :param I: desired integral term
        :param D: desired derivative term
        :param sample_time: how often you plan on sampling your system
        :ramp_time: how long you would like to ramp up to your setpoint
        '''
        self.P = P
        self.I = I
        self.D = D
        self.target = set
        self.t = sample_time
        self.error_sum = 0
        self.error_int = 0
        self.prev_err = 0
        self.sample_time = sample_time
        self.increments = ramp_time / sample_time
        self.count = 0

    def calc_percent_change(self, curr_val):
        '''
        Runs the control loop one step with its given parameters.

        :param curr_val: the measured value of your system
        :returns: the percent change to reach the calculated next value
        '''
        if(self.count == 0):
            # If running for the first time, divide up your setpoint into increments
            self.inc_amount = (self.target - curr_val) / self.increments
            self.target = curr_val + self.inc_amount
        elif(self.count < self.increments):
            self.target += self.inc_amount
            
        err = self.target - curr_val
        der = (err - self.prev_err) / self.sample_time

        self.error_int += err * self.sample_time
        self.prev_err = err
        self.count += 1

        ## Calculate control terms
        p_term = self.P * err
        i_term = self.I * self.error_sum
        d_term = self.D * der

        predicted_value = curr_val + p_term + i_term + d_term
        percent_diff = (self.target - predicted_value) / self.target

        return percent_diff
