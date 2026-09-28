from rest_framework import serializers

from apps.workstations.models import Station, WorkSession


class StationSerializer(serializers.ModelSerializer[Station]):
    """Posto de trabalho disponível para seleção."""

    station_type_label = serializers.CharField(source="get_station_type_display", read_only=True)

    class Meta:
        model = Station
        fields = ("id", "name", "station_type", "station_type_label")
        read_only_fields = fields


class WorkSessionSerializer(serializers.ModelSerializer[WorkSession]):
    """Sessão de trabalho com o posto ocupado."""

    station = StationSerializer(read_only=True)

    class Meta:
        model = WorkSession
        fields = ("id", "station", "started_at", "ended_at")
        read_only_fields = fields


class StartWorkSessionSerializer(serializers.Serializer[None]):
    """Entrada para iniciar sessão de trabalho."""

    station_id = serializers.UUIDField()
