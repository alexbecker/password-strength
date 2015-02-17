import string
from math import log
from collections import Counter
from pyparsing import Word, ParseException, Optional, lineEnd

wordsetFilePaths = {"male_first": "data/male_first_names.txt",
					"female_first": "data/female_first_names.txt",
					"last": "data/last_names.txt",
					"nouns_short": "data/nouns_short.txt",
					"nouns": "data/nouns.txt",
					"words_short": "data/words_short.txt",
					"words": "data/words.txt"}
wordsets = {}
wordsetBonuses = {}
for kind in wordsetFilePaths:
	wordsetFile = open(wordsetFilePaths[kind], "r")
	wordsets[kind] = set()
	for line in wordsetFile:
		wordsets[kind].add(line[:-1])
	wordsetBonuses[kind] = round(log(len(wordsets[kind]), 2))

lower = string.ascii_lowercase
upper = string.ascii_uppercase
letters = string.ascii_letters
digits = string.digits
hexdigits = string.hexdigits
leetdigits = "01345"
leetletters = "oieas"
leet = lower + leetdigits
symbols = ",.?!@#$%^&*-+~_"
allchars = string.printable

leetToAscii = {"0": "o",
			   "1": "i",
			   "3": "e",
			   "4": "a",
			   "5": "s"}
leetPattern = Word(leet).setResultsName("leet")
numbersPattern = Word(digits).setResultsName("numbers")
symbolsPattern = Word(symbols).setResultsName("symbols")
remainderPattern = Optional(Word(allchars)).setResultsName("remainder") + lineEnd
patterns = [[leetPattern + remainderPattern],
			[numbersPattern + remainderPattern],
			[leetPattern + numbersPattern + remainderPattern,
			 leetPattern + symbolsPattern + remainderPattern],
			[leetPattern + numbersPattern + symbolsPattern + remainderPattern,
			 leetPattern + symbolsPattern + numbersPattern + remainderPattern,
			 numbersPattern + symbolsPattern + remainderPattern,
			 symbolsPattern + numbersPattern + remainderPattern]
		   ]

def capitalBonus(string):
	lowercase = 0
	uppercase = 0
	for char in string:
		if char.islower():
			lowercase += 1
		elif char.isupper():
			uppercase += 1

	if uppercase == 0:
		return 0
	elif uppercase == 1 and string[0].isupper():
		return 1

	return lowercase + uppercase

twoDigitYears = set(map(str, list(range(84, 100)))).union(set(["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15"]))
fourDigitYears = set(map(str, range(1951, 2016)))
dates = set([month + day for month in ["01","02","03","04","05","06","07","08","09","10","11","12"] for day in ["01","02","03","04","05","06","07","08","09"] + list(map(str, range(10, 32)))])

def numberBonus(string):
	if string == "1":	# always first guess
		return 0
	if string in twoDigitYears:
		return 5
	if string in fourDigitYears:
		return 6
	if string in dates:
		return 9

	return int(10 * len(string) / 3)

def symbolBonus(string):
	if string == "!":	# always first guess
		return 0
	if string == "!" * len(string):
		return len(string) - 1

	return 4 * len(string)

def leetBonus(string):
	leetchars = 0
	leetable = 0
	for char in string:
		if char in leetdigits:
			leetchars += 1
		if char in leetletters:
			leetable += 1

	wordscore = wordlistBonus(deleet(string))

	if leetchars == 0:
		return wordscore
	elif wordscore:
		return leetable + leetchars + wordscore
	else:
		return None

def deleet(string):
	result = ""
	for char in string:
		if char in leetToAscii:
			result += leetToAscii[char]
		else:
			result += char

	return result

def wordBonus(string):
	result = 10000

	for kind in wordsets:
		if string in wordsets[kind]:
			result = min(result, wordsetBonuses[kind])
		elif string != "" and string[-1] == "s" and string[:-1] in wordsets[kind]:
			result = min(result, wordsetBonuses[kind] + 1)

	if result == 10000:
		return None
	return result

def wordlistBonus(string):
	"""
	Return the lowest sum of all possible word bonusus in a list of words
	"""
	if string == "":
		return 0

	results = [None] * len(string)	# results[i] = wordsBonus(string[:i])

	for i in range(len(string)):
		results[i] = wordBonus(string[:i + 1])

		for j in range(i):
			sliceBonus = wordBonus(string[j + 1:i + 1])

			if results[j] != None and sliceBonus != None:
				if results[i] != None:
					results[i] = min(results[i], results[j] + sliceBonus)
				else:
					results[i] = results[j] + sliceBonus

	return results[len(string) - 1]

def remainderBonus(string):
	return 1 + strength(string)

bonusFunctions = {"words": wordlistBonus,
				  "numbers": numberBonus,
				  "symbols": symbolBonus,
				  "leet": leetBonus,
				  "remainder": remainderBonus}

def randomStrength(password):
	"""
	Strength of a truly random password, based on length and charset
	"""
	charsets = [lower, upper, letters, digits, hexdigits, lower + digits, upper + digits, letters + digits,
				lower + symbols, upper + symbols, letters + symbols, digits + symbols, hexdigits + symbols,
				lower + digits + symbols, upper + digits + symbols, letters + digits + symbols]

	lowestCharsetBonus = 6	# base64 bonus
	for charset in charsets:
		inCharset = all([char in charset for char in password])

		if inCharset:
			lowestCharsetBonus = min(lowestCharsetBonus, log(len(charset), 2))

	bonus = lowestCharsetBonus * len(password)

	# handle really small subsets of charsets
	distinctChars = len(set(password))
	if distinctChars == 1:
		bonus = min(bonus, lowestCharsetBonus + int(log(len(password), 2)) + 1)
	elif distinctChars == 2:
		bonus = min(bonus, 2 * lowestCharsetBonus + len(password)) + int(log(len(password), 2)) 
	elif distinctChars == 3:
		bonus = min(bonus, 3 * lowestCharsetBonus + log(3, 2) * len(password) + int(log(len(password), 2))  - 1)

	return int(bonus)

def strength(password, verbose=False):
	"""
	Returns the number of bits of entropy in a password.
	"""
	passwordLower = password.lower()
	entropy = 10000

	for i in range(len(patterns)):
		for pattern in patterns[i]:
			try:
				match = pattern.parseString(passwordLower).asDict()
			except ParseException:
				continue

			possibleMatches = [match]
			if "leet" in match:
				# handle issue of greedyness eating trailing numbers
				while match["leet"] != "" and match["leet"][-1] in digits:
					match = match.copy()

					if "numbers" in match:
						match["numbers"] = match["leet"][-1] + match["numbers"]
					else:
						match["numbers"] = match["leet"][-1]
					match["leet"] = match["leet"][:-1]

					possibleMatches.append(match)

			for possibleMatch in possibleMatches:
				matchEntropy = i + capitalBonus(password)

				for elem in possibleMatch:
					bonus = bonusFunctions[elem](possibleMatch[elem])

					if bonus != None:
						matchEntropy += bonus
					else:
						matchEntropy = None
						break

				if verbose:
					print("pattern: {} entropy: {}".format(possibleMatch, matchEntropy))

				if matchEntropy and matchEntropy < entropy:
					entropy = matchEntropy

	randomEntropy = randomStrength(password)

	if verbose:
		print("random entropy: {}".format(randomEntropy))

	return min(entropy, randomEntropy)

# statistics on actual password lists
statfiles = ["stats/10kmostcommon.txt", "stats/100kmostcommon.txt", "stats/10mduplicates.txt", "stats/10mall.txt"]

def stats():
	for statfile in statfiles:
		fp = open(statfile, "r")

		entropyCounts = Counter()
		for line in fp:
			entropyCounts[strength(line[:-1])] += 1

		buckets = [0, 30, 40, 50, 60, 999]

		print("file: {}".format(statfile))
		for i in range(1, len(buckets)):
			bucketCount = sum([entropyCounts[e] for e in entropyCounts if e >= buckets[i-1] and e < buckets[i]])

			print("\t{} <= bits < {}: \t{}".format(buckets[i-1], buckets[i], bucketCount))
