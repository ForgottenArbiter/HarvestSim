from collections import defaultdict
import functools
from dataclasses import dataclass
import scipy
import itertools
import numpy as np


@dataclass
class Settings:

    # These parameters are economic parameters and should be changed to reflect the current market prices
    yellow_value: float = 1/16
    blue_value: float = 1/26
    purple_value: float = 1/26
    sacred_blossom_value: float = 230.0

    # This controls the BASE quantity of your maps (in percent)
    # Do not add bonuses from map quality, fragments, kirac crafts, or atlas passives
    # Pack size is calculated based on this map quality as floor((map quality) / 2.6)
    base_map_quantity: int = 60

    # Set this to True if you guarantee harvest through sextants or the map device
    guaranteed_harvest_spawn: bool = False

    # The following are your bonuses from atlas passives
    # IMPORTANT: Enter the values AFTER Grand Design/Wandering Path are applied
    # Use percents when applicable
    bumper_crop: bool = True   # 50% chance for an additional harvest
    bountiful_harvest: bool = True   # 10% chance for an additional monster
    heart_of_the_grove: bool = True   # 60% increased T4 chance, 10% chance for unchosen crop not to wilt
    doubling_season: bool = True   # Lifeforce has a 10% chance to be duplicated
    crop_rotation: bool = False   # Harvests only contain T1 plants, harvesting crops upgrades crops of different colors

    increased_t3_crop_chance: int = 30   # Up to 3 small nodes at 10% each
    increased_quantity_of_lifeforce: int = 18  # Up to 6 small nodes at 3% each
    duplicated_monsters_chance: int = 6  # Up to 2 small nodes at 3% each

    additional_sacred_grove_chance: int = 45   # 45% chance if you take all relevant nodes
    additional_extra_content_chance: int = 14   # Up to 18% chance if you block all content other than Harvest
    stream_of_consciousness: bool = False   # 50% increased base chance to spawn a Sacred Grove

    reduced_blue_chance: int = 0   # 10% + 10% + 25% chance if you take all relevant nodes
    reduced_yellow_chance: int = 0
    reduced_purple_chance: int = 0

    increased_quantity: int = 15   # Up to 15% with every small quantity node on the atlas tree
    increased_map_modifier_effect: int = 30   # Up to 30% with every small map modifier effect node on the atlas tree
    increased_pack_size: int = 0   # Grand Design can provide 1% for every notable

    # The following are bonuses from crafting (use percents here, or whole numbers)
    map_quality: int = 20   # Up to 20 under normal circumstances, adds to map quantity
    kirac_craft_quantity: int = 0   # Up to 0.08 for the free Kirac craft
    fragment_quantity: int = 0   # 5 per sacrifice fragment, for example
    fragment_pack_size: int = 0   # Pack size from Growing Hordes goes here

    # The following are sextants to double lifeforce and guarantee a certain color
    blue_sextant: bool = False
    yellow_sextant: bool = False
    purple_sextant: bool = False

    # This option can change our implementation of the sextant to reroll plot generation until the
    # chosen color occurs. Otherwise, the implementation is to only roll the color of one crop per harvest.
    sextant_reroll_implementation: bool = False

    # These parameters are determined from extensive testing and should not be changed for realistic results
    # (except for the low confidence values, if desired)
    t4_lifeforce: float = 235.0  # Low confidence
    t3_lifeforce: float = 47.0
    t2_lifeforce: float = 18.5
    t1_lifeforce: float = 7.25
    t4_dropchance: float = 1.0
    t3_dropchance: float = 1.0
    t2_dropchance: float = 0.1
    t1_dropchance: float = 0.02
    t4_seed_chance: float = 0.01  # Low confidence
    t2_binom_n: float = 8
    t2_binom_p: float = 0.75
    t3_binom_n: float = 3
    t3_binom_p: float = 0.25
    base_sacred_grove_chance: float = 0.08  # Data from poedb, in fraction, not in percent
    base_three_harvest_chance: float = 0.5  # Base chance of a sacred grove having 3 harvests
    base_four_harvest_chance: float = 0.5  # Base chance of a sacred grove having 4 harvests
    t1_crop_rotation_upgrade_chance: float = 0.25
    t2_crop_rotation_upgrade_chance: float = 0.20
    t3_crop_rotation_upgrade_chance: float = 0.03


@dataclass
class SeedTier:
    base_drop: float
    drop_chance: float
    is_boss: bool
    distribution: scipy.stats.rv_discrete
    support: list


def has_sextant(settings: Settings):
    return settings.yellow_sextant or settings.blue_sextant or settings.purple_sextant


def get_expected_lifeforce(num_seeds: int, seed_tier: SeedTier, area_iiq: int, pack_size: int, settings: Settings):
    if not seed_tier.is_boss:
        expected_monsters = num_seeds * (1 + pack_size / 100)
    else:
        expected_monsters = num_seeds
    expected_monsters *= (1 + settings.duplicated_monsters_chance / 100)
    lifeforce_mod = 1 + area_iiq / 200 + settings.increased_quantity_of_lifeforce / 100
    lifeforce_per_monster = seed_tier.base_drop * seed_tier.drop_chance * lifeforce_mod
    lifeforce_final_mult = 1.1 if settings.doubling_season else 1.0
    if has_sextant(settings):
        lifeforce_final_mult *= 2.0
    return lifeforce_per_monster * expected_monsters * lifeforce_final_mult


def get_crop_lifeforce_distribution(area_iiq: int, pack_size: int, settings: Settings):
    t4_chance = settings.t4_seed_chance
    if settings.heart_of_the_grove:
        t4_chance *= 1.6
    t4 = SeedTier(settings.t4_lifeforce, settings.t4_dropchance, True, scipy.stats.bernoulli(t4_chance), list(range(2)))
    t3_p = settings.t3_binom_p * (1 + settings.increased_t3_crop_chance / 100)
    t3 = SeedTier(settings.t3_lifeforce, settings.t3_dropchance, False,
                  scipy.stats.binom(settings.t3_binom_n, t3_p), list(range(settings.t3_binom_n + 1)))
    t2 = SeedTier(settings.t2_lifeforce, settings.t2_dropchance, False,
                  scipy.stats.binom(settings.t2_binom_n, settings.t2_binom_p), list(range(settings.t2_binom_n + 1)))
    t1 = SeedTier(settings.t1_lifeforce, settings.t1_dropchance, False, None, list(range(24)))

    all_seed_supports = (t4.support, t3.support, t2.support)
    lifeforce_probability_dict = defaultdict(int)
    for t4_seeds, t3_seeds, t2_seeds in itertools.product(*all_seed_supports):
        t1_seeds = 23 - (t4_seeds + t3_seeds + t2_seeds)
        probability = t4.distribution.pmf(t4_seeds) * t3.distribution.pmf(t3_seeds) * t2.distribution.pmf(t2_seeds)
        expected_lifeforce = 0
        for num_seeds, tier in [(t4_seeds, t4), (t3_seeds, t3), (t2_seeds, t2), (t1_seeds, t1)]:
            expected_lifeforce += get_expected_lifeforce(num_seeds, tier, area_iiq, pack_size, settings)
        lifeforce_probability_dict[expected_lifeforce] += probability

    support_probability_pairs = sorted(lifeforce_probability_dict.items())
    lifeforce_support, lifeforce_probabilities = zip(*support_probability_pairs)
    return np.array(lifeforce_support), np.array(lifeforce_probabilities)


def get_value_distribution_from_lifeforce_distribution(support, probabilities, settings: Settings):
    vivid_support = support * settings.yellow_value
    wild_support = support * settings.purple_value
    primal_support = support * settings.blue_value
    total_support = np.concatenate([vivid_support, wild_support, primal_support])
    vivid_probabilities = probabilities * (1 - settings.reduced_yellow_chance / 100)
    wild_probabilities = probabilities * (1 - settings.reduced_purple_chance / 100)
    primal_probabilities = probabilities * (1 - settings.reduced_blue_chance / 100)
    total_probabilities = np.concatenate([vivid_probabilities, wild_probabilities, primal_probabilities])
    total_probabilities /= np.sum(total_probabilities)
    new_order = np.argsort(total_support)
    return total_support[new_order], total_probabilities[new_order]


def distribute_cdf_to_new_support(old_support, new_support, old_cdf):
    old_index = 0
    old_value = old_support[0]
    old_prob = 0
    new_cdf = np.zeros_like(new_support, dtype=old_cdf.dtype)
    for new_index, new_value in enumerate(new_support):
        while new_value >= old_value:
            old_index += 1
            if old_index >= len(old_support):
                old_value = np.inf
                old_prob = 1
            else:
                old_value = old_support[old_index]
                old_prob = old_cdf[old_index - 1]
        new_cdf[new_index] = old_prob
    return new_cdf


def get_max_pmf(support_1, support_2, pmf_1, pmf_2):
    combined_support = np.array(sorted(set(support_1).union(set(support_2))))
    cdf_1 = np.cumsum(pmf_1)
    cdf_2 = np.cumsum(pmf_2)
    cdf_1 = distribute_cdf_to_new_support(support_1, combined_support, cdf_1)
    cdf_2 = distribute_cdf_to_new_support(support_2, combined_support, cdf_2)
    max_cdf = cdf_1 * cdf_2
    max_pmf = np.diff(max_cdf, prepend=0)
    return combined_support, max_pmf


def get_crop_pair_value(lifeforce_support, lifeforce_probabilities, settings: Settings):
    value_support, value_probabilities = get_value_distribution_from_lifeforce_distribution(
        lifeforce_support, lifeforce_probabilities, settings)
    no_wilt_chance = 10 if settings.heart_of_the_grove else 0
    if not has_sextant(settings):
        value_cdf = np.cumsum(value_probabilities)
        max_value_cdf = value_cdf * value_cdf
        max_value_pmf = np.diff(max_value_cdf, prepend=0)
        expected_crop_value = np.dot(value_support, value_probabilities)
        expected_max_value = np.dot(value_support, max_value_pmf)
        total_value = (no_wilt_chance / 100) * expected_crop_value * 2 + (1 - no_wilt_chance / 100) * expected_max_value
    else:
        if settings.blue_sextant:
            sextant_lifeforce_value = settings.blue_value
        elif settings.yellow_sextant:
            sextant_lifeforce_value = settings.yellow_value
        else:
            sextant_lifeforce_value = settings.purple_value
        if settings.sextant_reroll_implementation:
            #  TODO: Unimplemented
            raise NotImplementedError()
        else:
            guaranteed_support = lifeforce_support * sextant_lifeforce_value
            guaranteed_pmf = lifeforce_probabilities
            random_support = value_support
            random_pmf = value_probabilities
            max_support, max_pmf = get_max_pmf(guaranteed_support, random_support, guaranteed_pmf, random_pmf)
            expected_max_value = np.dot(max_support, max_pmf)
            expected_guaranteed_value = np.dot(guaranteed_support, guaranteed_pmf)
            expected_random_value = np.dot(random_support, random_pmf)
            expected_combined_value = expected_guaranteed_value + expected_random_value
            total_value = (no_wilt_chance / 100) * expected_combined_value + (1 - no_wilt_chance / 100) * expected_max_value

    return total_value


def get_sacred_grove_value(crop_pair_value, settings: Settings):
    mean_crop_pairs = settings.base_three_harvest_chance * 3 + settings.base_four_harvest_chance * 4
    mean_crop_pairs += settings.bumper_crop * 0.5
    return mean_crop_pairs * crop_pair_value


def get_area_stats(settings: Settings):
    area_iiq = int(settings.base_map_quantity * (1 + settings.increased_map_modifier_effect / 100))
    area_iiq += settings.fragment_quantity + settings.kirac_craft_quantity + settings.increased_quantity + settings.map_quality
    pack_size = int(settings.base_map_quantity * (1 + settings.increased_map_modifier_effect / 100) / 2.6)
    pack_size += settings.increased_pack_size + settings.fragment_pack_size
    return area_iiq, pack_size


def get_harvest_spawn_chance(settings: Settings):
    if settings.guaranteed_harvest_spawn:
        return 1.0
    else:
        harvest_spawn_chance = settings.base_sacred_grove_chance
        if settings.stream_of_consciousness:
            harvest_spawn_chance *= 1.5
        harvest_spawn_chance += settings.additional_sacred_grove_chance / 100
        harvest_spawn_chance += settings.additional_extra_content_chance / 100
        return harvest_spawn_chance


def get_overall_map_value(settings: Settings):
    area_iiq, pack_size = get_area_stats(settings)
    support, probabilities = get_crop_lifeforce_distribution(area_iiq, pack_size, settings)
    crop_pair_value = get_crop_pair_value(support, probabilities, settings)
    sacred_grove_value = get_sacred_grove_value(crop_pair_value, settings)
    average_harvest_value = get_harvest_spawn_chance(settings) * sacred_grove_value
    return average_harvest_value
