class InvalidArgumentError(Exception):
    pass

# TODO: This needs to check whether the user-chosed model actually exists (from LiteLLM perspective)
# and if not local it should check whether the user imported the appropriate API-KEYS in the .env
def check_model(model):
    pass

# TODO: This needs to check if the file exists. Needs to be applied for the .yaml and the --input file
# if provided
def check_file_existence(path):
    pass

def check_input(args):
    input_path = args.input
    text = args.text

    if input_path == None and text == None:
        raise InvalidArgumentError("You need to provide at least one form of input, whether that is from CLI or from an input file")

    if input_path != None:
        check_file_existence(input_path)

def check_args(args):
    check_model(args.model)
    check_input(args)
    check_file_existence(args.yaml)
    
