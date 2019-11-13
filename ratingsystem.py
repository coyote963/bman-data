from trueskill import Rating, rate_1vs1

def perform_trueskill_adjustment(killer_profile, victim_profile):
    killer = Rating(mu = killer_profile.mu, sigma = killer_profile.sigma)
    victim = Rating(mu = victim_profile.mu, sigma = victim_profile.sigma)
    new_killer, new_victim = rate_1vs1(killer, victim)
    return {
        'killer_mu' : new_killer.mu,
        'killer_mu_delta' : new_killer.mu - killer.mu,
        'killer_sigma' : new_killer.sigma,
        'killer_sigma_delta' : new_killer.sigma - killer.sigma,
        'victim_mu' : new_victim.mu,
        'victim_mu_delta' : new_victim.mu - victim.mu,
        'victim_sigma' : new_victim.sigma,
        'victim_sigma_delta' : new_victim.sigma - victim.sigma,
    }

