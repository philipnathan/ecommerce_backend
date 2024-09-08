def is_filled(**data):
    for each_data in data:
        if not each_data:
            return False
    return True
