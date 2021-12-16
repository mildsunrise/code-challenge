#!/usr/bin/env python3

import datetime
import re

def main():
    for i in range(int(input())):
        date, lang = input().split(':')
        ans = process_case(date, lang)
        print(f'Case #{i+1}: {ans}')

def parse_date_raw(date: str):
    if m := re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', date):
        return m.groups()
    if m := re.fullmatch(r'(\d{2})-(\d{2})-(\d{4})', date):
        return m.groups()[::-1]

def parse_date(date: str):
    if groups := parse_date_raw(date):
        try:
            return datetime.date(*map(int, groups))
        except ValueError:
            pass # range error, including things like February 30th

def process_case(date: str, lang: str):
    if not (date := parse_date(date)):
        return 'INVALID_DATE'
    lang = LANG_TO_ISO_639_1.get(lang, lang).lower()
    if not (language_data := LANGUAGE_DATA.get(lang)):
        return 'INVALID_LANGUAGE'
    return language_data[DAY_IDS[date.weekday()]].lower()

# standards exist for a reason...
LANG_TO_ISO_639_1 = {
    'CZ': 'CS',
    'DK': 'DA',
    'GR': 'EL',
    'SE': 'SV',
    'SI': 'SL',
}

# extracted right away from CLDR because I don't trust libc
# nor the user having all the requested locales installed
# (v40, generic calendar, stand-alone, wide)
DAY_IDS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
LANGUAGE_DATA = {
    "ca": {
        "sun": "diumenge",
        "mon": "dilluns",
        "tue": "dimarts",
        "wed": "dimecres",
        "thu": "dijous",
        "fri": "divendres",
        "sat": "dissabte"
    },
    "cs": {
        "sun": "neděle",
        "mon": "pondělí",
        "tue": "úterý",
        "wed": "středa",
        "thu": "čtvrtek",
        "fri": "pátek",
        "sat": "sobota"
    },
    "de": {
        "sun": "Sonntag",
        "mon": "Montag",
        "tue": "Dienstag",
        "wed": "Mittwoch",
        "thu": "Donnerstag",
        "fri": "Freitag",
        "sat": "Samstag"
    },
    "da": {
        "sun": "søndag",
        "mon": "mandag",
        "tue": "tirsdag",
        "wed": "onsdag",
        "thu": "torsdag",
        "fri": "fredag",
        "sat": "lørdag"
    },
    "en": {
        "sun": "Sunday",
        "mon": "Monday",
        "tue": "Tuesday",
        "wed": "Wednesday",
        "thu": "Thursday",
        "fri": "Friday",
        "sat": "Saturday"
    },
    "es": {
        "sun": "domingo",
        "mon": "lunes",
        "tue": "martes",
        "wed": "miércoles",
        "thu": "jueves",
        "fri": "viernes",
        "sat": "sábado"
    },
    "fi": {
        "sun": "sunnuntai",
        "mon": "maanantai",
        "tue": "tiistai",
        "wed": "keskiviikko",
        "thu": "torstai",
        "fri": "perjantai",
        "sat": "lauantai"
    },
    "fr": {
        "sun": "dimanche",
        "mon": "lundi",
        "tue": "mardi",
        "wed": "mercredi",
        "thu": "jeudi",
        "fri": "vendredi",
        "sat": "samedi"
    },
    "is": {
        "sun": "sunnudagur",
        "mon": "mánudagur",
        "tue": "þriðjudagur",
        "wed": "miðvikudagur",
        "thu": "fimmtudagur",
        "fri": "föstudagur",
        "sat": "laugardagur"
    },
    "el": {
        "sun": "Κυριακή",
        "mon": "Δευτέρα",
        "tue": "Τρίτη",
        "wed": "Τετάρτη",
        "thu": "Πέμπτη",
        "fri": "Παρασκευή",
        "sat": "Σάββατο"
    },
    "hu": {
        "sun": "vasárnap",
        "mon": "hétfő",
        "tue": "kedd",
        "wed": "szerda",
        "thu": "csütörtök",
        "fri": "péntek",
        "sat": "szombat"
    },
    "it": {
        "sun": "domenica",
        "mon": "lunedì",
        "tue": "martedì",
        "wed": "mercoledì",
        "thu": "giovedì",
        "fri": "venerdì",
        "sat": "sabato"
    },
    "nl": {
        "sun": "zondag",
        "mon": "maandag",
        "tue": "dinsdag",
        "wed": "woensdag",
        "thu": "donderdag",
        "fri": "vrijdag",
        "sat": "zaterdag"
    },
    "vi": {
        "sun": "Chủ Nhật",
        "mon": "Thứ Hai",
        "tue": "Thứ Ba",
        "wed": "Thứ Tư",
        "thu": "Thứ Năm",
        "fri": "Thứ Sáu",
        "sat": "Thứ Bảy"
    },
    "pl": {
        "sun": "niedziela",
        "mon": "poniedziałek",
        "tue": "wtorek",
        "wed": "środa",
        "thu": "czwartek",
        "fri": "piątek",
        "sat": "sobota"
    },
    "ro": {
        "sun": "duminică",
        "mon": "luni",
        "tue": "marți",
        "wed": "miercuri",
        "thu": "joi",
        "fri": "vineri",
        "sat": "sâmbătă"
    },
    "ru": {
        "sun": "воскресенье",
        "mon": "понедельник",
        "tue": "вторник",
        "wed": "среда",
        "thu": "четверг",
        "fri": "пятница",
        "sat": "суббота"
    },
    "sv": {
        "sun": "söndag",
        "mon": "måndag",
        "tue": "tisdag",
        "wed": "onsdag",
        "thu": "torsdag",
        "fri": "fredag",
        "sat": "lördag"
    },
    "sl": {
        "sun": "nedelja",
        "mon": "ponedeljek",
        "tue": "torek",
        "wed": "sreda",
        "thu": "četrtek",
        "fri": "petek",
        "sat": "sobota"
    },
    "sk": {
        "sun": "nedeľa",
        "mon": "pondelok",
        "tue": "utorok",
        "wed": "streda",
        "thu": "štvrtok",
        "fri": "piatok",
        "sat": "sobota"
    }
}

assert all(all(day in days for day in DAY_IDS) for days in LANGUAGE_DATA.values())

# for some reason, you deviated from the CLDR in this particular day
# and used a (apparently) less frequent dialectal variant
LANGUAGE_DATA['ro']['tue'] = 'marţi'

if __name__ == '__main__': main()
