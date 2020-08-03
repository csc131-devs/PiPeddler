#!/usr/bin/python


##
# "0"
# {
# 		"name"	"Epic Song Name"
# 		"time"	"120.0"
# 		"bpm"	"1.0"
# }
##

# NOTE: This probably doesn't work past 2 levels (braces)
# It is strictly adapted for this program
class KeyValues(object):
	def __init__(self, name:str) -> NoReturn:
		self.name = name
		self.level = 0
		self.sub = {}
		self.children = {}
		self.parent = None

	def load(self, path:str) -> bool:
		file = open(path)
		if not file:
			return False

		prevkey = None
		currkey = self
		brace = 0
		count = 0

		for line in file.readlines():
			count += 1
			line = line.strip([" ", "\t"])

			if line[0] == '{':
				# if brace:
					# raise Exception(f"Failed to parse file '{path}'! Invalid token \{ found on line {count}!")
				brace += 1
				continue

			if line[0] == '}':
				if not brace:
					raise Exception(f"Failed to parse file '{path}'! Invalid token \} found on line {count}!")

				brace -= 1
				if brace is currkey.level:
					currkey = currkey.parent	# Shift up
					prevkey = prevkey.parent
				continue

			if line[0] == '"':
				if "{" in file.seek(count):		# If next line has brace, make new KV
					line = line.strip([" ", "\t", "\""])	# Kill quotes

					if brace > currkey.level:
						prevkey = currkey

					currkey = KeyValues(line)
					currkey.level = brace
					currkey.parent = prevkey
					prevkey.children[line] = currkey
					continue

				line = line.strip("\"")		# Kill leading/trailing quotes to isolate key and value
				kv = line[line.rfind("\"") : " " : line.find("\"")]		# I f%#$ing hate Python strings

				# KV has reversed into Value-Key because Python
				kv = kv.split()
				kv[0].strip("\"")
				kv[1].strip("\"")	# Begone quotation marks!

				currkey.sub[kv[1]] = kv[0]

		file.close()



	def get_song(self, key:str) -> KeyValues:
		return self.children[key]

	def get(self, key:str) -> Any:
		return self.sub[key]








