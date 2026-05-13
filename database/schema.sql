-- database/schema.sql
-- Run: psql -U pag_user -d pag_system -f database/schema.sql

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100) UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    role            VARCHAR(50) NOT NULL DEFAULT 'viewer',
    full_name       VARCHAR(200),
    organization    VARCHAR(200),
    last_login      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Risk assessments table
CREATE TABLE IF NOT EXISTS risk_assessments (
    id                      SERIAL PRIMARY KEY,
    region                  VARCHAR(200) NOT NULL,
    disaster_type           VARCHAR(100) NOT NULL,
    risk_score              FLOAT NOT NULL,
    risk_level              VARCHAR(20) NOT NULL,
    estimated_affected      INTEGER DEFAULT 0,
    estimated_displaced     INTEGER DEFAULT 0,
    crop_damage_crore       FLOAT DEFAULT 0,
    economic_loss_crore     FLOAT DEFAULT 0,
    assessed_at             TIMESTAMP DEFAULT NOW()
);

-- Alerts log table
CREATE TABLE IF NOT EXISTS alerts_log (
    id              SERIAL PRIMARY KEY,
    region          VARCHAR(200) NOT NULL,
    disaster_type   VARCHAR(100) NOT NULL,
    risk_level      VARCHAR(20) NOT NULL,
    alert_text      TEXT,
    channel         VARCHAR(50),   -- 'sms', 'dashboard', 'ussd'
    sent_at         TIMESTAMP DEFAULT NOW()
);

-- Sensor readings (for non-time-series backup)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(50),
    region          VARCHAR(200),
    rainfall_mm     FLOAT,
    wind_speed_kmh  FLOAT,
    river_level_m   FLOAT,
    temperature_c   FLOAT,
    humidity        FLOAT,
    is_anomaly      BOOLEAN DEFAULT FALSE,
    recorded_at     TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_risk_region       ON risk_assessments(region);
CREATE INDEX IF NOT EXISTS idx_risk_assessed_at  ON risk_assessments(assessed_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_region     ON alerts_log(region);
CREATE INDEX IF NOT EXISTS idx_sensor_region     ON sensor_readings(region);

-- Default admin user (password: Admin@1234 — change immediately)
INSERT INTO users (username, password_hash, role, full_name, organization)
VALUES (
    'admin',
    '$2b$12$PLACEHOLDER_HASH_CHANGE_ME',
    'admin',
    'System Administrator',
    'PAG System'
) ON CONFLICT (username) DO NOTHING;

COMMENT ON TABLE users           IS 'Authenticated system users with role-based access';
COMMENT ON TABLE risk_assessments IS 'Historical risk assessment records per region';
COMMENT ON TABLE alerts_log       IS 'Log of all alerts sent via any channel';
COMMENT ON TABLE sensor_readings  IS 'Raw + cleaned sensor readings backup';
