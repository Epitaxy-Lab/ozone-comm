class PID_ff():
    def __init__(self, P, I, D, set, sample_time, ramp_time):
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
        if(self.count == 0):
            self.inc_amount = (self.target - curr_val) / self.increments
            self.target = curr_val + self.inc_amount
        elif(self.count < self.increments):
            self.target += self.inc_amount
        err = self.target - curr_val
        print("Current value is: " + str(curr_val))
        print("Error is: " + str(err))
        print("Target value is: " + str(self.target))
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
