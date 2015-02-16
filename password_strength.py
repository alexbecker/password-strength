import string
from math import log
from pyparsing import Word, ParseException, Optional, lineEnd

nameFilePaths = {"male_first": "data/male_first_names.txt",
				 "female_first": "data/female_first_names.txt",
				 "last": "data/last_names.txt"}
nameFiles = {}
names = {}
for kind in nameFilePaths:
	nameFiles[kind] = open(nameFilePaths[kind], "r")
	names[kind] = set()
	for line in nameFiles[kind]:
		names[kind].add(line[:-1])
namesBonus = {}
for kind in names:
	namesBonus[kind] = int(log(len(names[kind]), 2))

nounFilePath = "data/nouns.txt"
nounFile = open(nounFilePath, "r")
nouns = set()
for line in nounFile:
	nouns.add(line[:-1])
nounsBonus = int(log(len(nouns)))

wordFilePath = "data/words.txt"
wordFile = open(wordFilePath, "r")
words = set()
for line in wordFile:
	words.add(line[:-1])
wordsBonus = int(log(len(words))) + 1	# for plurals

lower = string.ascii_lowercase
upper = string.ascii_uppercase
letters = string.ascii_letters
digits = string.digits
hexdigits = string.hexdigits
leetdigits = "01345"
leetletters = "oieas"
leet = lower + leetdigits
symbols = ",.?!@#$%^&*-+~"

leetToAscii = {"0": "o",
			   "1": "i",
			   "3": "e",
			   "4": "a",
			   "5": "s"}

leetPattern = Word(leet).setResultsName("leet")
numbersPattern = Word(digits).setResultsName("numbers")
symbolsPattern = Word(symbols).setResultsName("symbols")
remainderPattern = Optional(Word(leet)).setResultsName("remainder") + lineEnd
patterns = [[leetPattern + remainderPattern],	# password
			[leetPattern + numbersPattern + remainderPattern],	# password97
			[leetPattern + symbolsPattern + remainderPattern,	# password!
			 leetPattern + numbersPattern + symbolsPattern + remainderPattern],	# password97!
			[leetPattern + symbolsPattern + numbersPattern + remainderPattern]	# password.1
		   ]

def capitalBonus(string):
	if string.islower():
		return 0
	elif len(string) > 1 and string[1:].islower():
		return 1
	return len(string)

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

	wordscore = wordBonus(deleet(string))

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

def allSplits(string, maxdepth):
	"""
	Recursively parse concatenated words into a list
	Returns all possible parses
	Except after multiple options have been detected at more than maxdepth levels,
	it only uses the first option for the remaining string
	This prevents denial of service attacks like [it] * 40,
	which since "i" and "tit" are both words has 2^20 possible parses
	"""
	if string == "":
		return [[]]

	possibleNextWords = []
	for i in range(1, len(string) + 1):
		if string[:i] in words or (string[i-1] == "s" and string[:i-1] in words):
			possibleNextWords.append((string[:i], string[i:]))

			if maxdepth == 0:
				break

	if len(possibleNextWords) > 1:
		maxdepth -= 1

	def parsePair(pair):
		return list(map(lambda x: [pair[0]] + x, allSplits(pair[1], maxdepth)))
			
	result = []
	for nextWord in possibleNextWords:
		nextParses = allSplits(nextWord[1], maxdepth)
	
		for parse in nextParses:
			result.append([nextWord[0]] + parse)

	return result

def wordBonus(string):
	lowestBonus = 10000

	# first try names
	for kind in names:
		if string in names[kind]:
			lowestBonus = min(lowestBonus, namesBonus[kind])

	# then try concatenated words:
	splits = allSplits(string, 7)

	for split in splits:
		bonus = 0
		for word in split:
			if word in nouns:
				bonus += nounsBonus
			else:
				bonus += wordsBonus

		lowestBonus = min(lowestBonus, bonus)

	if lowestBonus == 10000:
		return None
	return lowestBonus

bonusFunctions = {"words": wordBonus,
				  "numbers": numberBonus,
				  "symbols": symbolBonus,
				  "leet": leetBonus,
				  "remainder": strength}

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
