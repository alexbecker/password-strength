Password-Strength
-----------------

This library defines the strength() function, which estimates the number of bits of entropy
a password has in the face of a clever attacker. It considers several plausible strategies
an attacker might use, and returns the lowest number of bits the password has relative to any strategy.

The strategies used are:
 - Random passwords using various charsets. This includes guessing that small subsets of charsets are 
being used, e.g. "aaaaaaaaaaaaaaaaaaaaa" is not a good password.
 - Dictionary attacks using a list of common formats (including capitalization, l33t and symbols), 
in order of increasing complexity, and several possible sets of dictionaries:
	- Names
	- Nouns, both short and long lists
	- Words, both short and long lists
 - Recursive strategies where passwords are assumed to consist of multiple plausible passwords concatenated.

The algorithm was not trained using any dataset.
Statistics computed on the [password sets](https://xato.net/passwords/ten-million-passwords/#.VNszglOsXsb) 
released by Mark Burnett are located in the stats/results.txt file.
Of particular note are the fractions of all users with given levels of password entropy:

| bits |  users  |
|------|--------:|
| 0-20 | 3178432 |
|20-30 | 3280626 |
|30-40 | 1976416 |
|40-50 | 1009985 |
|50-60 | 308812  |
|60-999| 245702  |
