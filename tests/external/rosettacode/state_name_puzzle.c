// The output order depends on qsort's tie-breaking behaviour, which is
// unspecified by the C standard. macOS ARM64 qsort and Linux x86-64 qsort use
// different algorithms and produce different orderings for equal-ranked
// entries, resulting in a different (but equally valid) solution sequence.
// TEST: rosetta_state_name_puzzle
// DESCRIPTION: Rosetta Code - State name puzzle (qsort, string manipulation, SIGSEGV)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/State_name_puzzle#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Kory New + New Kory => New York + Wen Kory
// STDOUT: Kory New + New Kory => New York + York New
// STDOUT: Kory New + New Kory => Wen Kory + York New
// STDOUT: Kory New + New York => New Kory + Wen Kory
// STDOUT: Kory New + New York => New Kory + York New
// STDOUT: Kory New + New York => Wen Kory + York New
// STDOUT: Kory New + Wen Kory => New Kory + New York
// STDOUT: Kory New + Wen Kory => New Kory + York New
// STDOUT: Kory New + Wen Kory => New York + York New
// STDOUT: Kory New + York New => New Kory + New York
// STDOUT: Kory New + York New => New Kory + Wen Kory
// STDOUT: Kory New + York New => New York + Wen Kory
// STDOUT: New Kory + New York => Wen Kory + York New
// STDOUT: New Kory + Wen Kory => New York + York New
// STDOUT: New Kory + York New => New York + Wen Kory
// STDOUT: North Carolina + South Dakota => North Dakota + South Carolina
// EXPECTED_STDOUT_ARM64:
// STDOUT_ARM64: Missouri + Wen Kory => Kory New + Missouri
// STDOUT_ARM64: Missouri + New Kory => Kory New + Missouri
// STDOUT_ARM64: Mississippi + York New => Kory New + Mississippi
// STDOUT_ARM64: Mississippi + New York => Kory New + Mississippi
// STDOUT_ARM64: Mississippi + New Kory => Kory New + Mississippi
// STDOUT_ARM64: Ohio + York New => Kory New + Ohio
// STDOUT_ARM64: Ohio + York New => New Kory + Ohio
// STDOUT_ARM64: Ohio + Wen Kory => Kory New + Ohio
// STDOUT_ARM64: Ohio + Wen Kory => New Kory + Ohio
// STDOUT_ARM64: Vermont + Wen Kory => New Kory + Vermont
// STDOUT_ARM64: Vermont + Wen Kory => Kory New + Vermont
// STDOUT_ARM64: Vermont + York New => New Kory + Vermont
// STDOUT_ARM64: Vermont + York New => Kory New + Vermont
// STDOUT_ARM64: New Kory + New York => Kory New + New Kory
// STDOUT_ARM64: New Kory + New York => Kory New + Wen Kory
// STDOUT_ARM64: New Kory + New York => Wen Kory + York New
// STDOUT_ARM64: New Kory + New York => Kory New + York New
// STDOUT_ARM64: Kory New + New York => Wen Kory + York New
// STDOUT_ARM64: Kory New + New York => New Kory + Wen Kory
// STDOUT_ARM64: Kory New + New York => New Kory + York New
// STDOUT_ARM64: Kory New + New Kory => Wen Kory + York New
// STDOUT_ARM64: Kory New + New Kory => New York + Wen Kory
// STDOUT_ARM64: Kory New + New Kory => New York + York New
// STDOUT_ARM64: Kory New + Wen Kory => New Kory + York New
// STDOUT_ARM64: Kory New + Wen Kory => New York + York New
// STDOUT_ARM64: Wen Kory + York New => New Kory + Wen Kory
// STDOUT_ARM64: Wen Kory + York New => New York + Wen Kory
// STDOUT_ARM64: New Kory + Wen Kory => Kory New + York New
// STDOUT_ARM64: New Kory + Wen Kory => New York + York New
// STDOUT_ARM64: New Kory + York New => New York + Wen Kory
// STDOUT_ARM64: Kory New + York New => New York + Wen Kory
// STDOUT_ARM64: Oregon + Wen Kory => New York + Oregon
// STDOUT_ARM64: Oregon + Wen Kory => New Kory + Oregon
// STDOUT_ARM64: Oregon + York New => New York + Oregon
// STDOUT_ARM64: Oregon + York New => New Kory + Oregon
// STDOUT_ARM64: New Jersey + York New => Kory New + New Jersey
// STDOUT_ARM64: New Jersey + New Kory => Kory New + New Jersey
// STDOUT_ARM64: Tennessee + York New => Kory New + Tennessee
// STDOUT_ARM64: Tennessee + Wen Kory => Kory New + Tennessee
// STDOUT_ARM64: Wisconsin + York New => Wen Kory + Wisconsin
// STDOUT_ARM64: New Mexico + York New => Kory New + New Mexico
// STDOUT_ARM64: New Mexico + New York => Kory New + New Mexico
// STDOUT_ARM64: New Mexico + Wen Kory => Kory New + New Mexico
// STDOUT_ARM64: Utah + York New => New Kory + Utah
// STDOUT_ARM64: Utah + York New => Kory New + Utah
// STDOUT_ARM64: Virginia + York New => New Kory + Virginia
// STDOUT_ARM64: Virginia + York New => Kory New + Virginia
// STDOUT_ARM64: Virginia + York New => New York + Virginia
// STDOUT_ARM64: Virginia + Wen Kory => New Kory + Virginia
// STDOUT_ARM64: Virginia + Wen Kory => Kory New + Virginia
// STDOUT_ARM64: Virginia + Wen Kory => New York + Virginia
// STDOUT_ARM64: Washington + York New => Kory New + Washington
// STDOUT_ARM64: Washington + York New => New York + Washington
// STDOUT_ARM64: Washington + Wen Kory => Kory New + Washington
// STDOUT_ARM64: Washington + Wen Kory => New York + Washington
// STDOUT_ARM64: Texas + York New => New Kory + Texas
// STDOUT_ARM64: Texas + York New => New York + Texas
// STDOUT_ARM64: Maine + Wen Kory => Kory New + Maine
// STDOUT_ARM64: Maine + New York => Kory New + Maine
// STDOUT_ARM64: Minnesota + New Kory => Kory New + Minnesota
// STDOUT_ARM64: Minnesota + Wen Kory => Kory New + Minnesota
// STDOUT_ARM64: Minnesota + York New => Kory New + Minnesota
// STDOUT_ARM64: West Virginia + York New => New York + West Virginia
// STDOUT_ARM64: West Virginia + York New => Kory New + West Virginia
// STDOUT_ARM64: New Hampshire + Wen Kory => Kory New + New Hampshire
// STDOUT_ARM64: New Hampshire + New York => Kory New + New Hampshire
// STDOUT_ARM64: New Hampshire + New Kory => Kory New + New Hampshire
// STDOUT_ARM64: New Hampshire + York New => Kory New + New Hampshire
// STDOUT_ARM64: Rhode Island + York New => New Kory + Rhode Island
// STDOUT_ARM64: Rhode Island + York New => New York + Rhode Island
// STDOUT_ARM64: Rhode Island + Wen Kory => New Kory + Rhode Island
// STDOUT_ARM64: Rhode Island + Wen Kory => New York + Rhode Island
// STDOUT_ARM64: Michigan + New York => Kory New + Michigan
// STDOUT_ARM64: Michigan + Wen Kory => Kory New + Michigan
// STDOUT_ARM64: Montana + New York => Kory New + Montana
// STDOUT_ARM64: Louisiana + New York => Kory New + Louisiana
// STDOUT_ARM64: Oklahoma + Wen Kory => New Kory + Oklahoma
// STDOUT_ARM64: Oklahoma + Wen Kory => New York + Oklahoma
// STDOUT_ARM64: Oklahoma + Wen Kory => Kory New + Oklahoma
// STDOUT_ARM64: Oklahoma + York New => Kory New + Oklahoma
// STDOUT_ARM64: Pennsylvania + Wen Kory => Kory New + Pennsylvania
// STDOUT_ARM64: Pennsylvania + Wen Kory => New Kory + Pennsylvania
// STDOUT_ARM64: Pennsylvania + Wen Kory => New York + Pennsylvania
// STDOUT_ARM64: Pennsylvania + York New => Kory New + Pennsylvania
// STDOUT_ARM64: Pennsylvania + York New => New Kory + Pennsylvania
// STDOUT_ARM64: Pennsylvania + York New => New York + Pennsylvania
// STDOUT_ARM64: North Dakota + Wen Kory => Kory New + North Dakota
// STDOUT_ARM64: North Dakota + Wen Kory => New York + North Dakota
// STDOUT_ARM64: North Dakota + York New => Kory New + North Dakota
// STDOUT_ARM64: North Dakota + York New => New York + North Dakota
// STDOUT_ARM64: South Carolina + Wen Kory => New Kory + South Carolina
// STDOUT_ARM64: South Carolina + Wen Kory => Kory New + South Carolina
// STDOUT_ARM64: South Carolina + York New => Kory New + South Carolina
// STDOUT_ARM64: North Carolina + York New => New Kory + North Carolina
// STDOUT_ARM64: North Carolina + York New => Kory New + North Carolina
// STDOUT_ARM64: North Carolina + Wen Kory => New Kory + North Carolina
// STDOUT_ARM64: North Carolina + Wen Kory => Kory New + North Carolina
// STDOUT_ARM64: Massachusetts + New York => Kory New + Massachusetts
// STDOUT_ARM64: Massachusetts + York New => Kory New + Massachusetts
// STDOUT_ARM64: Massachusetts + New Kory => Kory New + Massachusetts
// STDOUT_ARM64: North Dakota + South Carolina => North Carolina + South Dakota

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define USE_FAKES 1

const char *states[] = {
#if USE_FAKES
	"New Kory", "Wen Kory", "York New", "Kory New", "New Kory",
#endif
	"Alabama", "Alaska", "Arizona", "Arkansas",
	"California", "Colorado", "Connecticut",
	"Delaware",    
	"Florida", "Georgia", "Hawaii",
	"Idaho", "Illinois", "Indiana", "Iowa",
	"Kansas", "Kentucky", "Louisiana",
	"Maine", "Maryland", "Massachusetts", "Michigan",
	"Minnesota", "Mississippi", "Missouri", "Montana",
	"Nebraska", "Nevada", "New Hampshire", "New Jersey",
	"New Mexico", "New York", "North Carolina", "North Dakota",
	"Ohio", "Oklahoma", "Oregon",
	"Pennsylvania", "Rhode Island",
	"South Carolina", "South Dakota", "Tennessee", "Texas",
	"Utah", "Vermont", "Virginia",
	"Washington", "West Virginia", "Wisconsin", "Wyoming"
};

int n_states = sizeof(states)/sizeof(*states);
typedef struct { unsigned char c[26]; const char *name[2]; } letters;

void count_letters(letters *l, const char *s)
{
	int c;
	if (!l->name[0]) l->name[0] = s;
	else l->name[1] = s;

	while ((c = *s++)) {
		if (c >= 'a' && c <= 'z') l->c[c - 'a']++;
		if (c >= 'A' && c <= 'Z') l->c[c - 'A']++;
	}
}

int lcmp(const void *aa, const void *bb)
{
	int i;
	const letters *a = aa, *b = bb;
	for (i = 0; i < 26; i++)
		if      (a->c[i] > b->c[i]) return  1;
		else if (a->c[i] < b->c[i]) return -1;
	return 0;
}

int scmp(const void *a, const void *b)
{
	return strcmp(*(const char *const *)a, *(const char *const *)b);
}

void no_dup()
{
	int i, j;

	qsort(states, n_states, sizeof(const char*), scmp);

	for (i = j = 0; i < n_states;) {
		while (++i < n_states && !strcmp(states[i], states[j]));
		if (i < n_states) states[++j] = states[i];
	}

	n_states = j + 1;
}

void find_mix()
{
	int i, j, n;
	letters *l, *p;

	no_dup();
	n = n_states * (n_states - 1) / 2;
	p = l = calloc(n, sizeof(letters));

	for (i = 0; i < n_states; i++)
		for (j = i + 1; j < n_states; j++, p++) {
			count_letters(p, states[i]);
			count_letters(p, states[j]);
		}

	qsort(l, n, sizeof(letters), lcmp);

	for (j = 0; j < n; j++) {
		for (i = j + 1; i < n && !lcmp(l + j, l + i); i++) {
			if (l[j].name[0] == l[i].name[0]
				|| l[j].name[1] == l[i].name[0]
				|| l[j].name[1] == l[i].name[1])
				continue;
			printf("%s + %s => %s + %s\n",
				l[j].name[0], l[j].name[1], l[i].name[0], l[i].name[1]);
		}
	}
	free(l);
}

int main(void)
{
	find_mix();
	return 0;
}
