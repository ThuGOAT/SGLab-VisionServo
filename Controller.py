
#位置式PID系统
class PositionalPID:
    def __init__(self, P: float, I: float, D: float):
        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.PIDOutput = 0.0  # PID控制器输出
        self.SystemOutput = 0.0  # 系统输出值
        self.LastSystemOutput = 0.0  # 系统的上一次输出

        self.PIDErrAdd = 0.0
        self.ResultValueBack = 0.0
        self.Error = 0.0
        self.LastError = 0.0

    def SetStepSignal(self, StepSignal):
        self.Error = StepSignal - self.SystemOutput

        KpWork  = self.Kp *self.Error
        KiWork = self.Ki* self.PIDErrAdd
        KdWork = self.Kd * (self.Error- self.LastError)
        self.PIDOutput = KpWork + KiWork + KdWork
        self.PIDErrAdd += self.Error
        self.LastError = self.Error

    def SetSystemOutput(self, SystemOutput):
        self.SystemOutput = SystemOutput
        self.LastSystemOutput = self.SystemOutput

class MyController:
    def __init__(self):
        # Attention to the plus or minus sign of P.
        self.pid_x = PositionalPID(1/40000, 0, 0)
        self.pid_y = PositionalPID(-1/40000, 0, 0)

    def adjust(self, cursor_position, icon_position):

        self.pid_x.SetSystemOutput(cursor_position[0])
        self.pid_x.SetStepSignal(icon_position[0])
        increase_x = self.pid_x.PIDOutput

        self.pid_y.SetSystemOutput(cursor_position[1])
        self.pid_y.SetStepSignal(icon_position[1])
        increase_y = self.pid_y.PIDOutput

        return increase_x, increase_y
    
    def is_inplace(self, icon_position, cursor_position):
        
        if (cursor_position[0] > icon_position[0]-15) and (cursor_position[0] < icon_position[0]+22):
            is_inplace_x = True
        else:
            is_inplace_x = False

        if (cursor_position[1] > icon_position[1]-15) and (cursor_position[1] < icon_position[1]+18):
            is_inplace_y = True
        else:
            is_inplace_y = False

        if is_inplace_x == True and is_inplace_y == True:
            return True
        else:
            return False
