CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL
);

CREATE TABLE incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    owner VARCHAR(50) NOT NULL,
    notes TEXT NOT NULL
);

INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin'),
('analyst', 'student123', 'analyst'),
('guest', 'guest123', 'guest');

INSERT INTO incidents (title, severity, owner, notes) VALUES
('Nieudane logowania do VPN', 'medium', 'Nowak', 'Wzrost liczby błędnych logowań od 08:30'),
('Podejrzany ruch HTTP', 'high', 'Kowalski', 'Nietypowe parametry w żądaniach do portalu'),
('Zmiana hasła konta uprzywilejowanego', 'critical', 'Admin', 'Weryfikacja wymagana przez CSIRT'),
('Błąd uprawnień w systemie zgłoszeń', 'low', 'Wiśniewski', 'Wymaga przeglądu konfiguracji ról');
