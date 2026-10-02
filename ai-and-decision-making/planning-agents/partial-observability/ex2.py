import random

ids = ["000000000", "000000000"]


class GringottsController:

    def __init__(self, map_shape, harry_loc, initial_observations):
        self.rows, self.cols = map_shape
        self.harry_loc = harry_loc
        self.visited = set()
        self.on_vault = False
        self.vaults = set()
        self.dragons = set()
        self.traps = set()
        self.destroyed_traps = set()
        self.collected_vaults = set()
        self.previous_location = harry_loc
        self.directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]



        # Timeout: 60 seconds

    def get_next_action(self, observations):
        harry_x, harry_y = self.harry_loc



        if self.harry_loc not in self.visited:
            self.visited.add(self.harry_loc)
            for obs in observations:
                if obs[0] == "vault"\
                    and obs[1] not in self.collected_vaults:
                    self.vaults.add(obs[1])
                elif obs[0] == "dragon":
                    self.dragons.add(obs[1])
                elif obs[0] == "sulfur":
                    for x, y in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                        new_harry_x, new_harry_y = harry_x + x, harry_y + y
                        if (0 <= new_harry_x < self.rows and 0 <= new_harry_y < self.cols)\
                            and (new_harry_x, new_harry_y) not in self.destroyed_traps:
                            self.traps.add((new_harry_x,new_harry_y))

        if self.on_vault:
            self.on_vault = False
            self.vaults.remove(self.harry_loc)
            self.collected_vaults.add(self.harry_loc)
            self.previous_location = (harry_x, harry_y)
            # print ("collect")
            return ("collect",)


        for x, y in self.directions:
            new_harry_x, new_harry_y = harry_x + x, harry_y + y
            if (0 <= new_harry_x < self.rows and 0 <= new_harry_y < self.cols
                    and (new_harry_x, new_harry_y) not in self.dragons):
                if (new_harry_x, new_harry_y) in self.vaults and (new_harry_x, new_harry_y) not in self.traps:
                    self.harry_loc = ((new_harry_x, new_harry_y))
                    self.on_vault = True
                    self.previous_location = (harry_x, harry_y)
                    # print ("move", (new_harry_x, new_harry_y))
                    return ("move",(new_harry_x, new_harry_y))

        random.shuffle(self.directions)

        for x, y in self.directions:
            new_harry_x, new_harry_y = harry_x + x, harry_y + y
            if (0 <= new_harry_x < self.rows and 0 <= new_harry_y < self.cols
                    and (new_harry_x, new_harry_y) not in self.dragons):
                if (new_harry_x, new_harry_y) in self.vaults and (new_harry_x, new_harry_y) in self.traps:
                    self.traps.remove((new_harry_x,new_harry_y))
                    self.destroyed_traps.add((new_harry_x,new_harry_y))
                    self.previous_location = (harry_x, harry_y)
                    # print("destroy", (new_harry_x, new_harry_y))
                    return ("destroy", (new_harry_x, new_harry_y))

        random.shuffle(self.directions)

        for x, y in self.directions:
            new_harry_x, new_harry_y = harry_x + x, harry_y + y
            if (0 <= new_harry_x < self.rows and 0 <= new_harry_y < self.cols
                and (new_harry_x, new_harry_y) not in self.dragons)\
                and (new_harry_x, new_harry_y) not in self.traps\
                and self.vaults:
                    min_dist = float('inf')
                    for vault in self.vaults:
                        dist = abs(new_harry_x - vault[0]) + abs(new_harry_y - vault[1])
                        if dist < min_dist:
                            min_dist = dist
                            self.harry_loc = ((new_harry_x, new_harry_y))
                            self.previous_location = (harry_x, harry_y)
                    # print ("move", (self.harry_loc))
                    return ("move",(self.harry_loc))

        random.shuffle(self.directions)

        for x, y in self.directions:
            new_harry_x, new_harry_y = harry_x + x, harry_y + y
            if (0 <= new_harry_x < self.rows and 0 <= new_harry_y < self.cols
                    and (new_harry_x, new_harry_y) not in self.dragons)\
                    and (new_harry_x, new_harry_y) not in self.visited\
                    and (new_harry_x, new_harry_y) not in self.traps:
                        self.harry_loc = ((new_harry_x, new_harry_y))
                        self.previous_location = (harry_x, harry_y)
                        # print ("move", (new_harry_x, new_harry_y))
                        return ("move", (new_harry_x, new_harry_y))

        random.shuffle(self.directions)

        for x, y in self.directions:
            new_harry_x, new_harry_y = harry_x + x, harry_y + y
            if (0 <= new_harry_x < self.rows and 0 <= new_harry_y < self.cols
                    and (new_harry_x, new_harry_y) not in self.dragons):
                if (new_harry_x, new_harry_y) in self.traps:
                    self.traps.remove((new_harry_x,new_harry_y))
                    self.destroyed_traps.add((new_harry_x,new_harry_y))
                    self.previous_location = (harry_x, harry_y)
                    # print("destroy", (new_harry_x, new_harry_y))
                    return ("destroy", (new_harry_x, new_harry_y))

        random.shuffle(self.directions)

        for x, y in self.directions:
            new_harry_x, new_harry_y = harry_x + x, harry_y + y
            if (0 <= new_harry_x < self.rows and 0 <= new_harry_y < self.cols
                    and (new_harry_x, new_harry_y) not in self.dragons)\
                    and (new_harry_x, new_harry_y) != self.previous_location:
                        self.harry_loc = ((new_harry_x, new_harry_y))
                        self.previous_location = (harry_x, harry_y)
                        # print ("move", (new_harry_x, new_harry_y))
                        return ("move", (new_harry_x, new_harry_y))

        random.shuffle(self.directions)

        for x, y in self.directions:
            new_harry_x, new_harry_y = harry_x + x, harry_y + y
            if (0 <= new_harry_x < self.rows and 0 <= new_harry_y < self.cols
                    and (new_harry_x, new_harry_y) not in self.dragons):
                        self.harry_loc = ((new_harry_x, new_harry_y))
                        self.previous_location = (harry_x, harry_y)
                        # print ("move", (new_harry_x, new_harry_y))
                        return ("move", (new_harry_x, new_harry_y))