DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS allergies CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS doctors CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ==========================================
-- 2. CREATE TABLES
-- ==========================================

-- A. USERS TABLE (For Login System)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL, 
    role VARCHAR(20) NOT NULL CHECK (role IN ('doctor', 'nurse', 'billing'))
);

-- B. DOCTORS TABLE
CREATE TABLE doctors (
    doctor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialty VARCHAR(50) NOT NULL, -- e.g. Cardiology
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_contact VARCHAR(15) -- Added: To contact the doctor
);

-- C. PATIENTS TABLE
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10),
    contact_number VARCHAR(15),
    address TEXT,
    insurance_provider VARCHAR(100) -- Added: Useful for Billing
);

-- D. APPOINTMENTS TABLE
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id),
    doctor_id INT REFERENCES doctors(doctor_id),
    appointment_date TIMESTAMP NOT NULL,
    room_number VARCHAR(10), -- Added: "Ward_No" logic
    reason_for_visit TEXT,
    status VARCHAR(20) DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Completed', 'Cancelled'))
);

-- E. MEDICAL RECORDS TABLE (Clinical Notes)
CREATE TABLE medical_records (
    record_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    doctor_id INT REFERENCES doctors(doctor_id),
    diagnosis TEXT NOT NULL,
    treatment_plan TEXT,
    record_date DATE DEFAULT CURRENT_DATE
);

-- F. ALLERGIES TABLE (Weak Entity)
CREATE TABLE allergies (
    allergy_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    allergen VARCHAR(100) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('Mild', 'Moderate', 'Severe', 'Life-Threatening'))
);

-- G. INVOICES TABLE (New! For the Billing Role)
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    amount DECIMAL(10, 2) NOT NULL, -- Money format
    status VARCHAR(20) DEFAULT 'Unpaid' CHECK (status IN ('Paid', 'Unpaid', 'Pending')),
    issue_date DATE DEFAULT CURRENT_DATE
);

INSERT INTO users (username, password, role) VALUES ('sanghvivincent', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('riaseth', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('ranveer64', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('krishnabahl', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('shenoyekantika', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('xshroff', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('tanvichopra', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('christopheredwin', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('alexander43', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('yashawini19', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('tamannakara', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('rajata36', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('lprashad', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('dhruv87', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('imangat', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('vohraojasvi', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('pillaybishakha', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('quincychaudhari', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('maneraagini', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('banikekalinga', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('waida12', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('deepjagdish', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('gnaik', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('wsolanki', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('hchowdhury', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('zborah', 'pass123', 'billing');
INSERT INTO users (username, password, role) VALUES ('skaul', 'pass123', 'nurse');
INSERT INTO users (username, password, role) VALUES ('umangjayaraman', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('othaker', 'pass123', 'doctor');
INSERT INTO users (username, password, role) VALUES ('nattamrita', 'pass123', 'nurse');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Faris', 'Palla', 'Orthopedics', 'swamyakshay@example.net', '+910381215160');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Viraj', 'Subramanian', 'Neurology', 'sachdevvictor@example.net', '9267073166');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Gaurangi', 'Sinha', 'Cardiology', 'hiteshpandit@example.com', '3315937321');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Balendra', 'Behl', 'Pediatrics', 'chaturasarin@example.net', '9267085269');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Vansha', 'Chaudhry', 'Orthopedics', 'ekiya77@example.org', '+918435331116');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Vasudha', 'Shroff', 'Orthopedics', 'krishna20@example.net', '07155633763');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Rayaan', 'Sidhu', 'Pediatrics', 'gavin12@example.com', '+911344287642');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Upasna', 'Thaman', 'Dermatology', 'chakrika20@example.net', '8288140102');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Robert', 'Issac', 'Pediatrics', 'wvenkataraman@example.com', '9269866710');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Ishanvi', 'Patla', 'Pediatrics', 'dsom@example.com', '00236456766');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Warjas', 'Savant', 'Dermatology', 'mitalshivansh@example.com', '0410186339');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Netra', 'Garde', 'Orthopedics', 'kalakrisha@example.org', '00147860028');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Aarna', 'Bhasin', 'Neurology', 'hpalan@example.org', '05973019766');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Anthony', 'Kadakia', 'Cardiology', 'jagdishpant@example.com', '3779767276');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Falguni', 'Saraf', 'Orthopedics', 'ladjonathan@example.net', '0254462610');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Advika', 'Chad', 'Dermatology', 'zkurian@example.com', '07424891272');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Vinaya', 'Bahri', 'Neurology', 'meera59@example.net', '07115105660');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Urishilla', 'Kota', 'Orthopedics', 'dadathomas@example.net', '0324081235');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Xavier', 'Raj', 'Cardiology', 'ibrahmbhatt@example.net', '+913148012878');
INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('Farhan', 'Nagarajan', 'Orthopedics', 'warinder55@example.com', '+912837046822');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Bakhshi', 'Choudhury', '1988-08-17', 'Other', '+919529215458', '20, Brar Street Vellore 064590', 'United Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Hamsini', 'Dey', '2006-03-19', 'Female', '06769285776', '34 Sarraf Circle, Bellary 116807', 'Aetna');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Ladli', 'Kohli', '1982-06-25', 'Male', '0144618690', 'H.No. 740, Sabharwal Ganj, Bijapur-881614', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Bhavini', 'Puri', '1946-10-11', 'Other', '+917814690074', '91/337 Srivastava Circle, Bhalswa Jahangir Pur 216573', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Upma', 'Subramaniam', '2004-03-03', 'Other', '6913848333', '00/261 Verma Street Dehradun 998910', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Chaaya', 'Bajaj', '1966-04-04', 'Female', '8807110579', 'H.No. 378, Behl Street, Avadi-801897', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Mitali', 'Dayal', '1982-08-27', 'Male', '+910356723767', '62/940, Bandi Zila, Howrah 105624', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Gautam', 'Vora', '2023-03-31', 'Male', '04443797486', '31, Atwal Ganj Ratlam-173685', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Manan', 'Om', '1940-06-11', 'Female', '06611852588', 'H.No. 06, Randhawa Circle, North Dumdum 094679', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Edhitha', 'Bal', '1986-12-05', 'Female', '0906608859', 'H.No. 296 Contractor Chowk, Farrukhabad 698913', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Xalak', 'Rajagopalan', '1958-12-18', 'Female', '0539656374', '30 Desai Street, Kavali 945910', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Lekha', 'Bansal', '1988-11-08', 'Female', '02897604885', '77 D’Alia Circle Hubli–Dharwad 472952', 'United Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Aryan', 'Srinivas', '2008-07-23', 'Male', '+910038611302', '15 Din Street, Madhyamgram-876073', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Rayaan', 'Prakash', '1996-09-25', 'Other', '+913698348101', 'H.No. 105, Talwar Thiruvananthapuram-840348', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Chameli', 'Talwar', '2020-07-23', 'Other', '2191054567', '74/285 Morar Nagar, Kolhapur 628992', 'Aetna');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Ekaraj', 'Nagi', '1984-01-03', 'Female', '+914666768884', '00 Dixit Chowk Allahabad 800448', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Udyati', 'Dar', '1999-07-06', 'Other', '+911282403560', '41/44, Ghosh Circle Amritsar 968944', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Osha', 'Sunder', '2024-08-17', 'Male', '4217286193', '48/112 Ranganathan Street, Siwan 479181', 'United Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Vrinda', 'Jani', '1952-12-16', 'Other', '8396315017', '60/398, Amble Street, Agartala-774287', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Dhruv', 'Natarajan', '2019-10-04', 'Other', '3380298403', '55/19, Raval Street Shahjahanpur-253588', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Gabriel', 'Merchant', '2023-10-20', 'Male', '3640909546', '389, Nagarajan Street Amaravati-472373', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Yashodhara', 'Balakrishnan', '1990-02-18', 'Female', '+917123159014', 'H.No. 71 Pai Marg, Patna-524330', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Januja', 'Kunda', '1977-10-22', 'Female', '2727983796', '814, Contractor Zila, Salem-965276', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Jyoti', 'Bakshi', '1977-01-18', 'Other', '05846136226', '97/73, Bhattacharyya Street, Bhusawal-124714', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Maya', 'Gera', '1996-11-22', 'Other', '+911164315837', '99/51, Shukla Street Gaya-101429', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Edhitha', 'Sahni', '1985-05-04', 'Male', '7038267903', '33/21, Rajagopalan Circle Moradabad-262640', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Tamanna', 'Nagarajan', '1969-10-21', 'Male', '8911172760', '76/66 Prabhu Zila, Tiruchirappalli 934885', 'Aetna');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Karan', 'Sangha', '1950-12-17', 'Male', '+910418981244', '36, Thakkar Zila, Agra 328742', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Chandresh', 'Kurian', '2016-02-22', 'Female', '01374594231', 'H.No. 99, Koshy Ganj, Bahraich-520836', 'United Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Vincent', 'Doctor', '1955-10-31', 'Other', '+913016715609', '083, Chaudhary Chowk, Anantapur-966599', 'United Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Alka', 'Gara', '1954-05-23', 'Female', '00375237691', '86 Sha Road Ajmer-273724', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Jeremiah', 'Chaudhari', '1944-11-15', 'Other', '+915091331377', '61, Sundaram Marg, Raiganj-563207', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Amol', 'Shan', '2001-09-29', 'Male', '09917324025', '78, Vyas Circle Jodhpur 283256', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Ojasvi', 'Kothari', '1946-03-16', 'Female', '+912821710669', '57 Korpal Mahbubnagar-495331', 'Aetna');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Jagrati', 'Venkataraman', '1937-07-14', 'Female', '+917058502639', 'H.No. 44 Sibal Road, Chandrapur 142489', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Unni', 'Parmer', '1944-10-25', 'Female', '0802509093', 'H.No. 61 Keer Path Rourkela-922235', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Chanchal', 'Chaudhari', '2020-01-16', 'Male', '04894921787', '617, Raghavan Road Dewas-932482', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Lavanya', 'Joshi', '1999-02-11', 'Female', '00741220099', '00/83 Anand Circle, Surendranagar Dudhrej 698075', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Utkarsh', 'Krishna', '1960-02-23', 'Male', '01033522182', '05 Muni Chowk Barasat-746565', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Madhav', 'Khalsa', '1954-10-15', 'Male', '5939200446', '32, Seth Street Kulti-441295', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Dev', 'Thaman', '1983-10-27', 'Female', '01495051011', '11/076 Khalsa Marg, Saharanpur 551593', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Vyanjana', 'Kalita', '1951-12-31', 'Other', '5859126773', '63, Lala Marg, Sangli-Miraj & Kupwad-457908', 'Aetna');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Krisha', 'Wason', '1960-07-17', 'Male', '6198468618', '694 Wason Nellore-560867', 'None');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Jhalak', 'Gola', '1979-10-12', 'Other', '+917357919888', 'H.No. 655, Manne Road, Anantapuram 166674', 'ICICI Lombard');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Yatin', 'Chada', '1951-10-21', 'Male', '+916973864492', '307, Dalal Street Nashik 864246', 'United Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Faqid', 'Deo', '2004-01-24', 'Male', '5845030270', '018, Viswanathan Nagar, Satara 070181', 'Aetna');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Yug', 'Sarkar', '1973-11-10', 'Other', '6212742015', 'H.No. 011 Kannan Chowk Haridwar-566453', 'United Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Yatan', 'Mander', '1955-05-04', 'Male', '9282510071', 'H.No. 85, Cherian, Mehsana 575136', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Harinakshi', 'Lall', '1998-03-13', 'Other', '05004106354', '910, Balay Path Bilaspur-934106', 'Star Health');
INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('Nimrat', 'Sidhu', '1984-10-31', 'Female', '0012073648', '243, Barad Nagar Chandrapur 249881', 'Star Health');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (45, 12, '2025-12-21 04:18:09', 'R-495', 'Ipsa vel ratione.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (26, 19, '2026-01-09 03:23:51', 'R-420', 'Molestiae maxime reiciendis totam.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (26, 18, '2026-01-22 01:03:39', 'R-187', 'Voluptate voluptatibus a.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (21, 13, '2025-12-02 09:30:10', 'R-128', 'Repellat laborum doloremque optio quos error consequuntur repellendus.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (18, 11, '2025-12-02 21:27:10', 'R-277', 'Et laboriosam recusandae rem impedit nihil.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (38, 8, '2026-01-21 02:35:07', 'R-211', 'Incidunt dolore soluta ad officiis nostrum ut.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (27, 16, '2026-01-11 00:13:42', 'R-599', 'Sint nobis at dolorum.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (19, 15, '2026-01-16 23:31:14', 'R-207', 'Maxime corporis cum numquam.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (11, 8, '2025-12-01 14:30:12', 'R-268', 'Blanditiis temporibus ex dolorum.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (2, 9, '2025-12-10 05:51:33', 'R-508', 'Occaecati iusto minus accusamus possimus voluptas aperiam dolor.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (7, 4, '2025-12-20 05:21:12', 'R-262', 'Magnam harum quod consequuntur consequatur alias.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (14, 16, '2026-01-24 00:12:39', 'R-565', 'Corporis culpa saepe ipsam ex.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (33, 3, '2025-12-28 15:50:05', 'R-196', 'Reprehenderit minus error beatae delectus doloribus quasi.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (49, 7, '2026-01-04 10:38:31', 'R-555', 'Recusandae praesentium quidem quis earum dignissimos facere.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (28, 9, '2025-12-27 10:11:37', 'R-535', 'Dolorum quis accusamus pariatur non illo cupiditate.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (42, 10, '2025-12-14 21:58:56', 'R-331', 'Beatae quasi dolore sunt voluptatibus iusto occaecati mollitia.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (50, 19, '2026-01-13 20:50:50', 'R-519', 'Molestias nesciunt eum eveniet repellat suscipit minus provident.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (29, 3, '2026-01-17 20:02:26', 'R-271', 'Itaque sint eveniet voluptas tempore occaecati.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (15, 17, '2025-12-29 08:54:16', 'R-112', 'Id in laudantium amet labore ullam quibusdam.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (45, 10, '2026-01-12 06:31:30', 'R-110', 'Quidem corporis animi laboriosam quas cumque.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (19, 20, '2026-01-23 17:49:44', 'R-439', 'Enim iure consequuntur repudiandae doloremque in fugit.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (20, 8, '2026-01-09 06:12:22', 'R-353', 'Error fuga mollitia adipisci.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (29, 19, '2026-01-18 23:58:22', 'R-426', 'Ad velit corrupti dicta.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (12, 8, '2026-01-09 13:33:37', 'R-326', 'Vero eius cum ratione.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (12, 19, '2025-12-24 09:36:57', 'R-552', 'Neque consequatur cupiditate asperiores enim eaque soluta.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (37, 6, '2026-01-19 03:55:41', 'R-235', 'Iure aperiam temporibus earum facilis cupiditate quasi quisquam.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (18, 8, '2025-12-12 23:48:03', 'R-595', 'Enim officia sapiente voluptatum eius consequatur vero.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (41, 15, '2026-01-25 23:58:15', 'R-403', 'Magni ab ipsam omnis quod dolores delectus.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (42, 6, '2026-01-01 19:07:19', 'R-169', 'Vel nisi culpa libero fuga ipsam.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (17, 2, '2025-12-09 15:27:01', 'R-470', 'Quis optio tenetur explicabo similique.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (1, 4, '2025-12-27 22:47:06', 'R-502', 'Dolorem iusto consequatur doloremque.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (46, 16, '2025-12-12 22:07:08', 'R-361', 'Quidem itaque quod.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (48, 18, '2025-11-29 22:31:00', 'R-120', 'Eaque debitis maxime temporibus in iste voluptatum.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (36, 9, '2026-01-24 17:30:17', 'R-160', 'Nobis commodi ratione quo nostrum.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (27, 3, '2026-01-15 19:45:42', 'R-106', 'Facilis odit corrupti illum.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (30, 6, '2025-12-09 01:11:19', 'R-492', 'Corrupti debitis debitis repudiandae at.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (2, 9, '2025-12-12 15:42:55', 'R-387', 'Eveniet placeat cum.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (32, 3, '2026-01-23 09:28:45', 'R-187', 'Tempore corrupti cumque minima velit tenetur debitis.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (47, 1, '2026-01-25 20:24:42', 'R-149', 'Enim debitis asperiores dolores doloremque dolores odit.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (17, 9, '2025-12-14 09:54:41', 'R-328', 'Dicta aspernatur blanditiis alias omnis.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (15, 11, '2026-01-11 11:07:56', 'R-147', 'Provident fugit facilis doloremque ut.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (47, 14, '2025-12-06 05:47:06', 'R-446', 'Ullam blanditiis enim voluptate excepturi ratione sapiente.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (22, 14, '2025-12-11 10:53:23', 'R-220', 'Nulla doloribus quibusdam quod modi non.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (9, 13, '2026-01-23 05:26:21', 'R-326', 'Ipsa necessitatibus accusantium laborum cupiditate.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (24, 6, '2026-01-02 13:16:37', 'R-173', 'Ea corrupti natus facilis beatae dolor error.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (14, 16, '2026-01-03 17:50:06', 'R-347', 'Eaque maxime est suscipit soluta deleniti.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (22, 19, '2026-01-07 00:28:09', 'R-101', 'Quasi tempore illo aut assumenda voluptates dolorum.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (36, 11, '2026-01-22 18:27:15', 'R-444', 'Pariatur praesentium earum culpa laboriosam doloribus.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (7, 8, '2025-12-17 04:39:56', 'R-280', 'Rerum doloremque a quod adipisci.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (23, 10, '2025-12-09 00:52:39', 'R-153', 'Eaque maxime quidem nulla recusandae provident iste.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (34, 6, '2026-01-13 20:18:47', 'R-581', 'Consequatur sequi deserunt quod sint aliquam repellat.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (49, 4, '2025-12-13 14:59:10', 'R-440', 'Aspernatur voluptate earum neque.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (24, 2, '2026-01-08 10:52:54', 'R-533', 'Impedit aut provident repellat dolorum.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (1, 16, '2025-11-30 05:44:38', 'R-452', 'Quis iure nam corrupti sed doloribus.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (4, 17, '2025-12-30 03:00:52', 'R-128', 'Quaerat perspiciatis dolorum iste adipisci placeat sit natus.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (28, 11, '2026-01-07 15:49:59', 'R-420', 'Aliquam nesciunt voluptatibus harum.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (43, 10, '2025-12-14 06:09:14', 'R-374', 'Nihil blanditiis veniam nostrum optio.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (40, 4, '2026-01-09 03:15:44', 'R-341', 'Tenetur nobis molestias tenetur.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (17, 19, '2025-12-12 10:37:05', 'R-243', 'Eaque architecto similique assumenda deserunt exercitationem sed consequatur.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (37, 4, '2026-01-04 09:52:24', 'R-145', 'Exercitationem eius ipsa delectus.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (37, 18, '2025-12-31 14:19:50', 'R-432', 'Earum magnam accusantium repellat rerum minima reprehenderit.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (20, 6, '2026-01-21 09:50:08', 'R-344', 'Rem corporis sit consequatur impedit ullam tempore.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (42, 15, '2026-01-03 21:28:59', 'R-380', 'Nobis iste nisi provident nihil libero.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (16, 1, '2026-01-16 17:56:01', 'R-401', 'Magni necessitatibus architecto delectus officia soluta autem.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (13, 17, '2025-11-30 09:12:22', 'R-590', 'Facere dicta debitis.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (40, 8, '2025-12-15 13:03:09', 'R-468', 'Pariatur id nulla soluta nobis ratione ullam.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (8, 19, '2026-01-06 21:37:55', 'R-249', 'Aperiam beatae suscipit possimus quis quas.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (16, 9, '2026-01-02 21:06:30', 'R-452', 'Eius odit rerum.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (4, 12, '2025-12-26 07:33:34', 'R-354', 'Exercitationem dolore magni sapiente.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (37, 2, '2026-01-14 07:41:58', 'R-386', 'Neque deleniti magnam temporibus maxime nam voluptatem.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (29, 14, '2025-12-04 14:09:38', 'R-458', 'At dolores deserunt.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (32, 15, '2026-01-06 05:03:36', 'R-350', 'Magni temporibus eveniet.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (16, 1, '2026-01-11 03:34:48', 'R-349', 'Temporibus maxime atque suscipit.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (43, 3, '2025-12-05 06:49:18', 'R-562', 'Repellat dignissimos soluta quod iusto modi.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (31, 5, '2025-12-02 10:31:20', 'R-152', 'Aspernatur quisquam aperiam minus iusto.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (48, 13, '2025-12-13 08:37:56', 'R-512', 'Esse rem nisi ut aliquid.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (35, 19, '2026-01-20 08:18:09', 'R-234', 'Perferendis voluptate illum perspiciatis.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (3, 5, '2025-12-24 02:02:40', 'R-422', 'Ipsam quis repellat maiores necessitatibus laboriosam expedita.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (11, 14, '2025-12-12 20:58:30', 'R-218', 'Et illo cupiditate tenetur inventore tempore.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (40, 15, '2026-01-27 05:03:32', 'R-207', 'Blanditiis quisquam veritatis provident commodi at.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (24, 12, '2025-12-25 12:18:39', 'R-470', 'Nisi mollitia placeat.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (10, 8, '2025-12-30 23:19:04', 'R-451', 'Recusandae unde accusamus incidunt dolorum.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (6, 11, '2026-01-02 18:50:18', 'R-540', 'Harum saepe accusantium assumenda iusto similique.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (7, 7, '2026-01-19 19:43:14', 'R-228', 'Maiores laborum excepturi ipsam quas in.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (16, 14, '2026-01-07 05:26:24', 'R-179', 'Accusantium non veritatis explicabo neque veritatis ipsa.', 'Completed');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (40, 4, '2025-12-09 02:09:58', 'R-550', 'Aperiam nihil ratione ut incidunt saepe corporis.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (6, 10, '2026-01-25 20:25:17', 'R-265', 'Fuga neque aperiam occaecati vero quis porro saepe.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (50, 6, '2026-01-14 05:32:23', 'R-460', 'Fuga debitis et rerum totam.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (22, 4, '2025-12-23 00:27:29', 'R-557', 'Pariatur tempora praesentium.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (30, 17, '2025-12-26 16:37:38', 'R-371', 'Itaque iusto voluptates beatae.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (21, 12, '2025-12-02 00:51:48', 'R-493', 'Assumenda accusantium possimus sunt possimus animi illum distinctio.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (11, 7, '2026-01-23 02:57:08', 'R-502', 'Error possimus pariatur maxime beatae necessitatibus quasi ea.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (1, 15, '2025-12-31 05:27:58', 'R-172', 'At fugiat sequi atque sit.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (16, 10, '2025-12-02 18:47:23', 'R-332', 'Quaerat reprehenderit error.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (50, 4, '2025-12-15 22:14:50', 'R-111', 'Aliquid voluptate odio ut.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (38, 6, '2026-01-02 10:06:34', 'R-466', 'Ipsum est doloribus voluptas rem.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (2, 6, '2026-01-02 19:07:57', 'R-335', 'Vero consequuntur voluptatum ratione at adipisci.', 'Cancelled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (18, 14, '2025-12-06 16:56:28', 'R-146', 'Harum cum esse accusantium animi.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (1, 14, '2025-12-13 21:52:04', 'R-247', 'Modi aliquam distinctio possimus hic.', 'Scheduled');
INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES (40, 13, '2026-01-17 15:23:03', 'R-135', 'Accusantium sint ratione perspiciatis quod.', 'Completed');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (49, 10, 'Voluptate', 'Rerum quam tenetur repellendus molestiae officiis veniam.', '2025-04-10');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (25, 9, 'Amet', 'Sit ea dolores eaque quisquam modi.', '2025-04-05');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (19, 5, 'Rem', 'Nam optio optio itaque dolorem architecto.', '2025-05-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (26, 15, 'Temporibus', 'Assumenda beatae ducimus libero cum commodi corporis distinctio.', '2025-11-30');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 13, 'Reprehenderit', 'Iure fugit voluptate alias sequi.', '2025-02-09');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (14, 10, 'Quibusdam', 'Odit odit dicta placeat.', '2025-07-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (50, 19, 'Soluta', 'Aliquid quis tempora mollitia saepe inventore nulla.', '2024-12-30');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (3, 3, 'Doloribus', 'Cumque adipisci dolore nihil ipsa.', '2025-02-15');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (34, 5, 'Rerum', 'Illo numquam iste rerum.', '2025-11-22');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (6, 3, 'Minima', 'Ipsa autem hic numquam consectetur.', '2025-04-12');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 7, 'Voluptatibus', 'Ea nulla officiis corporis recusandae.', '2025-05-06');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (5, 10, 'Cumque', 'Ducimus tenetur soluta aliquid qui asperiores.', '2024-12-28');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (35, 16, 'Harum', 'Provident quidem cum officia maiores debitis.', '2025-12-08');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (50, 15, 'Iste', 'Hic qui sed odio.', '2025-07-09');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 1, 'Quo', 'Voluptas deleniti consectetur minima iure beatae mollitia.', '2025-04-17');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (25, 1, 'Eveniet', 'Tenetur animi sequi dicta ea.', '2025-09-24');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (2, 2, 'Quidem', 'Possimus magnam quaerat.', '2025-12-14');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (47, 14, 'In', 'Sapiente dicta nulla officia dolorem qui ipsa.', '2025-07-20');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (36, 3, 'Nulla', 'Maxime enim ipsum veniam assumenda.', '2025-04-01');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (9, 16, 'Magni', 'Quod doloribus voluptatibus laboriosam nam enim.', '2025-07-12');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (28, 14, 'Quis', 'Facilis similique doloribus assumenda.', '2025-01-02');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 18, 'Eaque', 'Nemo consequuntur ullam voluptatibus minus laudantium natus.', '2025-06-16');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (47, 20, 'Incidunt', 'Corrupti laborum sed corporis excepturi ipsum ducimus.', '2025-10-13');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (34, 12, 'Recusandae', 'Ipsam ullam magni nisi accusamus qui.', '2025-08-24');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (50, 16, 'Dolores', 'Fugiat alias beatae temporibus.', '2025-07-25');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (29, 20, 'Delectus', 'Suscipit ipsa placeat dolorem quis a vitae.', '2025-11-16');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (42, 8, 'Esse', 'Eum corrupti et molestias perspiciatis reiciendis explicabo.', '2025-08-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (4, 3, 'Qui', 'Perspiciatis provident consectetur sint minima fugiat.', '2025-10-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (4, 11, 'Assumenda', 'Quisquam impedit quo suscipit reprehenderit porro consectetur ad.', '2025-07-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (43, 5, 'Architecto', 'Recusandae numquam nemo animi.', '2025-06-02');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (41, 3, 'Sint', 'Cupiditate expedita voluptas dicta itaque.', '2025-04-02');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (8, 9, 'Quas', 'Fuga iure possimus magnam asperiores nobis.', '2025-12-10');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (6, 19, 'Expedita', 'Vel perferendis modi ea odit.', '2025-11-21');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (26, 1, 'Facere', 'At occaecati aliquid voluptatem error.', '2025-02-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (25, 9, 'Quasi', 'Facilis minus odio voluptatibus quos.', '2025-07-26');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (37, 5, 'Veniam', 'Ullam suscipit facere id incidunt cumque numquam praesentium.', '2025-06-05');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (12, 9, 'Voluptate', 'Possimus minus placeat doloribus illo.', '2025-02-15');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (5, 13, 'Necessitatibus', 'Totam placeat accusamus molestias quisquam est.', '2025-07-17');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (21, 8, 'Expedita', 'Nihil dolore earum nemo maiores natus laudantium nesciunt.', '2025-02-12');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (15, 10, 'Sapiente', 'Error culpa facere vero temporibus nam placeat odit.', '2025-09-24');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (42, 8, 'Occaecati', 'Consectetur cupiditate voluptates amet earum corrupti.', '2025-01-27');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (3, 5, 'Distinctio', 'Cupiditate in vel perspiciatis accusamus temporibus voluptates.', '2025-11-15');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (24, 13, 'Quae', 'Officiis ducimus doloribus at illo.', '2025-05-28');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (35, 5, 'Repudiandae', 'Aut sequi autem tempore autem itaque.', '2025-10-10');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 20, 'Eaque', 'In recusandae ullam voluptatibus ex.', '2025-01-29');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (7, 6, 'Fugit', 'Occaecati consequuntur non quos accusamus animi enim.', '2025-02-18');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (20, 4, 'Id', 'Harum minima voluptates at iure.', '2025-06-22');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (36, 20, 'Fuga', 'Nemo soluta quas ea ipsam deleniti in.', '2025-08-09');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (9, 14, 'Excepturi', 'Occaecati optio a sequi distinctio debitis.', '2025-05-10');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (1, 11, 'Rem', 'Tenetur blanditiis quidem consectetur maxime nulla.', '2025-10-03');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (50, 8, 'Non', 'Consequatur a aliquam.', '2025-02-02');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (44, 15, 'Est', 'Est enim quidem mollitia hic ad.', '2025-12-09');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (22, 18, 'Laboriosam', 'In rerum quidem adipisci nihil iusto.', '2025-08-19');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (2, 18, 'Nesciunt', 'Impedit nesciunt vero corporis provident modi.', '2025-08-08');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (26, 10, 'Molestias', 'Qui voluptatibus architecto unde inventore quidem occaecati.', '2025-01-08');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (47, 15, 'Illum', 'Blanditiis debitis suscipit qui autem.', '2025-08-19');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (7, 13, 'Quidem', 'Quae numquam veritatis magnam.', '2025-09-11');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (13, 4, 'Ducimus', 'Sed perferendis nihil est laborum.', '2025-02-26');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (44, 18, 'Laboriosam', 'Veritatis quis eligendi sequi eaque molestiae.', '2025-09-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (14, 3, 'Ipsa', 'Exercitationem quam labore fugit nulla.', '2025-06-24');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (45, 8, 'Adipisci', 'In ratione quibusdam pariatur officia impedit.', '2025-02-10');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (46, 9, 'Voluptatibus', 'Eum tempore rem commodi repellendus.', '2025-06-25');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (36, 13, 'Sed', 'Suscipit nostrum veniam hic.', '2025-02-24');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (15, 10, 'Accusamus', 'Ratione autem at corporis labore laborum id officia.', '2025-05-04');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (12, 17, 'Dolore', 'Neque enim quae magni illo laborum voluptatem.', '2025-04-10');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (40, 1, 'Necessitatibus', 'Ullam harum saepe iusto ratione voluptatibus.', '2025-07-07');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (15, 10, 'Modi', 'Labore qui recusandae modi illum nesciunt repellendus.', '2025-12-24');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (31, 8, 'Repellat', 'Facere dolore iusto molestias nihil nisi.', '2025-01-10');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (12, 7, 'Aspernatur', 'Repudiandae corporis alias optio adipisci quae distinctio aliquam.', '2025-03-22');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (4, 10, 'Eius', 'Dignissimos corporis reprehenderit iure blanditiis ex vero.', '2025-03-23');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (5, 9, 'Sapiente', 'Illum molestiae delectus amet incidunt dolore.', '2025-03-05');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (23, 15, 'Libero', 'Labore possimus deleniti quia quas quo.', '2025-05-13');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (10, 1, 'Harum', 'Corporis omnis delectus voluptatibus.', '2025-04-21');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (26, 19, 'Laudantium', 'Debitis suscipit consectetur illum illo dolorum quibusdam alias.', '2025-05-08');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (13, 18, 'Voluptas', 'Accusantium voluptas debitis dolorum ducimus magnam eligendi.', '2025-01-30');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (26, 13, 'Enim', 'Tenetur vel magnam explicabo ad tempore.', '2025-02-04');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (9, 7, 'Mollitia', 'Reprehenderit omnis commodi labore fugit voluptatibus doloribus.', '2025-04-01');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (29, 2, 'Repellendus', 'Autem cumque deleniti nisi.', '2025-11-08');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (19, 2, 'Molestiae', 'Sunt ipsa cupiditate delectus quidem aperiam minima.', '2024-12-31');
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES (11, 3, 'Dolor', 'Culpa magnam facilis repellat.', '2025-10-07');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (4, 'perferendis', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (14, 'quas', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (8, 'explicabo', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (41, 'nisi', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (46, 'quo', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (47, 'aut', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (39, 'facilis', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (50, 'culpa', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (35, 'fuga', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (45, 'culpa', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (20, 'dolorem', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (33, 'alias', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (27, 'odio', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (13, 'et', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (11, 'ea', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (19, 'amet', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (30, 'dolorum', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (20, 'magnam', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (1, 'dolorem', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (28, 'ad', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (30, 'molestiae', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (4, 'fugiat', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (31, 'nisi', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (50, 'tenetur', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (47, 'explicabo', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (8, 'aperiam', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (14, 'ducimus', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (2, 'incidunt', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (28, 'deserunt', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (49, 'vero', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (27, 'nulla', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (38, 'praesentium', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (46, 'eos', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (46, 'nemo', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (27, 'laudantium', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (26, 'itaque', 'Life-Threatening');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (3, 'sed', 'Severe');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (31, 'rerum', 'Mild');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (20, 'explicabo', 'Moderate');
INSERT INTO allergies (patient_id, allergen, severity) VALUES (23, 'possimus', 'Life-Threatening');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (32, 5590.55, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (37, 16369.01, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (45, 15653.76, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (3, 814.04, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (2, 3844.87, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (19, 3032.61, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (33, 5173.06, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (24, 1411.03, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (6, 8367.6, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (49, 3297.74, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (44, 3991.54, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (33, 5393.16, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (26, 15066.62, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (22, 14050.85, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (17, 13522.86, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (13, 4291.59, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (19, 12453.68, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (24, 16153.92, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (32, 16617.14, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (47, 12509.88, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (45, 8172.87, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (40, 9286.17, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (3, 7470.44, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (42, 12116.41, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (14, 1846.31, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (47, 5270.86, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (36, 5018.0, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (5, 8627.08, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (18, 13852.05, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (5, 11337.88, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (16, 5137.9, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (44, 17023.98, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (36, 3736.44, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (23, 13162.25, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (42, 6559.83, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (47, 1135.47, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (32, 18422.5, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (39, 13199.76, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (27, 12212.32, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (29, 686.08, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (40, 8410.69, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (31, 16570.4, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (30, 11802.23, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (19, 18532.37, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (46, 2328.03, 'Unpaid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (37, 4755.12, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (24, 1052.77, 'Paid', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (50, 5817.45, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (28, 11617.36, 'Pending', '2025-12-28');
INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES (45, 10751.62, 'Pending', '2025-12-28');



SELECT * FROM patients;

SELECT *
FROM patients
WHERE AGE(dob) > INTERVAL '60 years';

