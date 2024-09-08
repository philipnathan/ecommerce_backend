from datetime import datetime


def get_data_and_validate(data, **kwargs):
    value = {}

    try:
        for variable, datatype in kwargs.items():
            if data.get(variable) is None:
                continue

            if datatype == datetime:
                try:
                    value[variable] = datetime.strptime(
                        data.get(variable), "%Y-%m-%d %H:%M:%S"
                    )
                    continue
                except ValueError:
                    raise ValueError(
                        f"Invalid value for {variable}. It must be in the format 'YYYY-MM-DD HH:MM:SS'"
                    )

            if not isinstance(data.get(variable), datatype):
                raise ValueError(
                    f"Invalid value for {variable}. It must be a valid {datatype}"
                )

            if data.get(variable):
                value[variable] = datatype(data.get(variable))
            else:
                value[variable] = None

        return value

    except ValueError as e:
        raise e
