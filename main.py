import copy
import dataclasses

import harvest
from harvest import Settings, get_overall_map_value
import matplotlib.pyplot as plt
import numpy as np

BASE_NO_ATLAS_SETTINGS = Settings(
    bumper_crop=False,
    bountiful_harvest=False,
    heart_of_the_grove=False,
    doubling_season=False,
    crop_rotation=False,
    increased_t3_crop_chance=0,
    increased_quantity_of_lifeforce=0,
    duplicated_monsters_chance=0,
    additional_sacred_grove_chance=0,
    additional_extra_content_chance=0,
    reduced_blue_chance=0,
    reduced_purple_chance=0,
    reduced_yellow_chance=0,
    increased_quantity=0,
    increased_map_modifier_effect=0,
    stream_of_consciousness=False
)

REGULAR_ATLAS_SETTINGS = Settings(
    reduced_blue_chance=45,
    reduced_purple_chance=45,
    reduced_yellow_chance=0,
    bumper_crop=True,
    bountiful_harvest=True,
    heart_of_the_grove=True,
    doubling_season=True,
    increased_t3_crop_chance=30,
    increased_quantity_of_lifeforce=18,
    duplicated_monsters_chance=6,
    additional_sacred_grove_chance=45,
    additional_extra_content_chance=14,
    increased_quantity=15,
    increased_map_modifier_effect=30,
    increased_pack_size=0,
    stream_of_consciousness=True
)

GRAND_DESIGN_ATLAS_SETTINGS = Settings(
    bumper_crop=True,
    bountiful_harvest=True,
    heart_of_the_grove=True,
    doubling_season=True,
    increased_t3_crop_chance=0,
    increased_quantity_of_lifeforce=0,
    duplicated_monsters_chance=0,
    additional_sacred_grove_chance=15,
    additional_extra_content_chance=8,
    reduced_blue_chance=25,
    reduced_purple_chance=25,
    reduced_yellow_chance=0,
    increased_quantity=0,
    increased_map_modifier_effect=0,
    increased_pack_size=40,
    stream_of_consciousness=True
)

WANDERING_PATH_ATLAS_SETTINGS = Settings(
    bumper_crop=False,
    bountiful_harvest=False,
    heart_of_the_grove=False,
    doubling_season=False,
    increased_t3_crop_chance=60,
    increased_quantity_of_lifeforce=36,
    duplicated_monsters_chance=12,
    additional_sacred_grove_chance=60,
    additional_extra_content_chance=0,
    reduced_blue_chance=40,
    reduced_purple_chance=40,
    reduced_yellow_chance=0,
    increased_quantity=30,
    increased_map_modifier_effect=60,
    stream_of_consciousness=True
)


def base_comparison():
    map_quantities = list(range(0, 130, 10))
    regular_values = []
    grand_design_values = []
    wandering_path_values = []
    for map_quantity in map_quantities:
        regular_atlas_settings = copy.copy(REGULAR_ATLAS_SETTINGS)
        regular_atlas_settings.base_map_quantity = map_quantity
        # regular_atlas_settings.guaranteed_harvest_spawn = True
        # regular_atlas_settings.yellow_sextant = True
        # regular_atlas_settings.fragment_pack_size = 40
        regular_values.append(harvest.get_overall_map_value(regular_atlas_settings))
        wandering_path_settings = copy.copy(WANDERING_PATH_ATLAS_SETTINGS)
        wandering_path_settings.base_map_quantity = map_quantity
        # wandering_path_settings.guaranteed_harvest_spawn = True
        # wandering_path_settings.yellow_sextant = True
        # wandering_path_settings.fragment_pack_size = 40
        # wandering_path_settings.increased_map_modifier_effect = 0
        wandering_path_values.append(harvest.get_overall_map_value(wandering_path_settings))
        grand_design_settings = copy.copy(GRAND_DESIGN_ATLAS_SETTINGS)
        grand_design_settings.base_map_quantity = map_quantity
        # grand_design_settings.guaranteed_harvest_spawn = True
        # grand_design_settings.yellow_sextant = True
        # grand_design_settings.fragment_pack_size = 40
        grand_design_values.append(harvest.get_overall_map_value(grand_design_settings))
    plt.plot(map_quantities, regular_values, marker='x', label="Regular Tree")
    plt.plot(map_quantities, wandering_path_values, marker='o', label="Wandering Path")
    plt.plot(map_quantities, grand_design_values, marker='+', label="Grand Design")
    plt.axvline(26, 0, 70, linestyle="dotted", c='gray')
    plt.text(26, 10, "(2 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(52, 0, 70, linestyle="dotted", c='gray')
    plt.text(52, 10, "(4 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(78, 0, 70, linestyle="dotted", c='gray')
    plt.text(78, 10, "(6 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(104, 0, 70, linestyle="dotted", c='gray')
    plt.text(104, 10, "(8 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.legend(loc="best")
    plt.xlabel("Base Map Quantity")
    plt.ylabel("Expected Sacred Grove Value (Chaos)")
    # plt.title("Harvest Value Comparison (Guaranteed Sacred Grove + Yellow Sextant)")
    plt.title("Harvest Value Comparison (Alch and go, no sextants)")
    plt.show()


def t3_comparison():
    map_quantities = list(range(0, 130, 10))
    regular_values = []
    t3_values = []
    for map_quantity in map_quantities:
        regular_atlas_settings = copy.copy(GRAND_DESIGN_ATLAS_SETTINGS)
        regular_atlas_settings.base_map_quantity = map_quantity
        regular_atlas_settings.guaranteed_harvest_spawn = True
        regular_atlas_settings.purple_sextant = True
        regular_atlas_settings.fragment_pack_size = 28
        regular_values.append(harvest.get_overall_map_value(regular_atlas_settings))
        t3_settings = copy.copy(REGULAR_ATLAS_SETTINGS)
        t3_settings.base_map_quantity = map_quantity
        t3_settings.guaranteed_harvest_spawn = True
        t3_settings.purple_sextant = True
        t3_settings.fragment_pack_size = 28
        t3_settings.increased_t3_crop_chance = 0
        t3_values.append(harvest.get_overall_map_value(t3_settings))
    print(regular_values)
    print(t3_values)
    plt.plot(map_quantities, regular_values, marker='x', label="Regular Tree")
    plt.plot(map_quantities, t3_values, marker='o', label="No T3 small passives")
    plt.axvline(26, 0, 70, linestyle="dotted", c='gray')
    plt.text(26, 47, "(2 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(52, 0, 70, linestyle="dotted", c='gray')
    plt.text(52, 47, "(4 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(78, 0, 70, linestyle="dotted", c='gray')
    plt.text(78, 47, "(6 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(104, 0, 70, linestyle="dotted", c='gray')
    plt.text(104, 47, "(8 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.legend(loc="best")
    plt.xlabel("Base Map Quantity")
    plt.ylabel("Expected Sacred Grove Value (Chaos)")
    plt.title("Harvest Value Comparison (Guaranteed Sacred Grove + Purple Sextant)")
    plt.show()


def sextant_comparison():
    map_quantities = list(range(0, 130, 10))
    regular_values = []
    t3_values = []
    for map_quantity in map_quantities:
        regular_atlas_settings = copy.copy(WANDERING_PATH_ATLAS_SETTINGS)
        regular_atlas_settings.base_map_quantity = map_quantity
        regular_atlas_settings.guaranteed_harvest_spawn = True
        regular_atlas_settings.purple_sextant = True
        regular_atlas_settings.fragment_pack_size = 28
        regular_values.append(harvest.get_overall_map_value(regular_atlas_settings))
        t3_settings = copy.copy(WANDERING_PATH_ATLAS_SETTINGS)
        t3_settings.base_map_quantity = map_quantity
        t3_settings.guaranteed_harvest_spawn = True
        t3_settings.yellow_sextant = True
        t3_settings.fragment_pack_size = 28
        t3_values.append(harvest.get_overall_map_value(t3_settings))
    print(regular_values)
    print(t3_values)
    plt.plot(map_quantities, regular_values, marker='x', label="Purple Sextant")
    plt.plot(map_quantities, t3_values, marker='o', label="Yellow Sextant")
    plt.axvline(26, 0, 70, linestyle="dotted", c='gray')
    plt.text(26, 47, "(2 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(52, 0, 70, linestyle="dotted", c='gray')
    plt.text(52, 47, "(4 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(78, 0, 70, linestyle="dotted", c='gray')
    plt.text(78, 47, "(6 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.axvline(104, 0, 70, linestyle="dotted", c='gray')
    plt.text(104, 47, "(8 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.legend(loc="best")
    plt.xlabel("Base Map Quantity")
    plt.ylabel("Expected Sacred Grove Value (Chaos)")
    plt.title("Sextant Value Comparison (Wandering Path + 28% Growing Hordes)")
    plt.show()

def scarab_comparison():
    map_quantities = list(range(80, 130, 10))
    regular_values = []
    rusted_values = []
    polished_values = []
    gilded_values = []
    sacrifice_values = []
    base_settings = WANDERING_PATH_ATLAS_SETTINGS
    for map_quantity in map_quantities:
        regular_atlas_settings = copy.copy(base_settings)
        regular_atlas_settings.base_map_quantity = map_quantity
        regular_atlas_settings.guaranteed_harvest_spawn = True
        regular_atlas_settings.yellow_sextant = True
        regular_values.append(harvest.get_overall_map_value(regular_atlas_settings))
        rusted_atlas_settings = copy.copy(base_settings)
        rusted_atlas_settings.base_map_quantity = map_quantity
        rusted_atlas_settings.guaranteed_harvest_spawn = True
        rusted_atlas_settings.yellow_sextant = True
        rusted_atlas_settings.fragment_pack_size = 20
        rusted_values.append(harvest.get_overall_map_value(rusted_atlas_settings))
        polished_atlas_settings = copy.copy(base_settings)
        polished_atlas_settings.base_map_quantity = map_quantity
        polished_atlas_settings.guaranteed_harvest_spawn = True
        polished_atlas_settings.yellow_sextant = True
        polished_atlas_settings.fragment_pack_size = 28
        polished_values.append(harvest.get_overall_map_value(polished_atlas_settings))
        gilded_atlas_settings = copy.copy(base_settings)
        gilded_atlas_settings.base_map_quantity = map_quantity
        gilded_atlas_settings.guaranteed_harvest_spawn = True
        gilded_atlas_settings.yellow_sextant = True
        gilded_atlas_settings.fragment_pack_size = 40
        gilded_values.append(harvest.get_overall_map_value(gilded_atlas_settings))
        sacrifice_atlas_settings = copy.copy(base_settings)
        sacrifice_atlas_settings.base_map_quantity = map_quantity
        sacrifice_atlas_settings.guaranteed_harvest_spawn = True
        sacrifice_atlas_settings.yellow_sextant = True
        sacrifice_atlas_settings.fragment_quantity = 20
        sacrifice_values.append(harvest.get_overall_map_value(sacrifice_atlas_settings))
    plt.plot(map_quantities, regular_values, marker='x', label="No Fragments")
    plt.plot(map_quantities, rusted_values, marker='o', label="Rusted Scarabs")
    plt.plot(map_quantities, polished_values, marker='+', label="Polished Scarabs")
    plt.plot(map_quantities, gilded_values, marker='^', label="Gilded Scarabs")
    plt.plot(map_quantities, sacrifice_values, marker='v', label="Sacrifice Fragments")
    # plt.axvline(26, 0, 70, linestyle="dotted", c='gray')
    # plt.text(26, 52, "(2 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    # plt.axvline(52, 0, 70, linestyle="dotted", c='gray')
    # plt.text(52, 52, "(4 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    # plt.axvline(78, 0, 70, linestyle="dotted", c='gray')
    # plt.text(78, 52, "(6 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    # plt.axvline(104, 0, 70, linestyle="dotted", c='gray')
    # plt.text(104, 52, "(8 Mods)", horizontalalignment='center', bbox=dict(alpha=0.6, fc="white", ec="white"))
    plt.xlabel("Base Map Quantity")
    plt.ylabel("Expected Sacred Grove Value (Chaos)")
    plt.title("Growing Hordes Comparison (2 Sextants)")
    plt.legend(loc="best")
    plt.show()


if __name__ == "__main__":
    print(harvest.get_overall_map_value(dataclasses.replace(WANDERING_PATH_ATLAS_SETTINGS, fragment_pack_size=40, base_map_quantity=100, yellow_sextant=True, guaranteed_harvest_spawn=True)))
    base_comparison()
    # scarab_comparison()
    # t3_comparison()
    # sextant_comparison()
