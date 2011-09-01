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
        attacker_ammo = int(self.request.get("attacker_ammo", 0))
        attacker_armor = int(self.request.get("attacker_armor", 1))
        attacker_cover = bool(self.request.get("attacker_cover", False))
        
        defender_target = int(self.request.get("defender_target", 11))
        defender_target_mod = int(self.request.get("defender_target_mod", 0))
        defender_damage = int(self.request.get("defender_damage", 13))
        defender_ammo = int(self.request.get("defender_ammo", 0))
        defender_armor = int(self.request.get("defender_armor", 1))
        defender_cover = bool(self.request.get("defender_cover", False))

        args = {
                    "attacker_dice" : attacker_dice,
                    "attacker_target" : attacker_target,
                    "attacker_target_mod" : attacker_target_mod,
                    "attacker_damage" : attacker_damage,
                    "attacker_ammo" : attacker_ammo,
                    "attacker_armor" : attacker_armor,
                    "attacker_cover" : attacker_cover,
                    
                    "defender_target" : defender_target,
                    "defender_target_mod" : defender_target_mod,
                    "defender_damage" : defender_damage,
                    "defender_ammo" : defender_ammo,
                    "defender_armor" : defender_armor,
                    "defender_cover" : defender_cover,
                    
                    "range5" : range(1, 6),
                    "range20" : range(1, 21),
                    "target_mods" : range(-12, 7, 3),
                    "armor_values" : range(11)
                }

        if test_type == "BS":
            d_cover = 0 if not defender_cover else 3
            a_cover = 0 if not attacker_cover else 3
            d_target = defender_target + defender_target_mod - a_cover
            a_target = attacker_target + attacker_target_mod - d_cover
            d_armor = defender_armor if attacker_ammo < AP_AMMO \
                      else (defender_armor + 1) // 2
            a_armor = attacker_armor if defender_ammo < AP_AMMO \
                      else (attacker_armor + 1) // 2
            d_damage = defender_damage - a_armor - a_cover
            a_damage = attacker_damage - d_armor - d_cover

            logging.warn([d_target, d_damage, defender_ammo,
                         attacker_dice, a_target, a_damage, attacker_ammo])

            results = ftf_1vN_roll_and_save(d_target,
                                            d_damage, defender_ammo,
                                            attacker_dice, a_target,
                                            a_damage, attacker_ammo)
            
            args["show_results"] = True
            args["defender_wounds"] = results[1]
            args["draw"] = results[0][0]
            args["attacker_wounds"] = results[2]
        
        #logging.warn(args)
        
        self.response.out.write(template.render("home.html", args))
