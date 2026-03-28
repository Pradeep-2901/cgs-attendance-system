-- =============================================
-- UNIFIED GEOFENCING SYSTEM - DATABASE SCHEMA
-- CGS Green Sustainergy - Complete Implementation
-- =============================================

USE cgs;

-- =============================================
-- 1. COMPANY SETTINGS TABLE
-- Stores main office location and system settings
-- =============================================

CREATE TABLE IF NOT EXISTS company_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_name VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Pre-populate with CGS Green Sustainergy office data (use INSERT IGNORE to avoid duplicates)
INSERT IGNORE INTO company_settings (setting_name, setting_value) VALUES
('office_address', 'CGS Green Sustainergy, Chennai, Tamil Nadu, India'),
('office_lat', '13.0475'),
('office_lon', '80.2400'),
('office_radius', '200'),
('company_name', 'CGS Green Sustainergy'),
('geofencing_enabled', 'true');

-- =============================================
-- 2. OFFICIAL SITES TABLE
-- Admin-defined list of approved work locations
-- =============================================

CREATE TABLE IF NOT EXISTS sites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_name VARCHAR(255) NOT NULL,
    site_address TEXT NOT NULL,
    site_lat DECIMAL(10, 8) NOT NULL,
    site_lon DECIMAL(11, 8) NOT NULL,
    site_radius INT DEFAULT 200,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Add some sample sites for demonstration
INSERT INTO sites (site_name, site_address, site_lat, site_lon, created_by) VALUES
('Client Office - Tech Park', 'IT Corridor, OMR, Chennai, Tamil Nadu', 12.9698, 80.2434, 'adm001'),
('Project Site - Guindy', 'Guindy Industrial Estate, Chennai, Tamil Nadu', 13.0067, 80.2206, 'adm001'),
('Regional Office - Coimbatore', 'RS Puram, Coimbatore, Tamil Nadu', 11.0168, 76.9558, 'adm001');

-- =============================================
-- 3. SITE VISITS TABLE
-- Employee requests for temporary on-site work
-- =============================================

CREATE TABLE IF NOT EXISTS site_visits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    site_id INT NOT NULL,
    visit_date DATE NOT NULL,
    reason TEXT,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by VARCHAR(10) NULL,
    reviewed_at TIMESTAMP NULL,
    review_notes TEXT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(user_id),
    UNIQUE KEY unique_user_site_date (user_id, site_id, visit_date)
);

-- =============================================
-- 4. MODIFY USERS TABLE
-- Add work mode and remote location fields
-- =============================================

-- Add work mode column
ALTER TABLE users 
ADD COLUMN work_mode ENUM('Office', 'Remote') NOT NULL DEFAULT 'Office';

-- Add remote work location fields
ALTER TABLE users 
ADD COLUMN remote_address VARCHAR(255) NULL,
ADD COLUMN remote_lat DECIMAL(10, 8) NULL,
ADD COLUMN remote_lon DECIMAL(11, 8) NULL;

-- =============================================
-- 5. CREATE INDEXES FOR PERFORMANCE
-- =============================================

CREATE INDEX idx_site_visits_user_date ON site_visits(user_id, visit_date);
CREATE INDEX idx_site_visits_status ON site_visits(status);
CREATE INDEX idx_sites_active ON sites(is_active);
CREATE INDEX idx_users_work_mode ON users(work_mode);

-- =============================================
-- 6. UPDATE EXISTING EMPLOYEES (OPTIONAL)
-- Set default work modes for existing employees
-- =============================================

-- Set all existing employees to 'Office' mode by default
UPDATE users SET work_mode = 'Office' WHERE role = 'employee';

-- =============================================
-- SCHEMA CREATION COMPLETE
-- =============================================

SELECT 'Unified Geofencing System Database Schema Created Successfully!' as status;
SELECT COUNT(*) as total_sites FROM sites;
SELECT COUNT(*) as total_employees FROM users WHERE role = 'employee';
SELECT setting_name, setting_value FROM company_settings;