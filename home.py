# home.py

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import logging

from infinity import *

class HomeHandler(webapp.RequestHandler):
    def get(self):
        params = {}
        test_type = self.request.get("test_type")

        attacker_target = int(self.request.get("attacker_target", 11))
        attacker_target_mod = int(self.request.get("attacker_target_mod", 0))
        attacker_dice = int(self.request.get("attacker_dice", 3))
        attacker_damage = int(self.request.get("attacker_damage", 13))
        attacker_armor = int(self.request.get("attacker_armor", 1))
        attacker_cover = bool(self.request.get("attacker_cover", False))
        
        defender_target = int(self.request.get("defender_target", 11))
        defender_target_mod = int(self.request.get("defender_target_mod", 0))
        defender_damage = int(self.request.get("defender_damage", 13))
        defender_armor = int(self.request.get("defender_armor", 1))
        defender_cover = bool(self.request.get("defender_cover", False))

        args = {
                    "attacker_dice" : attacker_dice,
                    "attacker_target" : attacker_target,
                    "attacker_target_mod" : attacker_target_mod,
                    "attacker_damage" : attacker_damage,
                    "attacker_armor" : attacker_armor,
                    "attacker_cover" : attacker_cover,
                    
                    "defender_target" : defender_target,
                    "defender_target_mod" : defender_target_mod,
                    "defender_damage" : defender_damage,
                    "defender_armor" : defender_armor,
                    "defender_cover" : defender_cover,
                    
                    "range5" : range(1, 6),
                    "range20" : range(1, 21),
                    "target_mods" : range(-12, 4, 3),
                    "armor_values" : range(11)
                }

        if test_type == "BS":
            d_target = defender_target + defender_target_mod + \
                (0 if not attacker_cover else -3)
            d_damage = defender_damage - attacker_armor + \
                (0 if not attacker_cover else -3)
            a_target = attacker_target + attacker_target_mod + \
                (0 if not defender_cover else -3)
            a_damage = attacker_damage - defender_armor + \
                (0 if not defender_cover else -3)
            
            results = ftf_1vN_roll_and_save(d_target, d_damage,
                                            attacker_dice,
                                            a_target, a_damage)
            
            args["show_results"] = True
            args["defender_wounds"] = results[1][0]
            args["draw"] = results[0][0]
            args["attacker_wounds"] = results[2]
        
        logging.debug(args)
        
        self.response.out.write(template.render("home.html", args))
