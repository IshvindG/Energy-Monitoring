CREATE OR REPLACE VIEW region_provider
AS SELECT region_id, region_name, r.provider_id
FROM regions r
JOIN providers p ON p.provider_id = r.provider_id;


CREATE OR REPLACE VIEW alert_users
AS SELECT 
    first_name,
    phone_number,
    email,
    alert_id,
    a.user_id,
    region_id,
    postcode
FROM users u
JOIN alerts a ON a.user_id = u.user_id;