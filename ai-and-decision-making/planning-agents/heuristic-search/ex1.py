from numpy import character

import search
import random
import math
import itertools
from itertools import product

ids = ["000000000", "000000000"]


class HarryPotterProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        self.map = initial['map']
        wizard_state = tuple(
            (wizard_name, wizard_data[0], wizard_data[1]) for
            wizard_name, wizard_data in initial['wizards'].items())
        horcrux_state = tuple(initial['horcruxes'])
        death_eater_state = tuple((de_name, tuple(de_path)) for de_name, de_path in initial['death_eaters'].items())

        general_data_state = (0, True, False, len(horcrux_state)) # (turn, voldemort_alive, has_dead_wizard, alive_horcruxes_amount)
        initial_state = wizard_state, death_eater_state, horcrux_state, general_data_state

        for i, arr in enumerate(self.map):
            for j, element in enumerate(arr):
                if element == 'V':
                    self.v_x, self.v_y = i, j


        search.Problem.__init__(self, initial_state)

    def actions(self, state):

        alive_horcruxes_amount = state[3][3]
        action_list = []
        wizards = {name: (pos, lives) for name, pos, lives in state[0]}
        horcruxes = [pos for pos in state[2]]


        for wiz_name, (pos, lives) in wizards.items():
            x, y = pos
            wizard_actions = []
            # Move actions (up, down, left, right)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < len(self.map) and 0 <= new_y < len(self.map[0]):  # Within bounds
                    if (self.map[new_x][new_y] == "P" or
                    (self.map[new_x][new_y] == "V" and wiz_name == "Harry Potter" and alive_horcruxes_amount == 0)):  # Passable tile
                        wizard_actions.append(("move", wiz_name, (new_x, new_y)))
            # Destroy action

            for index, (h_x_position, h_y_position) in enumerate(horcruxes):
                if (x, y) == (h_x_position, h_y_position):
                    wizard_actions.append(("destroy", wiz_name, index))
            # Wait action
            wizard_actions.append(("wait", wiz_name))
            # Kill_Voldemort

            if (self.map[x][y] == 'V'):
                wizard_actions.append(("kill", wiz_name))
            action_list.append(wizard_actions)
        # All the combination of actions(one for each wizard)

        return list(product(*action_list))

    def result(self, state, action):
        wizards = {name: (pos, lives) for name, pos, lives in state[0]}
        death_eaters = {name: path for name, path in state[1]}
        horcruxes = [pos for pos in state[2]]
        general_data = [x for x in state[3]]

        turn = general_data[0]+1
        voldemort_alive = general_data[1]
        has_dead_wizard = general_data[2]
        alive_horcruxes_amount = general_data[3]

        for wizard_action in action:
            if wizard_action[0] == 'move':
                wizard_name = wizard_action[1]
                new_position = wizard_action[2]
                lives = wizards[wizard_name][1]
                wizards[wizard_name] = (new_position, lives)
            if wizard_action[0] == 'destroy':
                wizard_name = wizard_action[1]
                horcrux_position = wizards[wizard_name][0]
                if horcrux_position in horcruxes:
                    horcruxes.remove(horcrux_position)
                    alive_horcruxes_amount -= 1
            if wizard_action[0] == 'kill':
                voldemort_alive = False  # voldemort is dead


        for de_name, de_path in death_eaters.items():
             for wiz_name, (wiz_pos, wiz_lives) in wizards.items():
                 cycle_length = 2 * len(de_path) - 2
                 cycle_pos = turn % cycle_length
                 if cycle_pos < len(de_path):
                     de_pos = de_path[cycle_pos]
                 else:
                     reverse_pos = cycle_length - cycle_pos
                     de_pos = de_path[reverse_pos]
                 if de_pos == wiz_pos:
                     wizards[wiz_name]= wiz_pos, wiz_lives-1
                     if wizards[wiz_name][1] == 0:
                         has_dead_wizard = True



        wizard_state = tuple(
            (wizard_name, wizard_data[0], wizard_data[1]) for
            wizard_name, wizard_data in wizards.items())
        horcrux_state = tuple(horcruxes)
        death_eater_state = tuple((de_name, tuple(de_path)) for de_name, de_path in death_eaters.items())

        general_data = turn, voldemort_alive, has_dead_wizard, alive_horcruxes_amount

        initial_state = wizard_state, death_eater_state, horcrux_state, general_data

        return initial_state

    def goal_test(self, state):
        general_data = [x for x in state[3]]
        voldemort_alive = general_data[1]
        has_dead_wizard = general_data[2]
        if not voldemort_alive and not has_dead_wizard:
            return True
        return False


    def h(self, node):
        total_heuristic = 0
        state = node.state
        wizards = {name: (pos, lives) for name, pos, lives in state[0]}
        has_dead_wizard = state[3][2]
        voldemort_is_alive = state[3][1]
        alive_horcruxes_amount = state[3][3]
        if has_dead_wizard:
            return float('inf')
        if not voldemort_is_alive:  # voldemort_is_dead
            return 0

        harry_vold_distance = abs(wizards["Harry Potter"][0][0] - self.v_x) + abs(wizards["Harry Potter"][0][1] - self.v_y)
        if alive_horcruxes_amount:   # there is alive horcruxes
            wizards_amount = len(wizards.keys())
            if wizards_amount > 1:
                horcrux_max_distances = []
                sum_distances = []
                for hor_pos in state[2]:
                    wizard_distances = [
                        abs(wiz_pos[0] - hor_pos[0]) + abs(wiz_pos[1] - hor_pos[1])
                        for wiz_name, (wiz_pos, wiz_lives) in wizards.items()
                    ]
                    horcrux_max_distances.append(max(wizard_distances))
                    sum_distances.append(sum(wizard_distances))
                # the max distance between some horcrux to some wizard
                total_heuristic += (max(horcrux_max_distances))
                # sum of wizards' distances from all alive horcrux in respect of their amount
                total_heuristic += (sum(sum_distances)) / (wizards_amount ** 0.6)
            else:
                relaxed_best_path = min(
                    abs(wizards["Harry Potter"][0][0] - hor_pos[0]) + abs(wizards["Harry Potter"][0][1] - hor_pos[1])
                    + abs(self.v_x - hor_pos[0]) + abs(self.v_y - hor_pos[1])
                    for hor_pos in state[2])
                total_heuristic += relaxed_best_path
            for wiz_name, (wiz_pos, wiz_lives) in wizards.items():
                if wiz_lives <= 2:  # critical_amount
                    total_heuristic += math.sqrt(3 - wiz_lives)  # penalty
            total_heuristic += harry_vold_distance
        else:
            total_heuristic += harry_vold_distance ** 2
            harry_lives = wizards["Harry Potter"][1]
            if harry_lives <= 2:
                total_heuristic *= ((3 - harry_lives) ** 2)

        return total_heuristic

def create_harrypotter_problem(game):
    return HarryPotterProblem(game)