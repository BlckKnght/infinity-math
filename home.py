# home.py

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import logging

from infinity import *

class HomeHandler(webapp.RequestHandler):
    def get(self):
        params = {}
        test_type = self.request.get("test_type")
        if test_type == "BS":
            defender_target = int(self.request.get("defender_target"))
            defender_damage = int(self.request.get("defender_damage"))
            attacker_dice = int(self.request.get("attacker_dice"))
            attacker_target = int(self.request.get("attacker_target"))
            attacker_damage = int(self.request.get("attacker_damage"))
            results = ftf_1vN_roll_and_save(defender_target,
                                            defender_damage,
                                            attacker_dice,
                                            attacker_target,
                                            attacker_damage)
            args = {
                    "defender_target" : defender_target,
                    "defender_damage" : defender_damage,
                    "attacker_dice" : attacker_dice,
                    "attacker_target" : attacker_target,
                    "attacker_damage" : attacker_damage,
                    "show_results" : True,
                    "defender_wounds" : results[1][0],
                    "draw" : str(results[0][0]),
                    "attacker_wounds" : results[2]
                }
        else:
            args = {
                    "defender_target" : 11,
                    "defender_damage" : 12,
                    "attacker_dice" : 3,
                    "attacker_target" : 11,
                    "attacker_damage" : 12,
                }

        args["range5"] = range(1, 6)
        args["range20"] = range(1, 21)

        logging.debug(args)
        
        self.response.out.write(template.render("home.html", args))


