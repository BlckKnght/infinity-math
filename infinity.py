# infinity.py

from __future__ import division
from collections import defaultdict

def binomial_coefficient(n, k):
    if k > n-k:
        k = n-k

    result = 1;
    for i in range(k):
        result *= (n-i) / (i+1)

    return result

  
def normal_roll(dice, target):
    if target <= 0:
        return [1] + [0]*dice
    
    success_odds = target / 20
    successes = []
    for i in range(dice+1):
        coef = binomial_coefficient(dice, i)
        successes.append(coef * success_odds**i * (1-success_odds)**(dice-i))
    return successes


def normal_roll_with_crits(dice, target):
    if target <= 0:
        return [[1]] + [[0]*(d+2) for d in range(dice)]
    
    successes = normal_roll(dice, target)
    crit_odds = 1/target
    results = []
    for s in range(len(successes)):
        crits = []
        for c in range(s+1):
            coef = binomial_coefficient(s, c)
            crits.append(successes[s] * coef *
                         crit_odds**c * (1-crit_odds)**(s-c))
            
        results.append(crits)
        
    return results


def armor_save(hits, damage):
    results = [0]*len(hits)

    #print(hits)
    
    for h in range(len(hits)):
        for c in range(len(hits[h])):
            wounds = normal_roll(h-c, damage)
            for w in range(len(wounds)):
                results[w+c] += hits[h][c] * wounds[w]

    return results


def normal_roll_and_save(B, BS, damage):
    return armor_save(normal_roll_with_crits(B, BS), damage)


def ftf_1vN_roll_with_crits(defender_target, attacker_dice, attacker_target):
    nothing_happens = 0
    defender_hits = [0, 0]
    attacker_hits = [[0] * (i+2) for i in range(attacker_dice)]

    #print([nothing_happens, defender_hits, attacker_hits])

    # we work through the possible defender rolls, starting with the lowest

    # When the defender rolls less than both targets, he'll succeed unless the attacker
    # rolls between the defender's roll and the attacker's target. This is equivalent
    # to a normal roll with (attacker_target - defender_roll) as the target (modified
    # to account for the ties the attacker should win).
    for defender_roll in range(1, min(defender_target, attacker_target)):
        target = attacker_target - defender_roll

        if attacker_target > defender_target: # modify for ties that favor the attacker
            target += 1

        roll = normal_roll_with_crits(attacker_dice, target)

        #print(defender_roll, roll)
        
        defender_hits[0] += 1/20 * roll[0][0] # defender wins, no crit
        for hits in range(1, len(roll)): # attaker wins
            for crits in range(hits+1): # how many crits?
                #print(hits, crits)
                attacker_hits[hits-1][crits] += 1/20 * roll[hits][crits]

    #print([nothing_happens, defender_hits, attacker_hits])
                
    # Now consider the defender rolling near the target values

    # If the targets are equal, crits can cancel out and ties on the lower rolls need
    # an adjustment (they were counted for to the defender above).
    if attacker_target == defender_target:
        defender_hits[1] += 1/20 * (19/20)**attacker_dice # defender crits and attacker doesn't
        nothing_happens += 1/20 * (1-(19/20)**attacker_dice) # both players crit, so they cancel

        for defender_roll in range(1, defender_target): # now cancel the ties from lower values
            roll = normal_roll_with_crits(attacker_dice, defender_roll) # == crits on this roll
            for hits in range(1, len(roll)):
                for crits in range(1, hits+1):
                    ties = 1/20 * roll[hits][crits]
                    defender_hits[0] -= ties
                    nothing_happens += ties
    # If the defender's target is larger, there's a range of defender rolls that are "unbeatable"
    # by the attacker, except with a crit. The defender's crits can't be beat.
    elif attacker_target < defender_target:
        defender_hits[1] += 1/20 # defender crits
        unbeatable_chance = (defender_target - attacker_target - 1) / 20 # odds of an "unbeatable"
        if unbeatable_chance:
            roll = normal_roll(attacker_dice, 1) # attacker crits
            defender_hits[0] += unbeatable_chance * roll[0] # no crits
            for crits in range(1, len(roll)):
                attacker_hits[crits-1][crits] += unbeatable_chance * roll[crits]
    # When attacker's target is higher we just need to handle defender crits.
    # They can only be beaten by attacker crits.
    else:
        roll = normal_roll(attacker_dice, 1) # attacker crits
        defender_hits[1] += 1/20 * roll[0] # no crit
        for crits in range(1, len(roll)):
            attacker_hits[crits-1][crits] += 1/20 * roll[crits]
        
    #print ([nothing_happens, defender_hits, attacker_hits])
    
    # finally, consider case when the defender's roll fails outright (too high)
    defender_fails = 1 - defender_target / 20

    roll = normal_roll_with_crits(attacker_dice, attacker_target)
    #print(defender_fails, roll)
    nothing_happens += defender_fails * roll[0][0] # both fail

    for hits in range(1, len(roll)):
        for crits in range(hits+1):
            attacker_hits[hits-1][crits] += defender_fails * roll[hits][crits]

    return [nothing_happens, [defender_hits], attacker_hits]


def ftf_1vN_roll_and_save(defender_target, defender_damage,
                          attacker_dice, attacker_target, attacker_damage):
    hits = ftf_1vN_roll_with_crits(defender_target, attacker_dice, attacker_target)

    defender_wounds = armor_save([[0]] + hits[1], defender_damage)
    attacker_wounds = armor_save([[0]] + hits[2], attacker_damage)

    no_wounds = hits[0] + defender_wounds[0] + attacker_wounds[0]

    return [[no_wounds], defender_wounds[1:], attacker_wounds[1:]]
