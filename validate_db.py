from schemas import DMMatch, SVLMatch, Player, DMMessage, SVLMessage, SVLRound, SVLDeath,SVLKill, DMKill, DMProfile

collections = [DMMatch, SVLMatch, Player, DMMessage, SVLMessage, SVLRound, SVLDeath,SVLKill, DMKill, DMProfile]

for s in collections:
    for x in s.objects:
        print(x)