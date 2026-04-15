// TEST: rosetta_holidays_related_to_easter
// DESCRIPTION: Rosetta Code - Holidays related to Easter (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Holidays_related_to_Easter#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Christian holidays, related to Easter, for each centennial from 400 to 2100 CE:
// STDOUT:  400 Easter: Sun  2 Apr, Ascension: Thu 11 May, Pentecost: Sun 21 May, Trinity: Sun 28 May, Corpus: Thu  1 Jun
// STDOUT:  500 Easter: Sun  4 Apr, Ascension: Thu 13 May, Pentecost: Sun 23 May, Trinity: Sun 30 May, Corpus: Thu  3 Jun
// STDOUT:  600 Easter: Sun 13 Apr, Ascension: Thu 22 May, Pentecost: Sun  1 Jun, Trinity: Sun  8 Jun, Corpus: Thu 12 Jun
// STDOUT:  700 Easter: Sun 15 Apr, Ascension: Thu 24 May, Pentecost: Sun  3 Jun, Trinity: Sun 10 Jun, Corpus: Thu 14 Jun
// STDOUT:  800 Easter: Sun 23 Apr, Ascension: Thu  1 Jun, Pentecost: Sun 11 Jun, Trinity: Sun 18 Jun, Corpus: Thu 22 Jun
// STDOUT:  900 Easter: Sun 28 Mar, Ascension: Thu  6 May, Pentecost: Sun 16 May, Trinity: Sun 23 May, Corpus: Thu 27 May
// STDOUT: 1000 Easter: Sun 30 Mar, Ascension: Thu  8 May, Pentecost: Sun 18 May, Trinity: Sun 25 May, Corpus: Thu 29 May
// STDOUT: 1100 Easter: Sun  8 Apr, Ascension: Thu 17 May, Pentecost: Sun 27 May, Trinity: Sun  3 Jun, Corpus: Thu  7 Jun
// STDOUT: 1200 Easter: Sun  9 Apr, Ascension: Thu 18 May, Pentecost: Sun 28 May, Trinity: Sun  4 Jun, Corpus: Thu  8 Jun
// STDOUT: 1300 Easter: Sun 18 Apr, Ascension: Thu 27 May, Pentecost: Sun  6 Jun, Trinity: Sun 13 Jun, Corpus: Thu 17 Jun
// STDOUT: 1400 Easter: Sun 20 Apr, Ascension: Thu 29 May, Pentecost: Sun  8 Jun, Trinity: Sun 15 Jun, Corpus: Thu 19 Jun
// STDOUT: 1500 Easter: Sun  1 Apr, Ascension: Thu 10 May, Pentecost: Sun 20 May, Trinity: Sun 27 May, Corpus: Thu 31 May
// STDOUT: 1600 Easter: Sun  2 Apr, Ascension: Thu 11 May, Pentecost: Sun 21 May, Trinity: Sun 28 May, Corpus: Thu  1 Jun
// STDOUT: 1700 Easter: Sun 11 Apr, Ascension: Thu 20 May, Pentecost: Sun 30 May, Trinity: Sun  6 Jun, Corpus: Thu 10 Jun
// STDOUT: 1800 Easter: Sun 13 Apr, Ascension: Thu 22 May, Pentecost: Sun  1 Jun, Trinity: Sun  8 Jun, Corpus: Thu 12 Jun
// STDOUT: 1900 Easter: Sun 15 Apr, Ascension: Thu 24 May, Pentecost: Sun  3 Jun, Trinity: Sun 10 Jun, Corpus: Thu 14 Jun
// STDOUT: 2000 Easter: Sun 23 Apr, Ascension: Thu  1 Jun, Pentecost: Sun 11 Jun, Trinity: Sun 18 Jun, Corpus: Thu 22 Jun
// STDOUT: 2100 Easter: Sun 28 Mar, Ascension: Thu  6 May, Pentecost: Sun 16 May, Trinity: Sun 23 May, Corpus: Thu 27 May
// STDOUT:
// STDOUT: Christian holidays, related to Easter, for years from 2010 to 2020 CE:
// STDOUT: 2010 Easter: Sun  4 Apr, Ascension: Thu 13 May, Pentecost: Sun 23 May, Trinity: Sun 30 May, Corpus: Thu  3 Jun
// STDOUT: 2011 Easter: Sun 24 Apr, Ascension: Thu  2 Jun, Pentecost: Sun 12 Jun, Trinity: Sun 19 Jun, Corpus: Thu 23 Jun
// STDOUT: 2012 Easter: Sun  8 Apr, Ascension: Thu 17 May, Pentecost: Sun 27 May, Trinity: Sun  3 Jun, Corpus: Thu  7 Jun
// STDOUT: 2013 Easter: Sun 31 Mar, Ascension: Thu  9 May, Pentecost: Sun 19 May, Trinity: Sun 26 May, Corpus: Thu 30 May
// STDOUT: 2014 Easter: Sun 20 Apr, Ascension: Thu 29 May, Pentecost: Sun  8 Jun, Trinity: Sun 15 Jun, Corpus: Thu 19 Jun
// STDOUT: 2015 Easter: Sun  5 Apr, Ascension: Thu 14 May, Pentecost: Sun 24 May, Trinity: Sun 31 May, Corpus: Thu  4 Jun
// STDOUT: 2016 Easter: Sun 27 Mar, Ascension: Thu  5 May, Pentecost: Sun 15 May, Trinity: Sun 22 May, Corpus: Thu 26 May
// STDOUT: 2017 Easter: Sun 16 Apr, Ascension: Thu 25 May, Pentecost: Sun  4 Jun, Trinity: Sun 11 Jun, Corpus: Thu 15 Jun
// STDOUT: 2018 Easter: Sun  1 Apr, Ascension: Thu 10 May, Pentecost: Sun 20 May, Trinity: Sun 27 May, Corpus: Thu 31 May
// STDOUT: 2019 Easter: Sun 21 Apr, Ascension: Thu 30 May, Pentecost: Sun  9 Jun, Trinity: Sun 16 Jun, Corpus: Thu 20 Jun
// STDOUT: 2020 Easter: Sun 12 Apr, Ascension: Thu 21 May, Pentecost: Sun 31 May, Trinity: Sun  7 Jun, Corpus: Thu 11 Jun

#include <stdio.h>

typedef int year_t, month_t, week_t, day_t;

typedef struct{
  year_t year; /* day_t year_day, */
  month_t month;  day_t month_day;/*
  week_t week, */ day_t week_day; } date_t;

const char *mon_fmt[] =      {0, "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
const char *week_day_fmt[] = {0, "Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"};

day_t month_days(year_t year, month_t month)
  { day_t days[]={0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    return (month==2) ? 28 + (( year % 4 == 0 && year % 100 != 0 ) || year % 400 == 0) : days[month];
  }

day_t year_days(year_t year) /* Ignore 1752 CE for the moment */
  { return (month_days(year, 2) == 28) ? 365 : 366; }

month_t year_months = 12;
week_t week_days = 7; /* France 1793 to 1805 had 10 day weeks! */

date_t plusab(date_t *date, day_t days)
    { /* todo: eliminate loops, handle year <== 1752 */
    /* Normalize the days to be less then 1 year */
       while(days < 0){
         date->year -= 1;
         days += year_days(date->year);
       };
       while(days > year_days(date->year)){
         days -= year_days(date->year);
         date->year += 1;
       };
       date->month_day += days;
    /* Normalize the days to be the same month */
       while(date->month_day > month_days(date->year, date->month)){
          date->month_day -= month_days(date->year, date->month);
          date->month += 1;
          if(date->month > year_months){
             date->month -= year_months;
             date->year += 1;
          }
       }
       date->week_day = week_day(*date);
       return *date;
    }

date_t easter (year_t year)
   {
      /*
         Easter date algorithm from J.M. Oudin (1940), reprinted in:
         P.K. Seidelmann ed., "Explanatory Supplement to the Astronomical
         Almanac" [1992] (Chapter 12, "Calendars", by L.E. Doggett)
      */
      date_t date; date.year = year;
      int c = year / 100, n = year % 19; /* 19 years: Metonic cycle */
      int i = (c - c / 4 - (c - (c - 17) / 25) / 3 + 19 * n + 15) % 30;
      i -= (i / 28) * (1 - (i / 28) * (29 / (i + 1)) * ((21 - n) / 11));
      int l = i - (year + year / 4 + i + 2 - c + c / 4) % 7;
      date.month = 3 + (l + 40) / 44;
      date.month_day = l + 28 - 31 * (date.month / 4);
      date.week_day = week_day(date);
      return date;
   }

day_t week_day (date_t date)
   /* Zeller’s Congruence algorithm from 1887. */
   {
      int year = date.year, month = date.month, month_day = date.month_day, c;
      if(month <= 2){month += 12; year -= 1;}
      c = year / 100;
      year %= 100;
      return 1 + ((month_day + ((month + 1) * 26) / 10
         + year + year / 4 + c / 4 - 2 * c) % 7 + 7) % 7;
   }

#define wdmdm_fmt "%s %2d %s"

typedef struct{date_t easter, ascension, pentecost, trinity, corpus_christi;}easter_related_t; 

easter_related_t easter_related_init (year_t year)
{
   date_t date;
   easter_related_t holidays;
/* Easter date, always a Sunday. */
   holidays.easter = date = easter(year);
/* Ascension day is 39 days after Easter.*/
   holidays.ascension = plusab(&date, 39);
/* Pentecost is 10 days after Ascension day.*/
   holidays.pentecost = plusab(&date, 10);
/* Trinity is 7 days after Pentecost.*/
   holidays.trinity = plusab(&date, 7);
/* Corpus Christi is 4 days after Trinity.*/
   holidays.corpus_christi = plusab(&date, 4);
   return holidays;
}

/* note: y10k bug here... :-) */
#define easter_related_fmt "%4d Easter: "wdmdm_fmt", Ascension: "wdmdm_fmt\
    ", Pentecost: "wdmdm_fmt", Trinity: "wdmdm_fmt", Corpus: "wdmdm_fmt"\n"

void easter_related_print(year_t year)
{
  easter_related_t holidays = easter_related_init(year);
#define wdmdm(date) week_day_fmt[date.week_day], date.month_day, mon_fmt[date.month]
  printf(easter_related_fmt, year,
    wdmdm(holidays.easter),  wdmdm(holidays.ascension), wdmdm(holidays.pentecost),
    wdmdm(holidays.trinity), wdmdm(holidays.corpus_christi));
}

int main(){
  year_t year;

  printf ("Christian holidays, related to Easter, for each centennial from 400 to 2100 CE:\n");
  for(year=400; year<=2100; year+=100){ easter_related_print(year); }

  printf ("\nChristian holidays, related to Easter, for years from 2010 to 2020 CE:\n");
  for(year=2010; year<=2020; year++){ easter_related_print(year); }
  return 0;
}