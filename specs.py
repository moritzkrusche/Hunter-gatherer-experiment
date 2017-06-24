# Specs of payoff per patch for assignment3_main.py

# At this moment, the pattern is fairly predictable, but it can be customised as needed:
# grass: gaussian distribution ("g") with given mean and standard deviation
# grassy_cliff: multimodal distribution ("m") -> 1 in 3 chance of mean -=5, standard deviation +=15
# if a deer is on the patch: mean +=10, 1 in 10 chance of being eaten()
# Note, these settings can be changes through variables in the main file
# Currently mean payoff increases as the gatherer moves away from the cave
# variance (standard deviations) increases per level and differs per group (+2 as group increased)

# FORMAT: payoff_patches[0][0] --> group 1, level 1; payoff_patches[2][1] --> group 3, level 2 etc.

payoff_patches = [[{"patch1": "g, 3, 3", "patch2": "d, 15, 3", "patch3": "m, 5, 3", "patch4": "g, 5, 3"},

                   {"patch1": "m, 2, 4", "patch2": "g, 2, 4", "patch3": "m, 2, 4", "patch4": "g, 2, 4",
                  "patch5": "d, 16, 4", "patch6": "m, 6, 4", "patch7": "d, 16, 4", "patch8": "g, 6, 4",
                  "patch9": "g, 6, 4"},

                 {"patch1": "g, 1, 5", "patch2": "m, 1, 5", "patch3": "g, 1, 5", "patch4": "g, 1, 5",
                "patch5": "m, 5, 5", "patch6": "g, 5, 5", "patch7": "d, 15, 5", "patch8": "m, 5, 5",
                "patch9": "g, 5, 5", "patch10": "g, 8, 5", "patch11": "m, 8, 5", "patch12": "m, 8, 5",
                "patch13": "g, 8, 5", "patch14": "d, 18, 5", "patch15": "m, 8, 5", "patch16": "d, 18, 5"}],

                  [{"patch1": "g, 3, 5", "patch2": "d, 15, 5", "patch3": "m, 5, 5", "patch4": "g, 5, 5"},

                   {"patch1": "m, 2, 6", "patch2": "g, 2, 6", "patch3": "m, 2, 6", "patch4": "g, 2, 6",
                  "patch5": "d, 16, 6", "patch6": "m, 6, 6", "patch7": "d, 16, 6", "patch8": "g, 6, 6",
                  "patch9": "g, 6, 6"},

                   {"patch1": "g, 1, 7", "patch2": "m, 1, 7", "patch3": "g, 1, 7", "patch4": "g, 1, 7",
                "patch5": "m, 5, 7", "patch6": "g, 5, 7", "patch7": "d, 15, 7", "patch8": "m, 5, 7",
                "patch9": "g, 5, 7", "patch10": "g, 8, 7", "patch11": "m, 7, 7", "patch12": "m, 8, 7",
                "patch13": "g, 8, 7", "patch14": "d, 18, 7", "patch15": "m, 8, 7", "patch16": "d, 18, 7"}],

                  [{"patch1": "g, 3, 7", "patch2": "d, 15, 7", "patch3": "m, 5, 7", "patch4": "g, 5, 7"},

                   {"patch1": "m, 2, 8", "patch2": "g, 2, 8", "patch3": "m, 2, 8", "patch4": "g, 2, 8",
                  "patch5": "d, 16, 8", "patch6": "m, 6, 8", "patch7": "d, 16, 8", "patch8": "g, 6, 8",
                  "patch9": "g, 6, 8"},

                   {"patch1": "g, 1, 9", "patch2": "m, 1, 9", "patch3": "g, 1, 9", "patch4": "g, 1, 9",
                "patch5": "m, 5, 9", "patch6": "g, 5, 9", "patch7": "d, 15, 9", "patch8": "m, 5, 9",
                "patch9": "g, 5, 9", "patch10": "g, 8, 9", "patch11": "m, 8, 9", "patch12": "m, 8, 9",
                "patch13": "g, 8, 9", "patch14": "d, 18, 9", "patch15": "m, 8, 9", "patch16": "d, 18, 9"}] ]

