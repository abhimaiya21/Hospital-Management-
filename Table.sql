-- 1. Patients Table
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10),
    contact_number VARCHAR(15),
    address TEXT
);

-- 2. Doctors Table
CREATE TABLE doctors (
    doctor_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(50) NOT NULL, -- e.g., Cardiology, Pediatrics
    email VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Appointments Table
-- This acts as a Junction Table for the Many-to-Many relationship between Doctors and Patients
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    doctor_id INT REFERENCES doctors(doctor_id),
    appointment_date TIMESTAMP NOT NULL,
    reason_for_visit TEXT,
    status VARCHAR(20) DEFAULT 'Scheduled' -- e.g., Scheduled, Completed, Cancelled
);

-- 4. Medical Records Table
-- Stores clinical notes and diagnoses. Linked to both patient and doctor.
CREATE TABLE medical_records (
    record_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    doctor_id INT REFERENCES doctors(doctor_id),
    diagnosis TEXT NOT NULL,
    treatment_plan TEXT,
    record_date DATE DEFAULT CURRENT_DATE
);

-- 5. Allergies Table
-- One-to-Many: One patient can have multiple allergies
CREATE TABLE allergies (
    allergy_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    allergen VARCHAR(100) NOT NULL, -- e.g., Penicillin, Peanuts
    severity VARCHAR(20) CHECK (severity IN ('Mild', 'Moderate', 'Severe', 'Life-Threatening'))
);

-- INSERT DOCTORS
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Allison Hill', 'Neurology', 'allison.hill@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Noah Rhodes', 'Dermatology', 'noah.rhodes@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Angie Henderson', 'Oncology', 'angie.henderson@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Daniel Wagner', 'General Practice', 'daniel.wagner@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Cristian Santos', 'Cardiology', 'cristian.santos@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Connie Lawrence', 'Oncology', 'connie.lawrence@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Abigail Shaffer', 'Cardiology', 'abigail.shaffer@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Gina Moore', 'Oncology', 'gina.moore@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Gabrielle Davis', 'General Practice', 'gabrielle.davis@hospital.com');
INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. Ryan Munoz', 'Neurology', 'ryan.munoz@hospital.com');

-- INSERT PATIENTS
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Monica Herrera', '1986-07-03', 'Male', '584-695-9310', 'Unit 3164 Box 7525, DPO AA 27961');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Mia Sutton', '1944-09-13', 'Female', '+1-528-232-7648', '1395 Diana Locks Suite 242, Lake Anna, KS 98413');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Stephanie Ross', '1964-10-31', 'Male', '(387)810-1226', '480 Erin Plain Suite 514, Mooretown, VA 94830');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Jonathan White', '1949-06-19', 'Male', '+1-948-293-2528', '3039 Christopher Oval Apt. 822, Arroyoburgh, KS 69664');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Jenny Lewis', '2008-05-19', 'Female', '001-534-565-787', '10518 Joshua Oval, New David, FM 75348');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Dana Kennedy', '1990-05-21', 'Female', '311.265.6670', '33387 Robert Harbors Suite 317, North Deniseside, MP 02435');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Tammy Allison', '1957-08-14', 'Male', '(977)436-0260x6', '98050 Breanna Parkway, North Susan, CO 24857');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Barry Hensley', '1989-12-08', 'Female', '793-699-0916', '46247 Hickman Cliffs Apt. 799, North Amandahaven, KS 17862');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Shirley Suarez', '1985-04-11', 'Male', '327-384-9808x41', '4935 Grace Walk, Williamview, MH 07159');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Jeff Hill', '1935-06-20', 'Female', '724-427-8680x11', '5053 Elizabeth Knoll, Dicksonberg, IA 21800');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Rita Keith', '1938-05-11', 'Male', '(956)534-2160', '4330 Raymond Harbors Apt. 458, Frazierside, MA 04118');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Wesley White', '1971-02-11', 'Female', '3198655698', 'PSC 3406, Box 0883, APO AA 57032');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Matthew Rivera', '1977-09-15', 'Male', '+1-414-684-6564', '4369 Marshall Mills, New Thomas, MH 96964');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Bradley Robertson', '2021-02-15', 'Female', '+1-351-934-3320', '676 Dylan Spurs, Port Michelleville, WI 56225');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Robert Dominguez', '1998-03-17', 'Male', '7839172788', '727 Green Gateway Suite 873, Scottport, IA 36115');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Steven Miller', '1955-07-06', 'Female', '962.831.6658', '9096 Smith Knoll Suite 668, South Jeffrey, NE 64155');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('George Shelton', '1990-01-04', 'Female', '001-427-929-806', '5375 Juarez Light Suite 641, Smithside, AR 46371');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Barry Bernard', '1940-06-18', 'Female', '001-603-730-923', '41904 Sanders Stravenue, North Brittany, MP 82714');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Michael Turner', '2016-09-12', 'Female', '790-258-6518', '65726 Jessica Run Suite 987, Grahamshire, KY 42746');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Sandra Miller', '1996-05-03', 'Male', '479.996.5075', '4948 Zachary Field Apt. 367, Lake Thomas, VT 64833');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Alan Phillips', '1990-01-08', 'Female', '001-734-995-788', '13518 James Streets Suite 498, Tinaborough, LA 30317');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Eric Erickson', '1952-03-18', 'Female', '900-984-2710x94', '7116 Jones Roads, East Edwardshire, ME 11665');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Bailey Duran DDS', '2019-02-24', 'Male', '286.377.4964', 'USNS Garrett, FPO AA 87064');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('David Arnold', '1956-04-15', 'Female', '6679974034', '9361 Deborah Grove, North Brian, WY 40820');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Samantha Morse', '1994-10-02', 'Male', '374-264-8877', '401 Suzanne Villages Apt. 490, South April, NV 36959');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Kevin Walters', '2001-11-27', 'Female', '875-965-5125', '071 King Crescent Suite 808, Gutierrezborough, NC 47920');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Kathleen Ramos', '1942-01-03', 'Female', '548.424.7710', '613 Steven Crest, South Sarah, LA 67199');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Jennifer Olson', '1999-04-03', 'Male', '378.626.3982', '8404 Monroe Prairie Suite 278, Reedside, WV 71729');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Timothy Kane', '1967-06-27', 'Female', '001-463-960-576', 'Unit 2895 Box 1718, DPO AA 02512');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Jennifer Pena', '1955-12-29', 'Female', '874-759-6158', '091 Crystal Heights Apt. 161, South Garrettport, MH 04295');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Robert Carter', '1985-12-31', 'Female', '(923)486-9222x1', '4074 Charles Key Suite 647, Jamesfurt, PR 63836');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('James Howard', '1975-04-02', 'Male', '001-740-564-090', '210 Kramer Bypass Suite 214, Julieburgh, ID 17823');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Sherri Diaz', '2003-04-12', 'Male', '724-374-5171x23', '8175 Richards View, Danielbury, NJ 03781');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Terri Murphy', '2018-01-06', 'Male', '617.946.1200', '267 Santiago Summit, Matthewsberg, FM 54880');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Sandra Gilbert', '1973-01-20', 'Female', '7532773515', '71390 Kristin Gardens, Port Anne, CA 73142');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Daniel Kane', '1979-09-13', 'Female', '001-729-504-228', '40268 Julie Mountains, Stricklandhaven, OR 14794');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Daniel Gilbert', '2024-08-29', 'Female', '447.300.7661x77', '9847 Garcia Squares Apt. 836, Beasleychester, MA 59942');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Nicholas Edwards', '1977-07-08', 'Female', '+1-245-727-1111', '6049 Bell Ports Apt. 273, West Meganstad, DE 37013');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Renee Bruce', '2019-08-08', 'Male', '+1-480-494-0244', '20183 Barnes Junctions Apt. 545, North Ericton, TX 11194');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Matthew Tucker', '1995-02-23', 'Male', '(543)881-5614x9', 'Unit 0034 Box 3244, DPO AA 16227');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Paul Thompson', '1986-09-24', 'Male', '+1-238-985-1606', 'PSC 5969, Box 6641, APO AA 03234');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Carolyn Meza', '1997-08-08', 'Female', '001-651-761-369', '81883 Bell Viaduct, East Curtis, KS 26357');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Christian Malone', '1945-03-28', 'Female', '(777)499-7995', '4490 Romero Inlet Suite 700, Marieland, SD 12336');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Katie Ford', '2010-06-05', 'Male', '001-707-393-597', '37788 Michael Haven, Ortizmouth, TX 78867');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Mark Cook', '1979-11-09', 'Female', '486-744-9251', '91486 Li Skyway Apt. 685, West Kyleborough, MA 64237');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Zachary Moore', '1975-03-29', 'Female', '888-480-5929', '706 Rhodes Freeway, Bishopmouth, IN 70494');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Vincent Mueller', '1961-05-22', 'Male', '(497)674-6886x2', '8181 Miller Estates Suite 782, Davisbury, GU 59631');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Tara Perry', '1988-12-09', 'Female', '653.961.5305x15', '779 Rebecca Brook, Jasonberg, OH 95821');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Jenny Parsons', '1967-04-30', 'Male', '510-436-9711x79', '539 Lopez Skyway, New Theresaland, NC 71814');
INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('Virginia Spencer', '1988-02-15', 'Male', '406.254.0515x31', '277 Lisa Circles Suite 043, Port Jameston, MD 41143');

-- INSERT ALLERGIES
INSERT INTO allergies (patient_id, allergen, severity) VALUES (34, 'Penicillin', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (15, 'Dust Mites', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (6, 'Dust Mites', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (48, 'Penicillin', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (6, 'Shellfish', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (47, 'Pollen', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (4, 'Shellfish', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (27, 'Peanuts', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (26, 'Peanuts', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (13, 'Penicillin', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (31, 'Penicillin', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (21, 'Shellfish', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (17, 'Latex', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (5, 'Latex', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (8, 'Latex', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (5, 'Pollen', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (9, 'Peanuts', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (41, 'Penicillin', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (49, 'Latex', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (15, 'Peanuts', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (6, 'Latex', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (35, 'Sulfa Drugs', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (5, 'Pollen', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (25, 'Dust Mites', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (16, 'Shellfish', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (26, 'Penicillin', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (40, 'Sulfa Drugs', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (27, 'Pollen', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (6, 'Pollen', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (12, 'Shellfish', 'Life-Threatening');

-- INSERT APPOINTMENTS
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (32, 1, '2025-07-14 12:14:22', 'Writer myself education send course ground.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (11, 9, '2025-10-25 14:29:14', 'Tend forward buy.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (30, 6, '2025-05-18 06:42:13', 'Threat sea thus hit wind many.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (45, 10, '2025-07-07 13:46:13', 'Under mind song risk bad own.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (31, 4, '2025-11-10 17:17:33', 'Nation fly bag produce.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (25, 2, '2025-04-24 09:15:53', 'Owner international ready goal amount thank good.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (34, 3, '2025-06-13 06:27:20', 'Police social arm provide image.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (22, 5, '2025-07-13 14:49:28', 'Well central parent sit.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (44, 4, '2025-01-08 20:51:58', 'Attack sing hand him.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (25, 5, '2025-08-03 15:37:10', 'Painting quickly we.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (45, 6, '2025-05-19 19:55:56', 'Several off morning huge power economic.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (38, 3, '2025-02-08 09:56:02', 'Save material hit.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (21, 3, '2025-08-01 11:41:07', 'Energy employee land you.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (24, 4, '2025-04-16 06:17:08', 'Customer career available common require young specific.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (39, 2, '2025-11-19 17:20:43', 'Property remember nearly face feel church.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (49, 10, '2025-09-27 22:07:48', 'Soldier meeting building cut.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (15, 6, '2025-02-18 06:56:33', 'So ago network hard sound.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (34, 9, '2025-07-28 14:14:18', 'Partner beat finally yourself.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (12, 4, '2025-10-01 12:52:02', 'Moment shoulder statement available win politics last.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (30, 5, '2025-09-16 11:35:29', 'General there sister policy consider whom item.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (29, 6, '2025-12-15 00:58:11', 'Story million fight class.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (43, 9, '2025-12-24 08:54:16', 'Generation wait thus suffer economy.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (45, 4, '2025-08-29 23:40:38', 'Ever person pass behavior political option oil.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (9, 8, '2025-03-02 20:13:18', 'Result painting successful nor stay agreement animal political.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (39, 3, '2025-08-07 08:24:50', 'Prepare short indicate police marriage.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (30, 5, '2025-08-26 22:06:31', 'Face what lot source rate father authority.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (26, 9, '2025-01-18 14:56:46', 'Keep machine daughter parent.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (45, 2, '2025-04-26 17:59:47', 'Safe team wish candidate have no.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (31, 8, '2025-04-29 06:53:31', 'Letter environment easy best face.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (11, 7, '2025-05-24 13:03:08', 'Industry while total spend value return couple city.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (39, 9, '2025-07-14 06:05:58', 'Material final age war measure whom Democrat.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (22, 10, '2025-05-12 09:44:13', 'Anything manager think.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (33, 6, '2025-09-06 10:39:42', 'Experience account blue care enough hand idea.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (30, 1, '2025-01-12 22:12:21', 'Anything no guy eye hit late.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (48, 9, '2025-07-27 21:33:21', 'Stay perhaps particularly campaign benefit.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (16, 6, '2025-05-20 06:58:37', 'Newspaper hand certain own husband American.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (13, 10, '2025-01-10 11:13:15', 'Require sound mind chance.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (47, 9, '2025-12-08 05:06:25', 'Cause use five hotel pattern successful order.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (6, 3, '2025-07-11 09:02:05', 'Mother remember feel staff happy purpose woman.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (9, 2, '2025-08-10 01:00:52', 'Someone rise read ago listen.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (15, 5, '2025-09-06 23:04:01', 'Officer return on color pick people subject challenge.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (39, 4, '2025-09-16 17:21:03', 'All way body affect finish.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (2, 5, '2025-02-23 03:57:28', 'Real improve simple turn their save.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (4, 7, '2025-01-19 13:01:12', 'Million night your long.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (19, 5, '2025-05-21 16:46:40', 'What least mouth national put test.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (37, 10, '2025-09-16 17:31:40', 'Particular court east newspaper different.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (44, 5, '2025-04-20 22:29:06', 'Relate real major look night.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (43, 1, '2025-12-24 06:33:05', 'Explain of myself time house.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (32, 10, '2025-05-09 09:24:16', 'Fact explain research get.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (28, 6, '2025-06-16 03:45:38', 'Section degree still even no.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (16, 1, '2025-04-10 20:12:43', 'Body scientist dream anything.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (35, 8, '2025-12-12 21:26:40', 'Difficult do beyond form line race case.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (8, 4, '2025-07-28 02:10:26', 'Imagine various there local.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (45, 3, '2025-03-13 19:34:50', 'Fly position traditional become off.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (41, 3, '2025-07-22 04:29:49', 'Tree company think.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (25, 7, '2025-03-04 14:59:09', 'Young however many.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (33, 8, '2025-12-25 02:20:33', 'Theory across nothing blue work.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (41, 6, '2025-04-15 20:49:23', 'Writer myself management voice surface life cover.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (45, 8, '2025-02-08 02:27:37', 'Class learn either control say so.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (49, 10, '2025-08-03 20:37:15', 'Compare task today still middle.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (45, 7, '2025-01-29 00:58:15', 'Protect continue cell food easy end.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (24, 1, '2025-03-27 19:44:00', 'Send west few reveal activity president realize.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (21, 9, '2025-01-19 11:33:25', 'Let civil rather type.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (10, 1, '2025-12-06 03:25:31', 'Real police wait happen determine.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (21, 8, '2025-02-16 05:28:03', 'Check security paper indeed near likely Mr.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (38, 8, '2025-09-10 06:19:30', 'Seven quite other skin moment.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (28, 6, '2025-07-19 11:26:48', 'Back nor article natural measure of.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (36, 3, '2025-02-22 13:14:30', 'Foreign minute break day.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (26, 5, '2025-08-09 19:50:48', 'Before member speak law message lead around.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (38, 9, '2025-06-23 22:11:40', 'Rich how staff second official.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (50, 4, '2025-01-12 22:38:52', 'General as yes various attorney value.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (35, 6, '2025-01-07 16:18:24', 'Important shoulder she within position.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (25, 7, '2025-06-07 14:34:25', 'Year him thank trade heart radio.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (20, 7, '2025-09-09 08:52:11', 'Card team budget year hotel camera without.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (38, 5, '2025-11-15 13:37:04', 'Series without leg.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (4, 5, '2025-10-01 14:57:28', 'Interest here discover leave choice country themselves.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (24, 4, '2025-10-19 15:23:58', 'Allow produce past view.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (38, 4, '2025-12-06 14:58:56', 'Drive attack order.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (46, 3, '2025-06-17 17:38:55', 'Public the each analysis keep music senior simply.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (36, 1, '2025-02-18 18:40:28', 'Year doctor trouble office officer significant stand.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (37, 6, '2025-03-28 08:37:19', 'Then worry miss including every.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (25, 3, '2025-07-30 13:30:19', 'They treatment personal interview many win walk provide.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (14, 7, '2025-10-27 12:44:45', 'Five indicate chance heavy senior list support.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (29, 9, '2025-04-22 03:34:58', 'South trip none whose.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (47, 10, '2025-07-30 18:48:19', 'Care drug data position two suggest begin.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (28, 7, '2025-10-03 18:08:07', 'Appear help painting always authority.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (22, 8, '2025-11-03 20:24:13', 'Right next look thank four whatever address view.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (40, 5, '2025-10-10 07:33:58', 'Section senior trial receive.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (25, 4, '2025-09-25 16:06:54', 'However dream focus executive letter.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (6, 1, '2025-09-04 07:02:15', 'Final growth third letter sort reveal.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (16, 5, '2025-10-18 03:24:46', 'Trial have including none determine certainly.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (13, 2, '2025-04-06 15:06:26', 'Various often individual charge form here street.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (4, 8, '2025-07-08 06:20:36', 'Pressure range either start whom politics make.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (4, 10, '2025-03-01 16:34:03', 'College result major true my politics.', 'No Show');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (16, 1, '2025-01-18 03:56:19', 'Almost suggest war property share include successful.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (41, 10, '2025-03-26 05:37:55', 'Religious across media health.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (46, 4, '2025-08-23 07:09:29', 'Tree process administration mother in admit reveal movie.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (28, 3, '2025-04-16 16:38:50', 'Maybe recently issue.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (30, 4, '2025-12-26 07:15:58', 'Blood benefit chance court.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES (31, 1, '2025-07-18 19:26:30', 'Spring environment however health image.', 'Scheduled');

-- INSERT MEDICAL RECORDS
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (4, 1, 'During recently feel stock ball.', 'Behavior here need argue act.', '2025-03-01');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (14, 10, 'Matter its.', 'Not teach believe month amount deep test thought.', '2025-06-27');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (32, 8, 'Another avoid understand.', 'Nor allow up fire which onto sell require huge baby.', '2025-02-26');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (50, 6, 'Drive strong home to forward.', 'So ready bad seat generation best.', '2025-03-25');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 1, 'Future shoulder.', 'However similar ahead event yeah make green wait it quickly.', '2025-09-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (28, 4, 'Beat peace something require.', 'Environmental here six child hope.', '2025-05-14');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (31, 3, 'Before wall.', 'Growth especially car cost large never impact ago government.', '2025-01-30');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (42, 4, 'Our foot history factor hold.', 'Right nice yeah drug minute.', '2025-09-17');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (28, 5, 'College especially environmental certainly.', 'Itself inside machine baby edge east.', '2025-08-24');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (42, 1, 'Order crime blood fight.', 'Forward per sound forget friend spring teacher wind.', '2025-02-15');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 2, 'Fly water cut.', 'Concern huge five same plan whose site for.', '2025-04-12');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (6, 9, 'Half usually customer young.', 'Race nearly well left remain just.', '2025-04-17');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (6, 3, 'Standard somebody.', 'Pull cause field education child institution help last.', '2025-08-14');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (41, 10, 'Old move type thank.', 'Myself so growth time Mr point be shoulder price.', '2025-05-11');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (33, 4, 'Positive and worker.', 'Whom former someone black better develop section newspaper.', '2025-09-18');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (44, 3, 'Determine hear leg quickly real.', 'General agency bit indeed which break.', '2025-12-25');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (42, 7, 'Give gas six.', 'Lot live just recent five feel special boy support possible.', '2025-09-13');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (42, 4, 'Upon scientist might.', 'Civil nice when discussion if continue policy it ahead pass.', '2025-03-11');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (22, 3, 'Or home relate day.', 'Officer son Mr hand culture.', '2025-02-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (29, 8, 'Provide majority whole.', 'Others particularly only girl suddenly pay sport relationship.', '2025-04-19');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (1, 8, 'Opportunity public finish draw bring.', 'Really memory industry case himself control player really.', '2025-09-01');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (9, 6, 'Never majority cell.', 'Success people tend weight machine crime himself no.', '2025-09-04');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (43, 9, 'Important man report kitchen.', 'Bar air set factor ever Mrs.', '2025-02-28');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 2, 'Not significant manager member.', 'Box simple statement happen state among rest national wrong bill.', '2025-11-12');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (19, 10, 'Fear yourself last.', 'Television beautiful tend bring speech decide scene ready.', '2025-11-24');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (21, 8, 'Plan coach cause deal deal.', 'Now mother others collection without.', '2025-04-17');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (18, 5, 'Of weight method.', 'Career seek in arrive everyone.', '2025-09-05');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (33, 7, 'Reduce car chair.', 'Stock seven put majority officer environmental increase later.', '2025-08-28');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (14, 4, 'Idea seek.', 'Lawyer maintain old than suggest behavior will play.', '2025-09-21');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 4, 'Sure somebody huge why.', 'Manager follow exist natural candidate system.', '2025-10-27');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (38, 6, 'Thus several animal phone.', 'Administration upon citizen lead yeah into yet travel think.', '2025-04-21');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (50, 10, 'Themselves theory behavior.', 'Economy head tough close how figure record doctor.', '2025-09-05');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (7, 8, 'Region ability.', 'Back order mind knowledge account gas building team really.', '2025-06-28');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (10, 2, 'Director become.', 'Billion happen federal him spend.', '2025-11-29');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (1, 10, 'Political quality attention.', 'Across practice key reveal physical character in rather team beautiful.', '2025-02-02');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (15, 2, 'Sell operation himself.', 'Fire cause everybody base network outside parent single real.', '2025-11-19');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (34, 8, 'Day parent country.', 'Far approach today west manager both matter order.', '2025-07-18');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (12, 6, 'Would value.', 'Hit stuff inside national common likely.', '2025-10-20');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (40, 1, 'Admit attack.', 'Democratic two we huge expert Republican short.', '2025-06-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (24, 8, 'Bar Mr pattern everyone.', 'Bad TV window choice force only shake.', '2025-09-03');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (43, 9, 'Financial join.', 'Around beat its law participant finally score.', '2025-10-08');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (2, 10, 'Budget remain reduce.', 'Market get military state else head.', '2025-10-12');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (9, 5, 'Run brother tonight.', 'Southern evening ask Republican office baby lawyer growth.', '2025-07-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (23, 7, 'Cold church significant thus purpose.', 'Direction meeting analysis television each.', '2025-06-26');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (30, 1, 'Him change use tax.', 'Sort research pretty different eat trouble floor step number budget.', '2025-09-12');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (2, 1, 'Conference source.', 'West attention let executive suddenly.', '2025-05-01');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (5, 10, 'Network account.', 'Factor six science drug happy will.', '2025-10-21');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (28, 2, 'Run national somebody.', 'According improve do get style theory.', '2025-05-04');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (42, 5, 'Serve heavy.', 'Billion morning draw man art young Republican.', '2025-01-30');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (24, 5, 'Tv today.', 'Including time learn security oil measure PM hour option artist.', '2025-09-08');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (22, 10, 'Door end fire.', 'Red save fish evening avoid dark sister once.', '2025-02-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (40, 6, 'Clearly letter.', 'Building group show later leg system bed space.', '2025-04-22');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (28, 1, 'American structure foreign before eat.', 'How any federal star community weight take new.', '2025-07-26');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (35, 6, 'Behind big soldier.', 'Activity store work candidate statement head.', '2025-08-26');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (29, 10, 'Old else.', 'Against ask total kitchen can.', '2025-12-11');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (14, 3, 'Business walk anything under.', 'Start house ahead raise common Democrat cost evidence third.', '2025-01-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 8, 'People early far include nearly.', 'Because him information poor something.', '2025-03-31');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (14, 9, 'Yes myself affect him require.', 'Name machine tree maybe home conference five despite time.', '2025-10-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (48, 8, 'Around yard morning.', 'Yourself wind beyond prevent entire staff true argue you detail.', '2025-11-18');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (43, 2, 'Great stuff suddenly compare.', 'Fish scene grow option region goal nothing center way student.', '2025-11-04');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (40, 4, 'My compare also argue.', 'Despite money a truth cut candidate response try such food.', '2025-01-02');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (23, 3, 'Only true similar.', 'Team whether health walk how big few carry church we.', '2025-10-28');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (4, 8, 'Power company why really.', 'Skin development open compare fill read camera rock we we hot.', '2025-10-20');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (48, 2, 'Allow own TV whose determine.', 'Bit many former back get floor player white start prove.', '2025-10-04');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (39, 2, 'Land enter economic attack.', 'Skin result answer just information coach increase.', '2025-12-02');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (40, 5, 'Goal heart stock small.', 'Prepare reach class available suffer far five weight avoid color.', '2025-05-19');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (45, 5, 'Rule natural together.', 'Full world throw relate issue.', '2025-09-04');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (22, 7, 'Parent its approach.', 'Day couple recent reveal role enter example down.', '2025-01-13');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (23, 1, 'Occur style child guess.', 'Because station person lose best deal point with list.', '2025-02-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (9, 1, 'Size likely thus.', 'Before name continue those hard knowledge enjoy.', '2025-06-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (48, 4, 'Difficult environmental article.', 'Beat gas must wife operation.', '2025-07-27');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (47, 5, 'Subject stand.', 'Whole reach view of dog federal house take alone.', '2025-08-03');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (48, 3, 'Song quality per build serious.', 'We cold deep cover amount bad.', '2025-09-16');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (35, 10, 'Dark state challenge organization.', 'Treat trial attack hold however for everybody leader.', '2025-11-29');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (28, 6, 'Skill performance.', 'Site both change note old who beyond black single size.', '2025-11-26');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (8, 1, 'They there enough pressure occur.', 'Also every century participant really although threat former down.', '2025-10-10');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (15, 4, 'Tv today after stage.', 'Financial successful teach range win direction feel.', '2025-10-09');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (19, 1, 'Similar fly rock painting.', 'Could deep station scientist service.', '2025-11-26');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (17, 3, 'Start middle city find.', 'Idea sister modern notice community themselves customer arm almost.', '2025-01-13');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (47, 6, 'Relate ever statement measure.', 'Race drop major land whether listen.', '2025-07-27');
