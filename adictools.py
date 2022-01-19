import argparse
import os
import json
import pyperclip

config_location = "adictools_config.json"
dict_base_location = "dictionaries"
dict_ext = ".json"
meta_ext = ".meta.json"

DEFAULT_CONFIG = {
	"src": "my_dict",
	"no-clip-output": False,
	"no-print-output": False,
	"log-warnings": True,
	"treat-warnings-as-errors": False
}

DEFAULT_META = {
	"readonly": False,
	"no-add": False,
	"no-overwrite": False,
	"no-delete": False,
	"keep-sorted": True,
	"store-pretty": True
}

def get_args():
	parser = argparse.ArgumentParser(
	description="""A simple dictionary tool that copies value to clipboard or prints a value retrieved from a key.""",
	epilog="Regardless of order, options are always processed in this order: Config, Add, List, Get, Delete. Only the last occurrence of a duplicate option is used.")
	
	parser.add_argument("-a", "--add", nargs="*",
		default=None,
		metavar=("KEY", "VALUE"),
		dest="key_value",
		help="Add a key-value pair to the selected dictionary"
	)
	parser.add_argument("-c", "--config", nargs=2,
		default=None,
		metavar=("KEY", "VALUE"),
		dest="configuration_kv",
		help="Configure a key-value pair in the configuration or meta file for the selected dictionary"
	)
	parser.add_argument("-d", "--delete",
		default=None,
		metavar="KEY",
		dest="del_key",
		help="Delete the specified key from the selected dictionary"
	)
	parser.add_argument("-g", "--get",
		default=None,
		metavar="KEY",
		dest="key",
		help="Gets the specified key from the selected dictionary"
	)
	parser.add_argument("-l", "--list",
		dest="list",
		action="store_true",
		help="List all entries in the selected dictionary"
	)
	return parser.parse_args()

def read(json_file):
	with open(json_file, 'r') as f:
		try:
			return json.load(f)
		except:
			if (input("[ERROR] The configuration file is corrupt. Would you like to reset it? (y/n): ").strip().lower() == 'y'): return {}
			else: raise Exception("Aborted due to malformed configuration.")

def write(json_file, data, sort_keys=None, indent=None):
	with open(json_file, 'w+') as f:
		json.dump(data, f, sort_keys=sort_keys, indent=indent)

def dict_as_list(dic, sort=False):
	sz = 0
	for k in dic:
		sz = max(sz, len(k))

	if sort:
		dic = dict(sorted(dic.items()))
	
	s = []
	for k, v in dic.items():
		s.append(f" {k}:{' ' * (1 + sz - len(k))}{v}")

	return s

def update_settings(loc, default, key, val, skip_keys=None):
	if (os.path.isfile(loc)):
		settings = read(loc)

		# Defaults
		for k in default:
			if not (k in settings) or not isinstance(settings[k], type(default[k])):
				settings[k] = default[k]
	else:
		settings = default
	
	if key is not None and val is not None:
		if isinstance(skip_keys, dict) and key in skip_keys: # Handle by other
			pass
		elif key in settings:
			if isinstance(default[key], str):
				settings[key] = val
			elif isinstance(default[key], bool):
				value = val.lower() in ("true", "1", "t", "y", "yes")
				if not value:
					value = not (val.lower() in ("false", "0", "f", "n", "no"))
					if value: raise ValueError(f"Could not convert {val} to bool.")
				settings[key] = value
			elif isinstance(default[key], int):
				settings[key] = int(val)
			else:
				raise Exception(f"Invalid type {type(default[key])} in configuration.")
			print("Updated settings: ")
			print('\n'.join(dict_as_list(settings)))
			
		else: raise Exception(f"Config key: {key} not found.")

	write(loc, settings, sort_keys=False, indent=4)
	return settings

def main():
	args = get_args()

	#### CONFIGS ####
	ck, cv = None, None
	if args.configuration_kv:
		ck = args.configuration_kv[0]
		cv = args.configuration_kv[1]
	
	config = update_settings(config_location, DEFAULT_CONFIG, ck, cv, DEFAULT_META)
	
	def warn(msg):
		nonlocal config
		if config["treat-warnings-as-errors"]: raise Exception(msg)
		if config["log-warnings"]: print(f"[Warning] {msg}")

	##### METAS #####
	meta_location = os.path.join(dict_base_location, f"{config['src']}{meta_ext}")

	os.makedirs(dict_base_location, exist_ok=True)

	meta = update_settings(meta_location, DEFAULT_META, ck, cv, DEFAULT_CONFIG)
	
	##### DICTS #####
	dict_location = os.path.join(dict_base_location, f"{config['src']}{dict_ext}")
	
	srcdict = read(dict_location) if (os.path.isfile(dict_location)) else {}
	
	if not config['no-print-output']: print(f'Selected dictionary: "{config["src"]}"')
	
	if args.key_value:
		if not (meta["readonly"] or meta["no-add"]):
			k = args.key_value[0]
			v = "" if len(args.key_value) < 2 else ' '.join(args.key_value[1:])
			if not (k in srcdict and meta["no-overwrite"]):
				srcdict[k] = v
			else: warn("Configuration disallows overwriting.")
		else: warn("Configuration disallows additions.")
	
	if args.list is not None or args.key is not None:
		if not (config['no-print-output'] and config['no-clip-output']):
			if args.list:
				s = dict_as_list(srcdict, True)
				s = f'[Dictionary "{config["src"]}" is empty]' if len(s) < 1 else '\n'.join(s)
				
				if not config['no-print-output']: print(s)
				if not config['no-clip-output']: pyperclip.copy(s)
			
			if args.key:
				k = args.key
				if k in srcdict:
					if not config['no-print-output']: print(srcdict[k])
					if not config['no-clip-output']: pyperclip.copy(srcdict[k])
				else: warn(f'There is no data stored for key "{k}".')
		else: warn("Configuration disallows any useful output.")

	k = args.del_key
	if k is not None:
		if not (meta["readonly"] or meta["no-delete"]):
			if k in srcdict:
				del srcdict[k]
			else: warn(f'Key "{k}" could not be deleted (not found).')
		else: warn(f"Configuration disallows deletions.")

	write(dict_location, srcdict, sort_keys=meta['keep-sorted'], indent=4 if meta['store-pretty'] else None)


if __name__ == '__main__':
	main()