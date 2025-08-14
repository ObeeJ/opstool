-- GDPR related tables

-- Table for storing user consents
CREATE TABLE user_consents (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    consent_type VARCHAR(50) NOT NULL,
    granted BOOLEAN NOT NULL DEFAULT false,
    consent_date TIMESTAMP NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    expiry_date TIMESTAMP,
    UNIQUE(user_id, consent_type)
);

-- Table for personal data tracking
CREATE TABLE personal_data (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    data_value TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    retention_period TIMESTAMP NOT NULL,
    encrypted BOOLEAN NOT NULL DEFAULT true,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table for data deletion requests (right to be forgotten)
CREATE TABLE deletion_requests (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    request_date TIMESTAMP NOT NULL,
    completed_date TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table for data export requests (right to data portability)
CREATE TABLE export_requests (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    request_date TIMESTAMP NOT NULL,
    completed_date TIMESTAMP,
    export_file_path TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for faster lookups
CREATE INDEX idx_personal_data_user_id ON personal_data(user_id);
CREATE INDEX idx_user_consents_user_id ON user_consents(user_id);
CREATE INDEX idx_deletion_requests_user_id ON deletion_requests(user_id);
CREATE INDEX idx_export_requests_user_id ON export_requests(user_id);
