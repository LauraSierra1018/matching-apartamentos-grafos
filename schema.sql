CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    budget REAL,
    zona TEXT,
    radio REAL,
    pets INTEGER,
    amenities_req TEXT,
    size_deseado REAL,
    bedrooms_deseado INTEGER
);

CREATE TABLE apartamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    price REAL,
    zona TEXT,
    distancia REAL,
    pet_friendly INTEGER,
    amenities TEXT,
    size REAL,
    bedrooms INTEGER
);

CREATE TABLE asignaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    apartamento_id INTEGER,
    peso REAL
);