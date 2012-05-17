# home.py

import webapp2 as webapp2
from webapp2_extras import jinja2
import logging

from infinity import *

class HomeHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def get(self):
        attacker_action = self.request.get("attacker_action")
        attacker_target = int(self.request.get("attacker_target", 11))
        attacker_target_mod = int(self.request.get("attacker_target_mod", 0))
        attacker_dice = int(self.request.get("attacker_dice", 3))
        attacker_damage = int(self.request.get("attacker_damage", 13))
        attacker_ammo = int(self.request.get("attacker_ammo", 0))
        attacker_armor = int(self.request.get("attacker_armor", 1))
        attacker_cover = bool(self.request.get("attacker_cover", False))

        defender_action = self.request.get("defender_action", "attack")
        defender_target = int(self.request.get("defender_target", 11))
        defender_target_mod = int(self.request.get("defender_target_mod", 0))
        defender_damage = int(self.request.get("defender_damage", 13))
        defender_ammo = int(self.request.get("defender_ammo", 0))
        defender_armor = int(self.request.get("defender_armor", 1))
        defender_cover = bool(self.request.get("defender_cover", False))

        args = {
                    "attacker_action" : attacker_action,
                    "attacker_dice" : attacker_dice,
                    "attacker_target" : attacker_target,
                    "attacker_target_mod" : attacker_target_mod,
                    "attacker_damage" : attacker_damage,
                    "attacker_ammo" : attacker_ammo,
                    "attacker_armor" : attacker_armor,
                    "attacker_cover" : attacker_cover,

                    "defender_action" : defender_action,
                    "defender_target" : defender_target,
                    "defender_target_mod" : defender_target_mod,
                    "defender_damage" : defender_damage,
                    "defender_ammo" : defender_ammo,
                    "defender_armor" : defender_armor,
                    "defender_cover" : defender_cover,
                    
                    "target_values" : range(8, 21),
                    "target_mods" : range(-15, 7, 3),
                    "armor_values" : range(11),
                    "burst_values" : range(1, 6),
                    "damage_values" : range(8, 16)
                }

        if attacker_action:
            draw, defender_results, attacker_results = \
                  resolve_test(attacker_action, attacker_dice,
                               attacker_target, attacker_target_mod,
                               attacker_damage, attacker_ammo,
                               attacker_armor, attacker_cover,
                               defender_action,
                               defender_target, defender_target_mod,
                               defender_damage, defender_ammo,
                               defender_armor, defender_cover)
            
            args["show_results"] = True
            d_results = [round(dr * 100, 2) for dr in defender_results
                                        if dr > 0.001]
            a_results = [round(ar * 100, 2) for ar in attacker_results
                                        if ar > 0.001]

            args["defender_results"] = d_results
            args["attacker_results"] = a_results

            args["draw"] = 100 - (sum(a_results) + sum(d_results))

        else:
            args["attacker_action"] = "attack"
        
        #logging.info(args)
        
        self.response.out.write(self.jinja2.render_template("home.html", **args))
