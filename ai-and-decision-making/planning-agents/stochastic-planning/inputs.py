inputs = [
    {
        "optimal": True,
        "turns_to_go": 10,
        "map": [
            ['P', 'P', 'I', 'P'],
            ['P', 'P', 'I', 'P'],
            ['P', 'P', 'P', 'P'],
            ['P', 'P', 'I', 'P']
        ],
        "wizards": {'Harry Potter': {"location": (2, 0)}
                    },
        "horcrux": {'Nagini': {"location": (0, 3),
                               "possible_locations": ((0, 3), (1, 3), (2, 2)),
                               "prob_change_location": 0.9}
                    },
        "death_eaters": {'Lucius Malfoy': {"index": 0,
                                           "path": [(1, 1), (2, 1), (2, 2)]}},
    },

    {
        "optimal": True,
        "turns_to_go": 100,
        "map": [
            ['I', 'I', 'P'],
            ['P', 'I', 'P'],
            ['I', 'P', 'P'],
            ['P', 'I', 'P']
        ],
        "wizards": {'Harry Potter': {"location": (2, 2)}
                    },
        "horcrux": {'Nagini': {"location": (0, 2),
                               "possible_locations": ((0, 2), (1, 2), (2, 2)),
                               "prob_change_location": 0.9},
                    'Diary': {"location": (0, 0),
                              "possible_locations": ((0, 0), (1, 0), (2, 0)),
                              "prob_change_location": 0.3}
                    },
        "death_eaters": {'Snape': {"index": 1,
                                           "path": [(2, 2), (2, 1)]}},
    },
    {
        "optimal": True,
        "turns_to_go": 100,
        "map": [
            ['I', 'I', 'P'],
            ['P', 'I', 'P'],
            ['I', 'P', 'P'],
            ['P', 'I', 'P']
        ],
        "wizards": {'Harry Potter': {"location": (0, 2)}
                    },
        "horcrux": {'Nagini': {"location": (0, 2),
                                "possible_locations": ((0, 2), (1, 2), (2, 2)),
                                "prob_change_location": 0.9},
                    'Diary': {"location": (0, 0),
                                "possible_locations": ((0, 0), (2, 0)),
                                "prob_change_location": 0.45}
                    },
        "death_eaters": {'Snape': {"index": 1,
                                            "path": [(1, 0), (2, 1)]},
                        'random_de': {"index": 0,
                                    "path": [(3, 2)]}},
    },

    # {
    #     "optimal": False,
    #     "turns_to_go": 30,
    #     "map": [
    #         ['P', 'P', 'I', 'P'],
    #         ['P', 'P', 'I', 'P'],
    #         ['P', 'P', 'P', 'P'],
    #         ['P', 'P', 'I', 'P']
    #     ],
    #     "wizards": {'Harry Potter': {"location": (2, 0)},
    #                 'Ron Weasley': {"location": (2, 1)}
    #                 },
    #     "horcrux": {'Nagini': {"location": (0, 3),
    #                            "possible_locations": ((0, 3), (1, 3), (2, 2)),
    #                            "prob_change_location": 0.4}
    #                 },
    #     "death_eaters": {'Lucius Malfoy': {"index": 0,
    #                                        "path": [(1, 1), (1, 0)]}},
    # },
    #
    # {
    #     "optimal": False,
    #     "turns_to_go": 100,
    #     "map": [
    #         ['I', 'P', 'P', 'P', 'P', 'P', 'I'],
    #         ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
    #         ['P', 'P', 'I', 'I', 'I', 'P', 'P'],
    #         ['P', 'P', 'I', 'P', 'I', 'P', 'P'],
    #         ['P', 'P', 'I', 'I', 'I', 'P', 'P'],
    #         ['P', 'P', 'P', 'P', 'P', 'P', 'P'],
    #         ['P', 'P', 'P', 'P', 'P', 'P', 'I']
    #     ],
    #     "wizards": {'Harry Potter': {"location": (2, 0)}
    #                 },
    #     "horcrux": {'Nagini': {"location": (3, 3),
    #                            "possible_locations": ((2, 2), (3, 3), (1, 1)),
    #                            "prob_change_location": 0.5}
    #                 },
    #     "death_eaters": {'Lucius Malfoy': {"index": 0,
    #                                        "path": [(1, 1), (1, 0)]},
    #                     'Snape': {"index": 0,
    #                             "path": [(5, 4), (5, 5), (5, 4)]}},
    #                     'random_de': {"index": 0,
    #                             "path": [(3, 3)]}
    # },

# {'optimal': False, 'turns_to_go': 100, 'map': [['P', 'P', 'P', 'I', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
#                                                                ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'I', 'P', 'I', 'P', 'P'],
#                                                                ['P', 'P', 'I', 'P', 'P', 'P', 'I', 'P', 'P', 'I', 'P', 'P', 'P', 'I'],
#                                                                ['I', 'P', 'P', 'P', 'I', 'P', 'P', 'I', 'P', 'P', 'P', 'I', 'P', 'P'],
#                                                                ['I', 'P', 'I', 'P', 'P', 'P', 'P', 'I', 'P', 'I', 'P', 'P', 'P', 'P'],
#                                                                ['P', 'P', 'P', 'I', 'P', 'P', 'I', 'I', 'P', 'P', 'P', 'P', 'P', 'P'],
#                                                                ['P', 'I', 'P', 'P', 'I', 'I', 'P', 'P', 'P', 'P', 'I', 'I', 'P', 'I'],
#                                                                ['P', 'P', 'P', 'I', 'P', 'P', 'I', 'P', 'I', 'P', 'P', 'P', 'P', 'I'],
#                                                                ['I', 'I', 'I', 'P', 'P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P'],
#                                                                ['P', 'P', 'P', 'I', 'P', 'P', 'P', 'I', 'I', 'P', 'P', 'P', 'P', 'P'],
#                                                                ['P', 'P', 'P', 'I', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
#                                                                ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'I'],
#                                                                ['P', 'P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'I', 'P', 'P'],
#                                                                ['I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'I', 'I', 'P', 'P', 'I', 'P']],
#                  'wizards': {'Wizard_0': {'location': (8, 3)},
#                              'Wizard_1': {'location': (10, 10)},
#                              'Wizard_2': {'location': (12, 0)},
#                              'Wizard_3': {'location': (8, 12)}},
#
#                  'horcrux': {'Horcrux_0': {'location': (4, 10), 'possible_locations': [(12, 13), (9, 2), (12, 3), (5, 0), (1, 3), (4, 10)],'prob_change_location': 0.78},
#                             'Horcrux_1': {'location': (9, 13), 'possible_locations': [(8, 13), (4, 5), (3, 12), (9, 13)], 'prob_change_location': 0.79},
#                              'Horcrux_2': {'location': (7, 7), 'possible_locations': [(1, 1), (13, 10), (12, 13), (4, 5), (0, 2), (7, 7)], 'prob_change_location': 0.12},
#                              'Horcrux_3': {'location': (10, 8), 'possible_locations': [(1, 2), (7, 1), (0, 12), (3, 13), (6, 6), (5, 9), (10, 8)], 'prob_change_location': 0.23},
#                              'Horcrux_4': {'location': (8, 7), 'possible_locations': [(11, 3), (5, 1), (3, 13), (5, 10), (6, 9), (8, 7)], 'prob_change_location': 0.12},
#                              'Horcrux_5': {'location': (5, 1), 'possible_locations': [(9, 9), (6, 8), (1, 8), (11, 12), (2, 3), (11, 4), (5, 1)], 'prob_change_location': 0.78},
#                              'Horcrux_6': {'location': (10, 13), 'possible_locations': [(13, 1), (6, 2), (10, 11), (1, 10), (10, 13)], 'prob_change_location': 0.88},
#                              'Horcrux_7': {'location': (12, 12), 'possible_locations': [(0, 1), (6, 8), (11, 6), (12, 12)], 'prob_change_location': 0.96}},
#
#                  'death_eaters':
#                 {'Death_Eater_0': {'index': 0, 'path': [(10, 11), (12, 6), (4, 8), (6, 9), (5, 12)]},
#                 'Death_Eater_1': {'index': 0, 'path': [(4, 13), (2, 7), (10, 0), (5, 0), (9, 11)]},
#                 'Death_Eater_2': {'index': 0, 'path': [(4, 10), (9, 0), (1, 4)]}}},
#
#     {'optimal': False, 'turns_to_go': 160,
#      'map': [['P', 'I', 'P', 'I', 'P', 'P', 'I', 'P', 'P', 'P'], ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'I', 'P', 'P'],
#              ['I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'I'], ['P', 'I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
#              ['P', 'P', 'P', 'I', 'I', 'P', 'I', 'I', 'I', 'P'], ['P', 'P', 'I', 'P', 'P', 'P', 'P', 'I', 'P', 'I'],
#              ['P', 'P', 'P', 'P', 'I', 'P', 'I', 'I', 'I', 'P'], ['P', 'P', 'I', 'P', 'I', 'P', 'P', 'I', 'P', 'I'],
#              ['I', 'I', 'P', 'P', 'I', 'P', 'I', 'I', 'I', 'P'], ['P', 'P', 'P', 'I', 'P', 'P', 'P', 'P', 'P', 'P']],
#      'wizards': {'Wizard_0': {'location': (4, 9)}, 'Wizard_1': {'location': (1, 6)}, 'Wizard_2': {'location': (1, 8)},
#                  'Wizard_3': {'location': (8, 9)}}, 'horcrux': {
#         'Horcrux_0': {'location': (4, 9), 'possible_locations': [(4, 5), (3, 3), (0, 8), (4, 9)],
#                       'prob_change_location': 0.78},
#         'Horcrux_1': {'location': (2, 1), 'possible_locations': [(9, 1), (7, 0), (3, 9), (0, 5), (2, 1)],
#                       'prob_change_location': 0.57},
#         'Horcrux_2': {'location': (7, 3), 'possible_locations': [(5, 3), (9, 6), (1, 8), (7, 3)],
#                       'prob_change_location': 0.09}},
#      'death_eaters': {'Death_Eater_0': {'index': 0, 'path': [(5, 5), (9, 9), (9, 6), (3, 3), (6, 0)]},
#                       'Death_Eater_1': {'index': 0, 'path': [(1, 1), (9, 2), (0, 5)]},
#                       'Death_Eater_2': {'index': 0, 'path': [(1, 0), (9, 9), (3, 9), (3, 6)]},
#                       'Death_Eater_3': {'index': 0, 'path': [(4, 5), (3, 8), (2, 2), (0, 0)]},
#                       'Death_Eater_4': {'index': 0, 'path': [(9, 6), (3, 5), (0, 5)]},
#                       'Death_Eater_5': {'index': 0, 'path': [(5, 3), (2, 7), (1, 4)]},
#                       'Death_Eater_6': {'index': 0, 'path': [(8, 9), (3, 9), (3, 4), (7, 8)]},
#                       'Death_Eater_7': {'index': 0, 'path': [(2, 3), (7, 5), (2, 5), (0, 4)]}}},
#



]