pymacro is a very simple tool to access dictionaries via the command line.

 === CMDLINE OPTIONS ===



 === CONFIG / META ===

/pymacro_config.json
option						type	default		description
src							str		"my_dict"	Points to the dictionary that is operated on.
no-print-output				bool	False		Disables printing output to stdout.
no-clip-output				bool	False		Disables copying output to clipboard.
log-warnings				bool	True		Enables printing warnings to stdout.
treat-warnings-as-errors	bool	False		Any triggered warning will abort the program instead of silently continuing.

/dictionaries/<dict-name>.meta.json
option						type	default		description
readonly					bool	False		Simply makes this dict readonly
no-add						bool	False		Disables addition of entries
no-overwrite				bool	False		Disables overwriting of entries
no-delete					bool	False		Disables deletion of entries
keep-sorted					bool	True		Keeps the dictionary sorted by keys.
store-pretty				bool	True		Keeps the dictionary indented by 4 per nest.