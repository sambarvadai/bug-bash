def is_leap_year(year):
    """
    Return True if year is a leap year.
    Rules:
      - Divisible by 4 AND not divisible by 100  -->  leap year
      - OR divisible by 400                       -->  also a leap year
    """
    return (year % 4 == 0 and year % 100 != 0) and (year % 400 == 0)
