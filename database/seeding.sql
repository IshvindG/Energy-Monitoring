INSERT INTO providers (provider_name) VALUES ('Scottish and Southern Energy (SSE)'),
('SP Energy Networks'),
('Electricity North West'),
('Northern Powergrid'),
('National Grid'),
('UK Power Networks'),
('Manx Utilities'),
('ESB Networks'),
('Northern Ireland Electricity Networks');

INSERT INTO regions (region_name, provider_id) VALUES
('North Scotland', 1),
('South Scotland', 1),
('North West England', 3),
('North East England', 4),
('Yorkshire', 4),
('North Wales & Merseyside', 2),
('South Wales', 2),
('West Midlands', 5),
('East Midlands', 5),
('East England', 6),
('South West England', 5),
('South England', 5),
('London', 6),
('South East England', 6),
('England', 5),
('Scotland', 1),
('Wales', 2);

INSERT INTO fuel_categories (fuel_category) VALUES
('Fossil Fuels'),
('Renewables'),
('Other'),
('Interconnectors');