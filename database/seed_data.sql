-- =============================================================================
-- SIH26099: Seed Data for PostgreSQL Database (sih26099)
-- Pre-seeds: Participating CPSEs, Prototype Canonical Materials (NMM-000001 - NMM-000008),
-- Initial Users, and Commodity Taxonomies.
-- =============================================================================

-- Seed CPSE Organizations
INSERT INTO cpse (code, name, sector) VALUES
('ONGC', 'Oil and Natural Gas Corporation Limited', 'Oil & Gas Exploration'),
('IOCL', 'Indian Oil Corporation Limited', 'Refining & Marketing'),
('BHEL', 'Bharat Heavy Electricals Limited', 'Heavy Engineering & Power'),
('NTPC', 'NTPC Limited', 'Power Generation'),
('SAIL', 'Steel Authority of India Limited', 'Steel Manufacturing'),
('GAIL', 'GAIL (India) Limited', 'Natural Gas Transmission')
ON CONFLICT (code) DO NOTHING;

-- Seed Enterprise Users
INSERT INTO users (employee_id, name, email, password_hash, role, cpse_name, is_active, status) VALUES
('ADM001', 'Dr. Rajesh Sharma (Director General)', 'admin@cpse-harmonization.gov.in', '$2b$10$zghlEeJ/lOHWxhfmZehFMureXByeU7bP9EAqHeY/4E485zFK4egve', 'ADMIN', 'CPSE_CONSORTIUM', TRUE, 'ACTIVE'),
('REV001', 'P. Venkatraman (Chief Technical Auditor)', 'audit.officer@cpse.gov.in', '$2b$10$8Z9XlzDUNzzh75Jw3mtyLe4u8GcFPhKVFszii7aF8EkpsYjOxCbqi', 'REVIEWER', 'GOVERNMENT_AUDIT', TRUE, 'ACTIVE'),
('USR001', 'S. Ananya (Material Procurement Officer)', 'procurement@ongc.co.in', '$2b$10$tikEiqNSAjIcr7Y7ze94OuFOmhhRz5HcllNc9JCoVVcizmAaEFEl2', 'OFFICER', 'ONGC', TRUE, 'ACTIVE'),
('USR002', 'Vikram Malhotra (Senior Engineer - Stores)', 'procurement@bhel.in', '$2b$10$tikEiqNSAjIcr7Y7ze94OuFOmhhRz5HcllNc9JCoVVcizmAaEFEl2', 'OFFICER', 'BHEL', TRUE, 'ACTIVE')
ON CONFLICT (employee_id) DO NOTHING;


-- Seed Taxonomies
INSERT INTO taxonomy (code, name, level, description) VALUES
('FASTENERS', 'Industrial Fasteners & Hardware', 1, 'Bolts, nuts, studs, washers, screws'),
('PIPING', 'Pipes, Tubes & Fittings', 1, 'Seamless pipes, ERW pipes, flanges, elbows'),
('ELECTRICAL', 'Electrical Equipment & Switchgear', 1, 'Transformers, motors, circuit breakers, cables'),
('VALVES', 'Industrial Valves', 1, 'Ball valves, gate valves, check valves, globe valves')
ON CONFLICT (code) DO NOTHING;

-- Seed Prototype Canonical Materials (NMM-000001 through NMM-000008)
INSERT INTO canonical_materials (
    national_material_code, canonical_code, standardized_description,
    canonical_description, category, material_type, standard_specification, standard_uom, approval_status
) VALUES
(
    'NMM-000001', 'NMM-000001',
    'Hex Head Bolt M10 x 50 mm, Stainless Steel Grade SS304 / A2-70, Full Thread DIN 933 / ISO 4017',
    'Hex Head Bolt M10 x 50 mm, Stainless Steel Grade SS304 / A2-70, Full Thread DIN 933 / ISO 4017',
    'Fasteners & Hardware', 'Consumable / Standard Part', 'DIN 933 / ISO 4017 / IS 1364', 'EA', 'APPROVED'
),
(
    'NMM-000002', 'NMM-000002',
    'Hex Head Bolt M10 x 50 mm, High Tensile Alloy Steel Grade 8.8, Zinc Plated DIN 933',
    'Hex Head Bolt M10 x 50 mm, High Tensile Alloy Steel Grade 8.8, Zinc Plated DIN 933',
    'Fasteners & Hardware', 'Consumable / Standard Part', 'DIN 933 / ISO 4017', 'EA', 'APPROVED'
),
(
    'NMM-000003', 'NMM-000003',
    'Seamless Carbon Steel Pipe 2 Inch Nominal Bore, Schedule 40, ASTM A106 Grade B / API 5L Gr. B',
    'Seamless Carbon Steel Pipe 2 Inch Nominal Bore, Schedule 40, ASTM A106 Grade B / API 5L Gr. B',
    'Piping & Flow Components', 'Raw Material / Piping', 'ASTM A106-B / API 5L Gr. B / ASME B36.10M', 'MTR', 'APPROVED'
),
(
    'NMM-000004', 'NMM-000004',
    'Forged Carbon Steel Weld Neck Flange 2 Inch NB, Class 150, Raised Face (RF), ASTM A105',
    'Forged Carbon Steel Weld Neck Flange 2 Inch NB, Class 150, Raised Face (RF), ASTM A105',
    'Piping & Flow Components', 'Piping Component', 'ASME B16.5 / ASTM A105', 'EA', 'APPROVED'
),
(
    'NMM-000005', 'NMM-000005',
    'Three-Phase Squirrel Cage Induction Motor 15 kW (20 HP), 4-Pole 1460 RPM, 415V 50Hz, Frame 160L IE3',
    'Three-Phase Squirrel Cage Induction Motor 15 kW (20 HP), 4-Pole 1460 RPM, 415V 50Hz, Frame 160L IE3',
    'Electrical Equipment & Motors', 'Capital / Rotating Equipment', 'IS 12615 / IEC 60034-30 IE3 Efficiency', 'EA', 'APPROVED'
),
(
    'NMM-000006', 'NMM-000006',
    'Single Row Deep Groove Ball Bearing 6205-2RS, Bore 25 mm, OD 52 mm, Width 15 mm, Rubber Sealed',
    'Single Row Deep Groove Ball Bearing 6205-2RS, Bore 25 mm, OD 52 mm, Width 15 mm, Rubber Sealed',
    'Bearings & Power Transmission', 'Spare Part', 'ISO 15 / DIN 625', 'EA', 'APPROVED'
),
(
    'NMM-000007', 'NMM-000007',
    'Three-Piece Trunnion Mounted Ball Valve 2 Inch NB Class 300, Stainless Steel SS316 Body/Trim, Flanged RF',
    'Three-Piece Trunnion Mounted Ball Valve 2 Inch NB Class 300, Stainless Steel SS316 Body/Trim, Flanged RF',
    'Valves & Actuators', 'Mechanical Component', 'API 6D / ASME B16.34', 'EA', 'APPROVED'
),
(
    'NMM-000008', 'NMM-000008',
    'Heavy Hexagon Nut M10, Stainless Steel Grade SS304 / A2-70, Metric Coarse Thread DIN 934 / ISO 4032',
    'Heavy Hexagon Nut M10, Stainless Steel Grade SS304 / A2-70, Metric Coarse Thread DIN 934 / ISO 4032',
    'Fasteners & Hardware', 'Consumable / Standard Part', 'DIN 934 / ISO 4032 / IS 1364', 'EA', 'APPROVED'
)
ON CONFLICT (national_material_code) DO NOTHING;

-- Initial System Audit Log Event
INSERT INTO audit_logs (action, entity_type, entity_id, performed_by, reason, "user")
VALUES (
    'SYSTEM_BOOTSTRAP',
    'database',
    'sih26099_pg',
    'SYSTEM_INSTALLER',
    'Database initialized with enterprise schema and seed taxonomies.',
    'SYSTEM_INSTALLER'
);
