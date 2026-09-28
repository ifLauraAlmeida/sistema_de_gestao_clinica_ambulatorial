export type StationType = 'RECEPTION_DESK' | 'CONSULTATION_ROOM';

export interface Station {
  id: string;
  name: string;
  station_type: StationType;
  station_type_label: string;
}

export interface WorkSession {
  id: string;
  station: Station;
  started_at: string;
  ended_at: string | null;
}
