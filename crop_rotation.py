from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from functools import total_ordering
import random

import numpy as np

from harvest import Settings, SeedTier, has_sextant


@total_ordering
class Color(Enum):
    YELLOW = 1
    PURPLE = 2
    BLUE = 3
    NONE = 0

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        else:
            raise NotImplementedError()


@dataclass
class CropPlot:
    color: Color
    t2_seeds: int
    t3_seeds: int
    t4_seeds: int

    def __repr__(self):
        return "{} {} {} {} {}".format(
            self.color,
            23 - (self.t2_seeds + self.t3_seeds + self.t4_seeds),
            self.t2_seeds,
            self.t3_seeds,
            self.t4_seeds)


def upgrade_crop(crop: CropPlot, settings: Settings) -> CropPlot:
    old_t1 = 23 - crop.t2_seeds - crop.t3_seeds - crop.t4_seeds
    upgraded_t1 = np.random.binomial(old_t1, settings.t1_crop_rotation_upgrade_chance)
    upgraded_t2 = np.random.binomial(crop.t2_seeds, settings.t2_crop_rotation_upgrade_chance)
    upgraded_t3 = np.random.binomial(crop.t3_seeds, settings.t3_crop_rotation_upgrade_chance)
    new_t2 = crop.t2_seeds + upgraded_t1 - upgraded_t2
    new_t3 = crop.t3_seeds + upgraded_t2 - upgraded_t3
    new_t4 = crop.t4_seeds + upgraded_t3
    return CropPlot(
        color=crop.color,
        t2_seeds=new_t2,
        t3_seeds=new_t3,
        t4_seeds=new_t4
    )


class CropPair:

    def __init__(self, plot_1: CropPlot, plot_2: Optional[CropPlot]):
        self.plot_1 = plot_1
        self.plot_2 = plot_2

    def __getitem__(self, index: int):
        if index < 0 or index > 2 or index == 1 and self.plot_2 is None:
            raise IndexError("Index {} out of range for crop pair \n{}".format(index, self))
        if index == 0:
            return self.plot_1
        else:
            return self.plot_2

    def __len__(self):
        if self.plot_2 is None:
            return 1
        else:
            return 2

    def __repr__(self):
        output = str(self.plot_1)
        if self.plot_2 is not None:
            output += ", " + str(self.plot_2)
        return output

    def sort(self) -> None:
        if self.plot_2 is not None and self.plot_1.color < self.plot_2.color:
            self.plot_1, self.plot_2 = self.plot_2, self.plot_1

    def get_color_score(self):
        """
        For a sorted plot, converts the pair of colors into a number from 1 to 9 for sorting pairs of plots
        :return: The color score of the plot from 1 to 9
        """
        if self.plot_2 is None:
            return self.plot_1.color.value
        elif self.plot_1.color == Color.BLUE:
            return self.plot_2.color.value + 6
        elif self.plot_1.color == Color.PURPLE:
            return self.plot_2.color.value + 4
        else:
            return 4

    @staticmethod
    def _roll_crop_colors(settings: Settings) -> List[Color]:
        blue_weight = 100 - settings.reduced_blue_chance
        purple_weight = 100 - settings.reduced_purple_chance
        yellow_weight = 100 - settings.reduced_yellow_chance
        total_weight = blue_weight + purple_weight + yellow_weight
        blue_chance = blue_weight / total_weight
        purple_chance = purple_weight / total_weight
        yellow_chance = yellow_weight / total_weight
        colors = []
        for i in range(2):
            color_roll = random.random()
            if color_roll < blue_chance:
                colors.append(Color.BLUE)
            elif color_roll < blue_chance + purple_chance:
                colors.append(Color.PURPLE)
            else:
                colors.append(Color.YELLOW)
        return colors

    @classmethod
    def create_random_crop_pair(cls, settings: Settings) -> CropPair:
        if has_sextant(settings):
            if settings.blue_sextant:
                sextant_color = Color.BLUE
            elif settings.purple_sextant:
                sextant_color = Color.PURPLE
            else:
                sextant_color = Color.YELLOW
            if settings.sextant_reroll_implementation:
                colors = CropPair._roll_crop_colors(Settings)
                while colors[0] != sextant_color and colors[1] != sextant_color:
                    colors = CropPair._roll_crop_colors(Settings)
            else:
                colors = CropPair._roll_crop_colors(Settings)
                # 50% chance for first crop to be replaced with sextant color, 50% chance for second crop
                if random.random() < 0.5:
                    colors[0] = sextant_color
                else:
                    colors[1] = sextant_color
        else:
            colors = CropPair._roll_crop_colors(settings)
        return cls(
            CropPlot(colors[0], 0, 0, 0),
            CropPlot(colors[1], 0, 0, 0)
        )


class HarvestLayout:

    def __init__(self, pairs: List[CropPair], settings: Settings):
        self.harvests = pairs
        self.settings = settings

    def sort(self) -> None:
        for i in range(len(self.harvests)):
            self.harvests[i].sort()
        self.harvests = sorted(self.harvests, key=lambda x: x.get_color_score(), reverse=True)

    def harvest(self, harvest_index: int, crop_index: int) -> HarvestLayout:
        """
        Harvest the chosen crop, upgrading other plots randomly
        :param harvest_index: The index of the plot to harvest
        :param crop_index: The index of the crop to harvest from the selected plot (0 or 1)
        :return: A new harvest layout with unchosen crop colors randomly upgraded
        """
        if harvest_index < 0 or harvest_index >= len(self.harvests):
            raise ValueError("Invalid harvest index {} for crop layout \n{}".format(harvest_index, self))
        if crop_index < 0 or crop_index >= len(self.harvests[harvest_index]):
            raise ValueError("invalid crop index {} for harvest {} in crop layout \n{}".format(
                crop_index, harvest_index, self))
        new_harvests = []
        chosen_color = self.harvests[harvest_index][crop_index].color
        unchosen_color = Color.NONE
        insert_point = -1
        for i, harvest in enumerate(self.harvests):
            if i == harvest_index:
                if harvest.plot_2 is not None:
                    unchosen_color = harvest[1 - crop_index].color
                continue
            new_pair = []
            if harvest.plot_1.color == chosen_color:
                new_pair.append(harvest.plot_1)
            else:
                new_pair.append(upgrade_crop(harvest.plot_1, self.settings))
            if harvest.plot_2 is None:
                if harvest.plot_1.color > unchosen_color:
                    insert_point = i
                new_pair.append(None)
            else:
                if harvest.plot_2.color == chosen_color:
                    new_pair.append(harvest.plot_2)
                else:
                    new_pair.append(upgrade_crop(harvest.plot_2, self.settings))
            new_harvests.append(CropPair(*new_pair))

        if insert_point == -1:
            insert_point = len(new_harvests)
        if self.settings.heart_of_the_grove and self.harvests[harvest_index].plot_2 is not None and random.random() < 0.1:
            unwilted_plot = self.harvests[harvest_index][1 - crop_index]
            if unwilted_plot.color == chosen_color:
                new_harvests.insert(insert_point, CropPair(unwilted_plot, None))
            else:
                upgraded_unwilted_plot = upgrade_crop(unwilted_plot, settings)
                new_harvests.insert(insert_point, CropPair(upgraded_unwilted_plot, None))
        return HarvestLayout(new_harvests, self.settings)

    def __repr__(self):
        harvest_strings = []
        for crop in self.harvests:
            harvest_strings.append(str(crop))
        return "\n".join(harvest_strings)

    @classmethod
    def create_random_harvest(cls, settings: Settings):
        num_crops = 3
        if random.random() < settings.base_four_harvest_chance:
            num_crops += 1
        if settings.bumper_crop and random.random() < 0.5:
            num_crops += 1
        harvests = []
        for i in range(num_crops):
            harvests.append(CropPair.create_random_crop_pair(settings))
        return cls(harvests, settings)


class CropRotationTable:

    def __init__(self, num_pairs: int, settings: Settings):
        values = np.zeros((num_pairs, 15, 2, 23, 15, 3))
        actions = np.zeros_like(values)

    def get_value(self):
        pass


if __name__ == "__main__":
    settings = Settings()
    random_harvest = HarvestLayout.create_random_harvest(settings)
    random_harvest.sort()
    while len(random_harvest.harvests) > 0:
        print(random_harvest)
        print("")
        random_harvest = random_harvest.harvest(0, 0)


