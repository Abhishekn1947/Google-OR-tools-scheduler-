import json
from ortools.sat.python import cp_model

class TestCenterScheduler:
    def __init__(self, num_centers, valves_info, shift_info):
        self.num_centers = num_centers
        self.valves_info = valves_info
        self.shift_info = shift_info
        self.model = cp_model.CpModel()
        self.tasks = []

    def create_schedule(self):
        for valve in self.valves_info:
            valve_type = valve['valve_type']
            test_center = valve['test_center']
            processing_time = valve['processing_time']
            start_range, end_range = valve['time_range']

            start_var = self.model.NewIntVar(int(start_range * 60), int((end_range - processing_time) * 60),
                                             f'Start_{valve_type}')
            end_var = self.model.NewIntVar(int(start_range * 60) + int(processing_time * 60), int(end_range * 60),
                                           f'End_{valve_type}')
            interval_var = self.model.NewIntervalVar(start_var, int(processing_time * 60), end_var,
                                                     f'Interval_{valve_type}')

            self.tasks.append((test_center, interval_var))

        for center in range(self.num_centers):
            center_intervals = [interval for test_center, interval in self.tasks if test_center == center]
            self.model.AddNoOverlap(center_intervals)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print('Optimal Schedule Found:')
            for _, interval_var in self.tasks:
                start_time = solver.Value(interval_var.StartExpr()) / 60
                end_time = solver.Value(interval_var.EndExpr()) / 60
                print(f'{interval_var.Name()} scheduled from {start_time:.2f} to {end_time:.2f}')
        else:
            print('No solution found.')

def load_input_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data['valves_info'], data['shift_info']

valves_info, shift_info = load_input_data('/Users/abhis_m3/PycharmProjects/OR Tools 2/input1.json')
num_test_centers = 6

scheduler = TestCenterScheduler(num_test_centers, valves_info, shift_info)
scheduler.create_schedule()
