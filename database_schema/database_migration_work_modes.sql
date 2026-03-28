-- ===================================================================
-- CGS Attendance System - Hierarchical Geofencing Schema Migration
-- ===================================================================
-- This script adds work mode support and company settings management
-- Execute these queries in your MySQL database in order

-- 1. Add work mode and remote location columns to users table
ALTER TABLE users 
ADD COLUMN work_mode ENUM('Office', 'Remote') NOT NULL DEFAULT 'Office' AFTER role,
ADD COLUMN remote_address VARCHAR(255) NULL AFTER work_mode,
ADD COLUMN remote_lat DECIMAL(10, 8) NULL AFTER remote_address,
ADD COLUMN remote_lon DECIMAL(11, 8) NULL AFTER remote_lat;

-- 2. Create company_settings table for flexible configuration
CREATE TABLE company_settings (
    setting_id INT PRIMARY KEY AUTO_INCREMENT,
    setting_name VARCHAR(50) NOT NULL UNIQUE,
    setting_value VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(10) NULL,
    FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 3. Create site_visits table for on-site visit management
CREATE TABLE site_visits (
    visit_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(10) NOT NULL,
    site_name VARCHAR(100) NOT NULL,
    site_address VARCHAR(255) NOT NULL,
    site_lat DECIMAL(10, 8) NOT NULL,
    site_lon DECIMAL(11, 8) NOT NULL,
    visit_date DATE NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by VARCHAR(10) NULL,
    review_date TIMESTAMP NULL,
    INDEX idx_user_date (user_id, visit_date),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 4. Pre-populate main office location (CGS Green Sustainergy, Chennai)
-- Note: Replace with actual coordinates for CGS Green Sustainergy
INSERT INTO company_settings (setting_name, setting_value, updated_by) VALUES 
('office_lat', '13.0827', 'admin'),
('office_lon', '80.2707', 'admin'),
('office_address', 'CGS Green Sustainergy, Anna Salai, Teynampet, Chennai, Tamil Nadu 600018, India'),
('office_radius', '200');

-- 5. Optional: Update existing employees to have explicit work modes
-- (Uncomment and run if you want all existing employees to be 'Office' workers)
-- UPDATE users SET work_mode = 'Office' WHERE role = 'employee';

-- 6. Verify the changes
SELECT 'Users table structure:' as info;
DESCRIBE users;

SELECT 'Company settings:' as info;
SELECT * FROM company_settings;

SELECT 'Site visits table structure:' as info;
DESCRIBE site_visits;

-- ===================================================================
-- Migration Complete - Your database is now ready for the new system
-- ===================================================================