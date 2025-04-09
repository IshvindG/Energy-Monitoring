DROP TABLE IF EXISTS prices;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS generations;
DROP TABLE IF EXISTS carbon_intensities;
DROP TABLE IF EXISTS fuel_types;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS outage_postcodes;
DROP TABLE IF EXISTS outages;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS demands;
DROP TABLE IF EXISTS providers;


CREATE TABLE providers(
    provider_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    provider_name VARCHAR(50),
    PRIMARY KEY (provider_id)
);

CREATE TABLE regions(
    region_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    region_name VARCHAR(100),
    provider_id SMALLINT,
    PRIMARY KEY (region_id),
    CONSTRAINT fk_provider_id FOREIGN KEY (provider_id) REFERENCES providers (provider_id)
);

CREATE TABLE outages(
    outage_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    outage_start TIMESTAMP,
    outage_end TIMESTAMP,
    region_id SMALLINT,
    planned BOOL,
    PRIMARY KEY (outage_id),
    CONSTRAINT fk_region_id_outage FOREIGN KEY (region_id) REFERENCES regions (region_id)
);

CREATE TABLE outage_postcodes(
    outage_postcode_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    postcode VARCHAR(7),
    outage_id SMALLINT,
    PRIMARY KEY (outage_postcode_id),
    CONSTRAINT fk_outage_id FOREIGN KEY (outage_id) REFERENCES outages (outage_id)
);


CREATE TABLE prices(
    price_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    price_per_mwh DECIMAL(5,2),
    price_at TIMESTAMP,
    PRIMARY KEY (price_id)
);


CREATE TABLE carbon_intensities(
    carbon_intensity_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    index VARCHAR(10),
    current_measure SMALLINT,
    forecast_measure SMALLINT,
    measure_at TIMESTAMP,
    region_id SMALLINT,
    PRIMARY KEY (carbon_intensity_id),
    CONSTRAINT fk_region_id_carbons FOREIGN KEY (region_id) REFERENCES regions (region_id) 

);

CREATE TABLE fuel_types(
    fuel_type_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    fuel_type VARCHAR(20),
    fuel_type_name VARCHAR(50),
    PRIMARY KEY (fuel_type_id)
);

CREATE TABLE generations(
    generation_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    mw_generated SMALLINT,
    fuel_type_id SMALLINT,
    generation_at TIMESTAMP,
    PRIMARY KEY (generation_id),
    CONSTRAINT fk_fuel_type_id FOREIGN KEY (fuel_type_id) REFERENCES fuel_types (fuel_type_id)
);

CREATE TABLE users(
    user_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    DOB DATE,
    email VARCHAR(254),
    phone_number VARCHAR(15),
    postcode VARCHAR(7),
    PRIMARY KEY (user_id)
);

CREATE TABLE subscriptions(
    subscription_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    user_id SMALLINT,
    region_id SMALLINT,
    PRIMARY KEY (subscription_id),
    CONSTRAINT fk_region_id_subscription FOREIGN KEY (region_id) REFERENCES regions (region_id),
    CONSTRAINT fk_user_id_subscription FOREIGN KEY (user_id) REFERENCES users (user_id) 
);

CREATE TABLE alerts(
    alert_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    outage_postcode_id SMALLINT,
    user_id SMALLINT,
    last_alert_sent TIMESTAMP,
    region_id SMALLINT,
    PRIMARY KEY (alert_id),
    CONSTRAINT fk_outage_postcode_id FOREIGN KEY (outage_postcode_id) REFERENCES outage_postcodes (outage_postcode_id),
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT fk_region_id_alerts FOREIGN KEY (region_id) REFERENCES regions (region_id)

);

CREATE TABLE demands(
    demand_id SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    demand_at TIMESTAMP,
    total_demand BIGINT,
    PRIMARY KEY (demand_id)
);