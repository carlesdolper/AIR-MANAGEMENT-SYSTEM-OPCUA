CREATE TABLE cycle_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    cycle_type TEXT NOT NULL,
    quality_score REAL NOT NULL
);

-- Crear tabla de mediciones detalladas
CREATE TABLE cycle_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_id INTEGER,
    phase_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    flow REAL,
    accum_flow REAL,
    temperature REAL,
    pressure REAL,
    itv_value REAL,
    FOREIGN KEY (cycle_id) REFERENCES cycle_patterns(id)
);