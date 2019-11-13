from schemas import PlayerAccount,DMMatch, Player, DMKill, DMProfile, DMRatingInstance
from ratingsystem import perform_trueskill_adjustment
from mongoengine import DoesNotExist
killer = PlayerAccount(
    platform = '0',
    profile = '76561198291746286'
)
victim = PlayerAccount(
    platform = '0',
    profile = '76561198303147008'
)

dm_killer_player = Player.objects.get(profile = killer)
dm_victim_player = Player.objects.get(profile = victim)

try:
    dm_killer_profile = DMProfile.objects.get(player = dm_killer_player)
except DoesNotExist:
    dm_killer_profile = DMProfile(player = dm_killer_player)

try:
    dm_victim_profile = DMProfile.objects.get(player = dm_victim_player)
except DoesNotExist:
    dm_victim_profile = DMProfile(player = dm_victim_player)


#Run this once to make the profiles
# dm_killer_profile = DMProfile(player = dm_killer_player)
# dm_victim_profile = DMProfile(player = dm_victim_player)

#run this when you already got profiles


current_match = DMMatch(map_name = "lfkdj")
current_match.save()
dm_kill = DMKill(
    victim = dm_killer_player,
    killer = dm_victim_player,
    weapon = '4',
    killer_location = '2,3',
    victim_location = '4,5',
    match = current_match
)
# Perform the rating adjustment, Refactor into a separate func
# dm_killer_profile = DMProfile.objects.get(player=killer.profile)
# dm_victim_profile = DMProfile.objects.get(player=victim.profile)


adjustment = perform_trueskill_adjustment(dm_killer_profile, dm_victim_profile)

dm_killer_profile.mu = adjustment['killer_mu']
dm_killer_profile.sigma = adjustment['killer_sigma']
dm_victim_profile.mu = adjustment['victim_mu']
dm_victim_profile.sigma = adjustment['victim_sigma']

dm_killer_profile.save()
dm_victim_profile.save()

killer_rating_instance = DMRatingInstance(mu = adjustment['killer_mu'],
    sigma = adjustment['killer_sigma'],
    mu_delta= adjustment['killer_mu_delta'],
    sigma_delta = adjustment['killer_sigma_delta'])

victim_rating_instance = DMRatingInstance(mu = adjustment['victim_mu'],
    sigma = adjustment['victim_sigma'],
    mu_delta= adjustment['victim_mu_delta'],
    sigma_delta = adjustment['victim_sigma_delta'])

dm_kill.killer_rating = killer_rating_instance
dm_kill.victim_rating = victim_rating_instance

dm_kill.save()