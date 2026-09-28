from apps.workstations.models import Station, StationType


def create_reception_desk(name: str = "Guichê 01") -> Station:
    return Station.objects.create(station_type=StationType.RECEPTION_DESK, name=name)


def create_consultation_room(name: str = "Consultório 01") -> Station:
    return Station.objects.create(station_type=StationType.CONSULTATION_ROOM, name=name)
