"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.
    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
        nonlocal score0, score1
        if score1 == 2 * score0 or score0 == 2 * score1:
            score0, score1 = score1, score0

    # Main loop
    while score0 < 100 and score1 < 100:
        # Get the current scores of both players
        who_score = get_score(who)
        opponent_score = get_score(other(who))
        # Get the strategy provided by current player
        strategy = get_strategy(who)(who_score, opponent_score)
        # Use above information to select correct dice
        dice = select_dice(who_score, opponent_score)
        # Then roll the dice and update current player's score
        update_score(who, take_turn(strategy, opponent_score, dice))
        # Swine swap if condition holds
        swine()
        # Now it's time for the other player
        who = other(who)

    return score0, score1

#######################
# Phase 2: Strategies #
#######################

def always_roll(n):
    """Return a strategy that always rolls N dice.
    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.
    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=30000):
    """Return a function that returns the average_value of FN when called.
    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.
    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0
    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def ret(*args):
        sum, i = 0, 0
        while i < num_samples:
            sum, i = sum + fn(*args), i + 1
        return sum / num_samples

    return ret


def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Assume that dice always
    return positive outcomes.
    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    10
    """
    _max, number_of_dice, ret = 0, 10, 0
    while number_of_dice > 0:
        avg = make_averaged(roll_dice)(number_of_dice, dice)
        _max = max(_max, avg)
        if avg >= _max:
            ret = number_of_dice
        number_of_dice -= 1

    return ret

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    bacon_points = abs(opponent_score // 10 - opponent_score % 10) + 1

    if bacon_points >= margin:
        return 0
    else:
        return num_rolls

def swap_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least MARGIN points and rolls
    NUM_ROLLS otherwise.
    """
    bacon_points = abs(opponent_score // 10 - opponent_score % 10) + 1

    if opponent_score == 2 * (score + bacon_points):
        return 0
    elif (score + bacon_points) == 2 * opponent_score:
        return num_rolls
    else:
        return bacon_strategy(score, opponent_score, margin, num_rolls)

def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.
    See the per-line comments.
    PS. The expected score of rolling a 4-sided dice is about 3.797.
    PSS. This strategy get an average win rate greater than 0.55, is 0.56 possible?
    """
    bacon_points = abs(opponent_score // 10 - opponent_score % 10) + 1

    # If bacon_points is greater than 3.797, leave opponent with 4-sided dice
    if (score + bacon_points + opponent_score) % 7 == 0 and bacon_points >= 4:
        return 0
    # Try to trigger a beneficial swine swap by trying score only one point
    elif 2 * (score + 1) == opponent_score:
        return swap_strategy(score, opponent_score, 10, 10)
    # Decrease num_rolls to 3 and margin to 4, more suitable for a 4-sided dice
    elif (score + opponent_score) % 7 == 0:
        return swap_strategy(score, opponent_score, 4, 3)
    # More offensive when losing
    elif score < opponent_score:
        return swap_strategy(score, opponent_score, 9, 6)
    # More defensive when leading
    else:
        return swap_strategy(score, opponent_score, 7, 4)

asddqwkndoieqroi2eqwio
##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.
    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()
