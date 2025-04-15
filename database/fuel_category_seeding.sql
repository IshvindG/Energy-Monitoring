-- Run once fuel_types has been run. Will connect fuel types to their respective category.

UPDATE fuel_types
SET fuel_category_id = 1
WHERE fuel_type ='CCGT'
OR fuel_type ='COAL'
OR fuel_type='OIL'
OR fuel_type='OCGT';

UPDATE fuel_types
SET fuel_category_id = 2
WHERE fuel_type='NPSHYD'
OR fuel_type='WIND'
OR fuel_type='SOLAR';

UPDATE fuel_types
SET fuel_category_id = 3
WHERE fuel_type='BIOMASS'
OR fuel_type='NUCLEAR'
OR fuel_type='PS'
OR fuel_type='OTHER';

UPDATE fuel_types
SET fuel_category_id = 4
WHERE fuel_type LIKE 'INT%';