-- ── Business tables ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS teachers (
    id        SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    email     VARCHAR(100),
    subject   VARCHAR(100),
    hired_at  DATE
);

CREATE TABLE IF NOT EXISTS students (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100),
    age         INTEGER,
    gpa         NUMERIC(3,2),
    phone       VARCHAR(20),
    address     TEXT,
    enrolled_at DATE
);

CREATE TABLE IF NOT EXISTS courses (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(150) NOT NULL,
    teacher_id   INTEGER REFERENCES teachers(id),
    credits      INTEGER,
    description  TEXT,
    start_date   DATE,
    end_date     DATE,
    max_students INTEGER
);

CREATE TABLE IF NOT EXISTS enrollments (
    id          SERIAL PRIMARY KEY,
    student_id  INTEGER REFERENCES students(id),
    course_id   INTEGER REFERENCES courses(id),
    grade       NUMERIC(4,2),
    enrolled_at DATE,
    status      VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS grades (
    id          SERIAL PRIMARY KEY,
    student_id  INTEGER REFERENCES students(id),
    course_id   INTEGER REFERENCES courses(id),
    grade       NUMERIC(4,2),
    grade_type  VARCHAR(20),
    graded_at   DATE
);

CREATE TABLE IF NOT EXISTS parents (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100),
    phone       VARCHAR(20),
    student_id  INTEGER REFERENCES students(id),
    relation    VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS payments (
    id          SERIAL PRIMARY KEY,
    student_id  INTEGER REFERENCES students(id),
    amount      NUMERIC(10,2),
    paid_at     TIMESTAMP,
    status      VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS attendance (
    id          SERIAL PRIMARY KEY,
    student_id  INTEGER REFERENCES students(id),
    course_id   INTEGER REFERENCES courses(id),
    date        DATE,
    status      VARCHAR(20)
);

-- ── Sample data ─────────────────────────────────────────────────────────────

INSERT INTO teachers (name, email, subject, hired_at) VALUES
    ('Alisher Umarov',   'alisher@school.uz',  'Matematika',      '2018-09-01'),
    ('Dilnoza Yusupova', 'dilnoza@school.uz',  'Fizika',          '2019-03-15'),
    ('Sardor Rашidov',   'sardor@school.uz',   'Informatika',     '2020-01-10'),
    ('Malika Karimova',  'malika@school.uz',   'Ingliz tili',     '2017-08-20'),
    ('Bobur Toshmatov',  'bobur@school.uz',    'Tarix',           '2016-06-05');

INSERT INTO students (name, email, age, gpa, phone, address, enrolled_at) VALUES
    ('Jasur Holmatov',   'jasur@mail.uz',   20, 3.85, '+998901234567', 'Toshkent, Chilonzor',   '2023-09-01'),
    ('Zulfiya Nazarova', 'zulfiya@mail.uz', 21, 3.92, '+998901234568', 'Toshkent, Yunusobod',   '2023-09-01'),
    ('Otabek Mirzayev',  'otabek@mail.uz',  19, 3.45, '+998901234569', 'Samarqand',             '2023-09-01'),
    ('Nodira Xasanova',  'nodira@mail.uz',  22, 3.71, '+998901234570', 'Toshkent, Mirzo Ulugbek','2023-09-01'),
    ('Sherzod Qodirov',  'sherzod@mail.uz', 20, 2.95, '+998901234571', 'Fargona',               '2023-09-01'),
    ('Kamola Tursunova', 'kamola@mail.uz',  21, 3.60, '+998901234572', 'Toshkent, Sergeli',     '2023-09-01'),
    ('Ulugbek Rahimov',  'ulugbek@mail.uz', 23, 3.10, '+998901234573', 'Namangan',              '2022-09-01'),
    ('Feruza Abdullayeva','feruza@mail.uz',  20, 3.78, '+998901234574', 'Toshkent, Shayxontohur','2023-09-01');

INSERT INTO courses (title, teacher_id, credits, description, start_date, end_date, max_students) VALUES
    ('Oliy Matematika',    1, 4, 'Differensial va integral hisob',    '2024-02-01', '2024-06-30', 30),
    ('Fizika asoslari',    2, 3, 'Mexanika va termodinamika',         '2024-02-01', '2024-06-30', 25),
    ('Dasturlash (Python)',3, 4, 'Python dasturlash tili asoslari',   '2024-02-01', '2024-06-30', 35),
    ('Ingliz tili B2',     4, 2, 'Akademik ingliz tili',             '2024-02-01', '2024-06-30', 20),
    ('O''zbekiston tarixi',5, 2, 'Mustaqillik davri tarixi',          '2024-02-01', '2024-06-30', 40),
    ('Algebra va geometriya',1,3,'Chiziqli algebra va analitik geometriya','2024-02-01','2024-06-30',30);

INSERT INTO enrollments (student_id, course_id, grade, enrolled_at, status) VALUES
    (1, 1, 88.5, '2024-02-01', 'active'), (1, 3, 95.0, '2024-02-01', 'active'), (1, 4, 82.0, '2024-02-01', 'active'),
    (2, 1, 92.0, '2024-02-01', 'active'), (2, 2, 90.0, '2024-02-01', 'active'), (2, 4, 96.0, '2024-02-01', 'active'),
    (3, 1, 75.0, '2024-02-01', 'active'), (3, 3, 80.0, '2024-02-01', 'active'), (3, 5, 78.0, '2024-02-01', 'active'),
    (4, 2, 85.0, '2024-02-01', 'active'), (4, 4, 88.0, '2024-02-01', 'active'), (4, 6, 91.0, '2024-02-01', 'active'),
    (5, 1, 65.0, '2024-02-01', 'active'), (5, 3, 70.0, '2024-02-01', 'active'), (5, 5, 68.0, '2024-02-01', 'active'),
    (6, 2, 82.0, '2024-02-01', 'active'), (6, 3, 87.0, '2024-02-01', 'active'), (6, 6, 79.0, '2024-02-01', 'active'),
    (7, 1, 72.0, '2024-02-01', 'active'), (7, 5, 74.0, '2024-02-01', 'active'),
    (8, 2, 89.0, '2024-02-01', 'active'), (8, 4, 93.0, '2024-02-01', 'active'), (8, 6, 85.0, '2024-02-01', 'active');

INSERT INTO grades (student_id, course_id, grade, grade_type, graded_at) VALUES
    (1,1,85.0,'midterm','2024-04-01'), (1,1,92.0,'final','2024-06-20'),
    (1,3,93.0,'midterm','2024-04-01'), (1,3,97.0,'final','2024-06-20'),
    (2,1,90.0,'midterm','2024-04-01'), (2,1,94.0,'final','2024-06-20'),
    (2,2,88.0,'midterm','2024-04-01'), (2,2,92.0,'final','2024-06-20'),
    (3,1,72.0,'midterm','2024-04-01'), (3,1,78.0,'final','2024-06-20'),
    (4,2,83.0,'midterm','2024-04-01'), (4,2,87.0,'final','2024-06-20'),
    (5,1,60.0,'midterm','2024-04-01'), (5,1,70.0,'final','2024-06-20'),
    (6,2,80.0,'midterm','2024-04-01'), (6,2,84.0,'final','2024-06-20'),
    (7,1,68.0,'midterm','2024-04-01'), (7,1,76.0,'final','2024-06-20'),
    (8,2,87.0,'midterm','2024-04-01'), (8,2,91.0,'final','2024-06-20');

INSERT INTO parents (name, phone, student_id, relation) VALUES
    ('Holmat Holmatov',   '+998901110001', 1, 'father'),
    ('Barno Holmatova',   '+998901110002', 1, 'mother'),
    ('Nazarov Ismoil',    '+998901110003', 2, 'father'),
    ('Mirzayev Tohir',    '+998901110005', 3, 'father'),
    ('Xasanova Gulnora',  '+998901110007', 4, 'mother'),
    ('Qodirov Mansur',    '+998901110009', 5, 'father'),
    ('Tursunova Mavluda', '+998901110011', 6, 'mother'),
    ('Rahimov Saidakbar', '+998901110013', 7, 'father'),
    ('Abdullayev Hamid',  '+998901110015', 8, 'father');

INSERT INTO payments (student_id, amount, paid_at, status) VALUES
    (1, 1500000, '2024-02-05 10:00:00', 'paid'),
    (1,  500000, '2024-04-05 10:00:00', 'paid'),
    (2, 1500000, '2024-02-03 09:00:00', 'paid'),
    (3, 1500000, '2024-02-10 11:00:00', 'paid'),
    (3,  500000, NULL,                  'pending'),
    (4, 1500000, '2024-02-07 08:30:00', 'paid'),
    (5, 1000000, '2024-02-15 14:00:00', 'paid'),
    (5,  500000, NULL,                  'overdue'),
    (6, 1500000, '2024-02-06 10:00:00', 'paid'),
    (7,  800000, '2024-02-20 09:00:00', 'paid'),
    (7,  700000, NULL,                  'overdue'),
    (8, 1500000, '2024-02-04 11:00:00', 'paid');

INSERT INTO attendance (student_id, course_id, date, status) VALUES
    (1,1,'2024-02-05','present'),(1,1,'2024-02-12','present'),(1,1,'2024-02-19','late'),(1,1,'2024-02-26','present'),
    (1,3,'2024-02-06','present'),(1,3,'2024-02-13','present'),(1,3,'2024-02-20','present'),(1,3,'2024-02-27','present'),
    (2,1,'2024-02-05','present'),(2,1,'2024-02-12','present'),(2,1,'2024-02-19','present'),(2,1,'2024-02-26','present'),
    (2,2,'2024-02-07','present'),(2,2,'2024-02-14','present'),(2,2,'2024-02-21','absent'),(2,2,'2024-02-28','present'),
    (3,1,'2024-02-05','present'),(3,1,'2024-02-12','absent'),(3,1,'2024-02-19','absent'),(3,1,'2024-02-26','late'),
    (4,2,'2024-02-07','present'),(4,2,'2024-02-14','present'),(4,2,'2024-02-21','present'),(4,2,'2024-02-28','present'),
    (5,1,'2024-02-05','absent'),(5,1,'2024-02-12','present'),(5,1,'2024-02-19','absent'),(5,1,'2024-02-26','absent'),
    (6,2,'2024-02-07','present'),(6,2,'2024-02-14','late'),(6,2,'2024-02-21','present'),(6,2,'2024-02-28','present'),
    (7,1,'2024-02-05','present'),(7,1,'2024-02-12','present'),(7,1,'2024-02-19','late'),(7,1,'2024-02-26','present'),
    (8,2,'2024-02-07','present'),(8,2,'2024-02-14','present'),(8,2,'2024-02-21','present'),(8,2,'2024-02-28','present');

-- ── Permissions for ai_readonly ─────────────────────────────────────────────
GRANT SELECT ON students, teachers, courses, enrollments,
                grades, parents, payments, attendance TO ai_readonly;
