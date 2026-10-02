from random import random
import copy
from itertools import product

ids = ["000000000", "000000000"]


DESTROY_HORCRUX_REWARD = 2
RESET_REWARD = -2
DEATH_EATER_CATCH_REWARD = -1


def state_to_tuple(initial):

    wizard_state = tuple(
        (wizard_name, wizard_data["location"])
        for wizard_name, wizard_data in initial["wizards"].items()
    )

    horcrux_state = tuple(
        (
            horcrux_name,
            horcrux_data["location"],
            tuple(horcrux_data["possible_locations"]),
            horcrux_data["prob_change_location"]
        )
        for horcrux_name, horcrux_data in initial["horcrux"].items()
    )

    death_eater_state = tuple(
        (de_name, de_data["index"], tuple(de_data["path"]))
        for de_name, de_data in initial["death_eaters"].items()
    )
    return wizard_state, horcrux_state, death_eater_state


def state_reward(state):
    points = 0
    wizards = {name: {"location": pos} for name, pos in state[0]}
    death_eaters = {name: {"index": index, "path": list(path)} for name, index, path in state[2]}
    for _, wiz_data in wizards.items():
        for _, de_data in death_eaters.items():
            if wiz_data["location"] == de_data["path"][de_data["index"]]:
                points = points + DEATH_EATER_CATCH_REWARD
    return points


class OptimalWizardAgent:
    def __init__(self, initial):
        self.initial = initial
        self.map = initial['map']
        self.turns_tg = initial['turns_to_go']
        self.wizard_state, self.horcrux_state, self.death_eater_state = state_to_tuple(initial)
        # Precompute action space and optimal policy for every possible state and remaining turns
        self.value_func = {}
        self.optimal_policy = {}
        self.compute_optimal_policy()

    def actions(self, state):
        wizards = {name: {"location": pos} for name, pos in state[0]}
        horcruxes = {name: {
            "location": location,
            "possible_locations": list(possible_locations),
            "prob_change_location": prob_change_location
        } for name, location, possible_locations, prob_change_location in state[1]}
        action_list = []
        # Iterate over wizards
        for wiz_name, wiz_data in wizards.items():
            x, y = wiz_data["location"]  # Access wizard's location
            wizard_actions = []

            # Generate move actions (up, down, left, right)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < len(self.map) and 0 <= new_y < len(self.map[0]):  # Within bounds
                    if self.map[new_x][new_y] == "P":  # Passable cell
                        wizard_actions.append(("move", wiz_name, (new_x, new_y)))

            # Generate destroy actions if on a horcrux location
            for horcrux_name, horcrux_data in horcruxes.items():
                hx, hy = horcrux_data["location"]
                if (x, y) == (hx, hy):
                    wizard_actions.append(("destroy", wiz_name, horcrux_name))

            # Add "wait" action
            wizard_actions.append(("wait", wiz_name))

            # Append wizard's possible actions to the action list
            action_list.append(wizard_actions)

            # Debug print for possible actions
        # Generate all combinations of actions (Cartesian product)
        return list(product(*action_list)) + ["terminate", "reset"]

    def results(self, state, action):
        all_possible_states = []
        if action == 'reset':
            all_possible_states.append((state_to_tuple(self.initial), 1))
            return all_possible_states
        wizards = {name: {"location": pos} for name, pos in state[0]}
        horcruxes = {name: {
            "location": location,
            "possible_locations": list(possible_locations),
            "prob_change_location": prob_change_location
        } for name, location, possible_locations, prob_change_location in state[1]}
        death_eaters = {name: {"index": index, "path": list(path)} for name, index, path in state[2]}

        for wizard_action in action:
            if wizard_action[0] == 'move':
                wizard_name = wizard_action[1]
                new_position = wizard_action[2]
                wizards[wizard_name]["location"] = new_position  # Update only the 'location' key

        possible_h_state_list = []
        horcrux_names = list(horcruxes.keys())
        possible_locations = [horcruxes[name]["possible_locations"] for name in horcrux_names]
        # Iterating over all combinations of locations
        for combination in product(*possible_locations):
            modified_dict = copy.deepcopy(horcruxes)  # Create a deep copy of horcruxes

            total_prob = 1  # Start with the total probability being 1 (100%)

            # Assign the new locations from the combination to each horcrux
            for i, horcrux_name in enumerate(horcrux_names):
                current_location = horcruxes[horcrux_name]["location"]
                new_location = combination[i]
                prob_change = horcruxes[horcrux_name]["prob_change_location"]
                num_options = len(horcruxes[horcrux_name]["possible_locations"])
                if new_location != current_location:
                    total_prob *= prob_change / num_options
                    modified_dict[horcrux_name]["location"] = new_location
                else:
                    total_prob *= (1 - prob_change) + (prob_change / num_options)
            possible_h_state_list.append((modified_dict, total_prob))

        possible_de_state_list = []
        death_eater_names = list(death_eaters.keys())

        # Generate possible moves for each death eater
        possible_moves = []
        for name in death_eater_names:
            data = death_eaters[name]
            current_index = data["index"]
            path = data["path"]

            # Determine possible moves and probabilities
            moves = []
            probabilities = []
            if current_index > 0:  # Not the first tile
                moves.append(current_index - 1)  # Move backward
                probabilities.append(1 / 3 if current_index < len(path) - 1 else 1 / 2)
            if current_index < len(path) - 1:  # Not the last tile
                moves.append(current_index + 1)  # Move forward
                probabilities.append(1 / 3 if current_index > 0 else 1 / 2)

            moves.append(current_index)  # Stay in place
            if 0 < current_index < len(path) - 1:  # Non-edge
                probabilities.append(1 / 3)
            else:  # Edge
                probabilities.append(1 / 2)

            possible_moves.append(list(zip(moves, probabilities)))

        # Generate all combinations of movements
        for combination in product(*possible_moves):
            modified_dict = copy.deepcopy(death_eaters)
            combined_probability = 1

            for i, (new_index, probability) in enumerate(combination):
                name = death_eater_names[i]
                combined_probability *= probability
                modified_dict[name]["index"] = new_index

            possible_de_state_list.append((modified_dict, combined_probability))

        for de, pr1 in possible_de_state_list:
            for h, pr2 in possible_h_state_list:
                st = {"wizards": wizards, "horcrux": h, "death_eaters": de}
                new_possible_state = state_to_tuple(st)
                all_possible_states.append((new_possible_state, pr1 * pr2))
        return all_possible_states

    def compute_optimal_policy(self):
        initial_state = state_to_tuple(self.initial)
        self.opt_value_iterations(initial_state, self.turns_tg)

    def opt_value_iterations(self, state, turns_left):

        # Base case: V^0(s) = R(s)
        if turns_left == 0:
            self.value_func[state, turns_left] = state_reward(state)
            self.optimal_policy[state, turns_left] = None
            return self.value_func[state, turns_left]

        # Check if value has already been computed
        if (state, turns_left) in self.value_func:
            return self.value_func[(state, turns_left)]

        # Recursive computation: V^t(s) = R(s) + max_a Σ_s' [P(s' | s, a) * V^(t-1)(s')]
        max_value = float('-inf')
        best_action = None

        for action in self.actions(state):
            if action == "terminate":
                expected_value = 0
            else:
                expected_value = sum(
                    probability * self.opt_value_iterations(next_state, turns_left - 1)
                    for next_state, probability in self.results(state, action)
                )
                if action != "reset":
                    destroy_count = 0
                    for wizard_action in action:
                        if wizard_action[0] == 'destroy':
                            destroy_count += 1
                    expected_value += destroy_count * DESTROY_HORCRUX_REWARD
                else:
                    expected_value += RESET_REWARD

            if expected_value > max_value:
                max_value = expected_value
                best_action = action

        # Store the computed value and optimal action
        self.value_func[(state, turns_left)] = state_reward(state) + max_value
        self.optimal_policy[(state, turns_left)] = best_action
        return self.value_func[(state, turns_left)]

    def act(self, state):
        """
        Given the current state, choose the optimal action from the precomputed policy.
        """
        turns_tg = state["turns_to_go"]
        curr_state = state_to_tuple(state)
        # Use the precomputed optimal policy to decide the next action
        action = self.optimal_policy[curr_state, turns_tg]
        return action


class WizardAgent:
    def __init__(self, initial):
        self.map = initial["map"]

    def act(self, state):
        danger_zones = set()
        for de_name, de_info in state["death_eaters"].items():
            path = de_info["path"]
            index = de_info["index"]
            curr_pos = path[index]
            if len(path) > 2:
                if index == 0:
                    danger_zones.update([curr_pos, path[1]])
                elif index == len(path) - 1:
                    danger_zones.update([curr_pos, path[-2]])

        # Simple heuristic for non-optimal agent
        return_action = []
        for wizard, info in state["wizards"].items():
            # Check if we can destroy a horcrux
            can_destroy = False
            for horcrux, h_info in state["horcrux"].items():
                if h_info["location"] == info["location"]:
                    return_action.append(("destroy", wizard, horcrux))
                    can_destroy = True
                    break

            if not can_destroy:
                # Simple movement strategy - try to move towards nearest horcrux
                closest_horcrux = None
                min_dist = float('inf')
                for horcrux, h_info in state["horcrux"].items():
                    dist = abs(h_info["location"][0] - info["location"][0]) + \
                           abs(h_info["location"][1] - info["location"][1])
                    if dist < min_dist:
                        min_dist = dist
                        closest_horcrux = h_info["location"]

                if closest_horcrux:
                    # Move towards horcrux while avoiding death eaters
                    dx = closest_horcrux[0] - info["location"][0]
                    dy = closest_horcrux[1] - info["location"][1]

                    new_x, new_y = info["location"]
                    possible_moves = []
                    if abs(dx) > abs(dy):
                        if dx > 0:
                            possible_moves.append((new_x + 1, new_y))
                        else:
                            possible_moves.append((new_x - 1, new_y))
                    else:
                        if dy > 0:
                            possible_moves.append((new_x, new_y + 1))
                        else:
                            possible_moves.append((new_x, new_y - 1))

                    if abs(dx) > abs(dy):
                        if dy > 0:
                            possible_moves.append((new_x, new_y + 1))
                        else:
                            possible_moves.append((new_x, new_y - 1))
                    else:
                        if dx > 0:
                            possible_moves.append((new_x + 1, new_y))
                        else:
                            possible_moves.append((new_x - 1, new_y))

                    # Select the best valid move
                    chosen_move = None
                    for move in possible_moves:
                        x, y = move
                        if (0 <= x < len(self.map) and 0 <= y < len(self.map[0]) and
                                self.map[x][y] == 'P' and move not in danger_zones):
                            chosen_move = move
                            break

                    if chosen_move:
                        return_action.append(("move", wizard, chosen_move))
                    else:
                        return_action.append(("wait", wizard))  # No safe move, better to wait
                else:
                    return_action.append(("wait", wizard))

        return tuple(return_action)
