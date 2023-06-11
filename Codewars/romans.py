class RomanNumerals:
    def to_roman(val):
        guide = [
            ("M", 1000),
            ("D", 500),
            ("C", 100),
            ("L", 50),
            ("X", 10),
            ("V", 5),
            ("I", 1),
        ]
        changes = [
            ("DCCCC", "CM"),
            ("CCCC", "CD"),
            ("LXXXX", "XC"),
            ("XXXX", "XL"),
            ("VIIII", "IX"),
            ("IIII", "IV"),
        ]
        roman = ""
        for number in guide:
            while val - number[1] >= 0:
                val -= number[1]
                roman += number[0]
        for change in changes:
            if change[0] in roman:
                roman = roman.replace(change[0], change[1])
        return roman

    def from_roman(roman_num):
        guide = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}
        changes = [
            ("DCCCC", "CM"),
            ("CCCC", "CD"),
            ("LXXXX", "XC"),
            ("XXXX", "XL"),
            ("VIIII", "IX"),
            ("IIII", "IV"),
        ]

        for change in changes:
            if change[1] in roman_num:
                roman_num = roman_num.replace(change[1], change[0])
        arabic = 0
        for letter in roman_num:
            arabic += guide[letter]
        return arabic


print(RomanNumerals.to_roman(2309))
print(RomanNumerals.from_roman("MMCXLVII"))
