class DatabaseError(BaseException):

    def __init__(self) -> None:
        super().__init__("Database error")


class UserNotFoundError(BaseException):

    def __init__(self) -> None:
        super().__init__("User not found")


class UserNotInTripError(BaseException):

    def __init__(self) -> None:
        super().__init__("User not in trip")


class GeocodingError(BaseException):

    def __init__(self) -> None:
        super().__init__("Geocoding error")


class LocationExistsError(BaseException):

    def __init__(self) -> None:
        super().__init__("Location already exists")


class InvalidDateError(BaseException):

    def __init__(self) -> None:
        super().__init__("Date is in the date interval of the previous location")


class NavigationError(BaseException):

    def __init__(self) -> None:
        super().__init__("Can not build the navigation route")


class IsStartPointError(BaseException):

    def __init__(self) -> None:
        super().__init__(
            "Can not add the same location to the trip as the starting point"
        )


class NoLocationsError(BaseException):

    def __init__(self) -> None:
        super().__init__("No locations in the trip")


class WeatherDateError(BaseException):

    def __init__(self) -> None:
        super().__init__("The weather forecast is only available for 16 days ahead")


class ServiceConnectionError(BaseException):

    def __init__(self) -> None:
        super().__init__("Can not connect to the external service")
