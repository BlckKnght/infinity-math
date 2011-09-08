# infinity.py

from __future__ import division
import logging

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

NORMAL_AMMO = 0
DA_AMMO     = 1
EXP_AMMO    = 2
T2_AMMO     = 3

AP_AMMO     = 4
AP_DA_AMMO  = DA_AMMO | AP_AMMO  #5
AP_EXP_AMMO = EXP_AMMO | AP_AMMO #6
AP_T2_AMMO  = T2_AMMO | AP_AMMO  #7

def armor_save_with_special_ammo(hits, damage, ammo):
    
    if ammo % AP_AMMO == DA_AMMO:
        new_hits = [hits[0]] + [[0]*(d+2) for d in range((len(hits)-1)*2)]
        for h in range(1, len(hits)):
            for c in range(h+1): # crits count as one crit and one regular hit
                new_hits[2*h][c] += hits[h][c]
                
        hits = new_hits
        
    elif ammo % AP_AMMO == EXP_AMMO:
        new_hits = [hits[0]] + [[0]*(d+2) for d in range((len(hits)-1)*3)]
        for h in range(1, len(hits)):
            for c in range(h+1): # crits count as one crit and two regular hits
                new_hits[3*h][c] += hits[h][c]
                
        hits = new_hits

    results = armor_save(hits, damage)

    if ammo % AP_AMMO == T2_AMMO:
        for i in range(len(results)-1, 0, -1):
            results.insert(i, 0) # double damage by inserting zeros for all the odd positions

    return results


def normal_roll_and_save(B, BS, damage, ammo=0):
    return armor_save_with_special_ammo(normal_roll_with_crits(B, BS), damage, ammo)


def ftf_1vN_roll_with_crits(defender_target, attacker_dice, attacker_target):
    nothing_happens = 0
    defender_hits = [0, 0]
    attacker_hits = [[0] * (i+2) for i in range(attacker_dice)]

    # sanity check our arguments
    if defender_target < 1:
        roll = normal_roll_with_crits(attacker_dice, attacker_target)
        nothing_happens = roll[0][0]
        attacker_hits = roll[1:]
        return [nothing_happens, [defender_hits], attacker_hits]
    elif attacker_target < 1:
        roll = normal_roll_with_crits(1, defender_target)
        nothing_happens = roll[0][0]
        defender_hits = roll[1]
        return [nothing_happens, [defender_hits], attacker_hits]
    
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

        # now cancel the ties from lower values
        roll = normal_roll(attacker_dice, 1) # sum of hits == odds of tying on any number
        ties = (min(attacker_target, defender_target) - 1)/20 * (1 - roll[0])
        defender_hits[0] -= ties
        nothing_happens += ties
    # If the defender's target is larger, there's a range of defender rolls that are "unbeatable"
    # by the attacker, except with a crit. The defender's crits can't be beat.
    elif attacker_target < defender_target:
        defender_hits[1] += 1/20 # defender crits
        unbeatable_chance = (defender_target - attacker_target) / 20 # odds of an "unbeatable"
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
        
    #logging.info([nothing_happens, defender_hits, attacker_hits])
    
    # finally, consider case when the defender's roll fails outright (too high)
    defender_fails = 1 - defender_target / 20

    roll = normal_roll_with_crits(attacker_dice, attacker_target)
    #print(defender_fails, roll)
    nothing_happens += defender_fails * roll[0][0] # both fail

    for hits in range(1, len(roll)):
        for crits in range(hits+1):
            attacker_hits[hits-1][crits] += defender_fails * roll[hits][crits]

    return [nothing_happens, [defender_hits], attacker_hits]


def gather_crits(roll):
    hit = 0
    crit = 0
    for hits in range(1, len(roll)):
        hit += roll[hits][0]
        for crits in range(1, hits+1):
            crit += roll[hits][crits]
    return [roll[0][0], hit, crit]


def ignore_crits(roll):
    successes = sum(sum(roll[i]) for i in range(1, len(roll)))

    return roll[0][0], successes


def ftf_1vN_roll_and_save(defender_target, defender_damage, defender_ammo,
                          attacker_dice, attacker_target,
                          attacker_damage, attacker_ammo):
    hits = ftf_1vN_roll_with_crits(defender_target, attacker_dice, attacker_target)

    defender_wounds = armor_save_with_special_ammo([[0]] + hits[1], defender_damage, defender_ammo)
    attacker_wounds = armor_save_with_special_ammo([[0]] + hits[2], attacker_damage, attacker_ammo)

    no_wounds = hits[0] + defender_wounds[0] + attacker_wounds[0]

    return no_wounds, defender_wounds[1:], attacker_wounds[1:]


def resolve_test(attacker_action, attacker_dice,
                 attacker_target, attacker_target_mod,
                 attacker_damage, attacker_ammo,
                 attacker_armor, attacker_cover,
                 defender_action,
                 defender_target, defender_target_mod,
                 defender_damage, defender_ammo,
                 defender_armor, defender_cover):

    a_dice = attacker_dice if attacker_action == "attack" else 1
    d_cover = 0 if attacker_action != "attack" or not defender_cover else 3
    a_cover = 0 if defender_action != "attack" or not attacker_cover else 3
    d_target = defender_target + defender_target_mod - a_cover
    a_target = attacker_target + attacker_target_mod - d_cover
    d_armor = (defender_armor if attacker_ammo < AP_AMMO
               else (defender_armor + 1) // 2)
    a_armor = (attacker_armor if defender_ammo < AP_AMMO
               else (attacker_armor + 1) // 2)
    d_damage = defender_damage - a_armor - a_cover
    a_damage = attacker_damage - d_armor - d_cover

    #logging.warn([d_target, d_damage, defender_ammo,
    #             attacker_dice, a_target, a_damage, attacker_ammo])

    a_action = attacker_action
    d_action = defender_action

    if defender_action == "nothing":
        if attacker_action == "attack":
            roll = normal_roll_and_save(a_dice, a_target,
                                        a_damage, attacker_ammo)
        
        elif attacker_action == "dodge":
            roll = normal_roll(1, a_target)

        else: # attacker_action == "hack"
            roll = gather_crits(normal_roll_with_crits(1, a_target))
            
        return roll[0], [], roll[1:]
    
    else: # face to face roll of some kind
        roll = ftf_1vN_roll_with_crits(d_target, a_dice, a_target)

        if defender_action == "attack":
            defender_results = armor_save_with_special_ammo([[0]] + roll[1], d_damage, defender_ammo)
        elif defender_action == "dodge":
            defender_results = ignore_crits([[0]] + roll[1])
        else: # defender_action == "hack"
            defender_results = gather_crits([[0]] + roll[1])

        if attacker_action == "attack":
            attacker_results = armor_save_with_special_ammo([[0]] + roll[2], a_damage, attacker_ammo)
        elif attacker_action == "dodge":
            attacker_results = ignore_crits([[0]] + roll[2])
        else: # attacker_action == "hack"
            attacker_results = gather_crits([[0]] + roll[2])

        nothing_happens = roll[0] + defender_results[0] + attacker_results[0]

        return nothing_happens, defender_results[1:], attacker_results[1:]
            
