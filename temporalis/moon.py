from datetime import timedelta
from astral import moon
from temporalis.time import in_utc

moon_phase_names = {'en':
                        ('New moon',
                         'Waxing crescent',
                         'First quarter',
                         'Waxing gibbous',
                         'Full moon',
                         'Waning gibbous',
                         'Last quarter',
                         'Waning crescent'),
                    'nl':
                        ('Nieuwe maan',
                         'Wassende, sikkelvormige maan',
                         'Eerste kwartier',
                         'Wassende,vooruitspringende maan',
                         'Volle maan',
                         'Krimpende, vooruitspringende maan',
                         'Laatste kwartier',
                         'Krimpende, sikkelvormige maan'),
                    'de':
                        ('Neumond',
                         'Zunehmender Sichelmond',
                         'Erstes Viertel',
                         'Zunehmender Mond',
                         'Vollmond',
                         'Abnehmender Mond',
                         'Letztes Viertel',
                         'Abnehmender Sichelmond'),
                    'fr':
                        ('Nouvelle lune',
                         'Premier croissant',
                         'Premier quartier',
                         'Lune gibbeuse croissante',
                         'Pleine lune',
                         'Lune gibbeuse décroissante',
                         'Dernier quartier',
                         'Dernier croissant'),
                    'es':
                        ('Luna nueva',
                         'Luna creciente',
                         'Cuarto creciente',
                         'Luna creciente gibosa',
                         'Luna llena',
                         'Luna menguante gibosa',
                         'Cuarto menguante',
                         'Luna menguante'),
                    'pt':
                        ('Lua nova',
                         'Lua crescente',
                         'Quarto crescente',
                         'Lua crescente gibosa',
                         'Lua cheia',
                         'Lua minguante gibosa',
                         'Quarto minguante',
                         'Lua minguante'),
                    'it':
                        ('Luna nuova',
                         'Luna crescente',
                         'Primo quarto',
                         'Gibbosa crescente',
                         'Luna piena',
                         'Gibbosa calante',
                         'Ultimo quarto',
                         'Luna calante'),
                    'af':
                        ('Donkermaan',
                         'Groeiende sekelmaan',
                         'Eerste kwartier',
                         'Groeiende bolmaan',
                         'Volmaan',
                         'Afnemende bolmaan',
                         'Laaste kwartier',
                         'Afnemende sekelmaan'),
                    }
moon_phase_symbols = ('🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘')


def moon_code_to_name(code, lang='en'):
    return moon_phase_names[lang][code]


def moon_code_to_symbol(code):
    return moon_phase_symbols[code]


def moon_phase_to_inaccurate_code(phase):
    phase = int(phase)
    if phase == 0:
        return 0
    elif 0 < phase < 7:
        return 1
    elif phase == 7:
        return 2
    elif 7 < phase < 14:
        return 3
    elif phase == 14:
        return 4
    elif 14 < phase < 21:
        return 5
    elif phase == 21:
        return 6
    else:
        return 7


def get_moon_phase(date):
    date = in_utc(date)
    phase_today = moon.phase(date=date)
    code_today = moon_phase_to_inaccurate_code(phase_today)

    if code_today % 2 == 0:
        phase_yesterday = moon.phase(date=date - timedelta(days=1))
        code_yesterday = moon_phase_to_inaccurate_code(phase_yesterday)

        if code_today == code_yesterday:
            return phase_today, code_today + 1

    return phase_today, code_today
