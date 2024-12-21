def get_response(user_input:str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return "*awkward silence*"
    
    return 'default'