import numpy as np

RANDOM_WORD = ['Space',
               'Earth',
               'Solar system',
               'Sun',
               'Jupiter',
               'Mars',
               'Moon',
               'Neptune',
               'gibbous', 'Mercury', 'Pluto', 'Half-moon', 'Saturn', 'Venus', 'Crescent', 'Uranus',
               'Planet', 'Asteroid belt', 'Asteroid', 'Black hole',
               'Big bang theory', 'Astronaut', 'Comet', 'Binary star', 'Astronomer', 'Astronomy',
               'elliptical orbit', 'Constellation', 'Deep space', 'Cosmonaut', 'Cosmos',
               'Dwarf planet', 'Crater', 'Dwarf', 'Star dust', 'Equinox', 'Planets',
               'Galaxy', 'Lunar', 'Meteorite', 'Meteor', 'Gravity', 'Milky Way', 'Nebula',
               'Orbit', 'Rocket', 'Solar', 'Space exploration', 'Solstice', 'Star', 'Umbra',
               'Satellite', 'Solar system', 'New moon', 'Solar wind', 'Light-year', 'Rings',
               'Observatory', 'Universe', 'Zodiac', 'Space station', 'Sun', 'Starlight', 'Telescope',
               ]


def get_random_word():
    return np.random.choice(RANDOM_WORD)

