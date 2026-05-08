-- Create and use the database
CREATE DATABASE gymdb;
USE gymdb;

-- 1. MEMBER Table 
CREATE TABLE `member` ( 
  `member_id`  INTEGER      NOT NULL AUTO_INCREMENT, 
  `name`       VARCHAR(50)  NOT NULL, 
  `phone_no`   VARCHAR(20)  NULL, 
  `email`      VARCHAR(50)  NULL, 
  `gender`     VARCHAR(15)  CHECK (`gender` IN ('Male', 'Female', 'Other')), 
  `join_date`  DATE         NOT NULL, 
 
  PRIMARY KEY (`member_id`) 
); 
 
-- 2. MEMBERSHIP_PLAN Table 
CREATE TABLE `membership_plan` ( 
  `plan_id`       INTEGER       NOT NULL AUTO_INCREMENT, 
  `plan_name`     VARCHAR(50)   NOT NULL UNIQUE, 
  `duration_days` INTEGER       NOT NULL, 
  `fee`           DECIMAL(10,2) NOT NULL, 
 
  PRIMARY KEY (`plan_id`) 
); 
 
-- 3. TRAINER Table 
CREATE TABLE `trainer` ( 
  `trainer_id`     INTEGER       NOT NULL AUTO_INCREMENT, 
  `name`           VARCHAR(50)   NOT NULL, 
  `phone_no`       VARCHAR(20)   NULL, 
  `salary`         DECIMAL(10,2) CHECK (`salary` >= 0) NOT NULL, 
  `specialization` VARCHAR(50)   NULL, 
  `status`         VARCHAR(20)   NOT NULL CHECK (`status` IN ('Active', 'On-leave', 'Terminated')), 
  `default_fee`    DECIMAL(10,2) NULL, 
 
  PRIMARY KEY (`trainer_id`) 
); 
 
-- 4. USER Table 
CREATE TABLE `user` ( 
  `user_id`    INTEGER      NOT NULL AUTO_INCREMENT, 
  `username`   VARCHAR(45)  NOT NULL, 
  `password`   VARCHAR(45)  NOT NULL CHECK (LENGTH(`password`) >= 8), 
  `role`       VARCHAR(25)  NOT NULL CHECK (`role` IN ('Admin', 'Receptionist')), 
  `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP, 
 
  PRIMARY KEY (`user_id`) 
); 
 
-- 5. EXPENSE Table 
CREATE TABLE `expense` ( 
  `expense_id`   INTEGER       NOT NULL AUTO_INCREMENT, 
  `amount`       DECIMAL(10,2) NOT NULL CHECK (`amount` > 0), 
  `expense_date` DATE          NOT NULL, 
 
  PRIMARY KEY (`expense_id`) 
); 
 
-- 6. OPERATIONAL_EXPENSE Table 
CREATE TABLE `operational_expense` ( 
  `expense_id` INTEGER     NOT NULL, 
  `category`   VARCHAR(50) NOT NULL CHECK (`category` IN ('Utility Bills', 'Rent', 'Marketing&Sales', 'Maintenance&Supplies', 'Extras')), 
 
  PRIMARY KEY (`expense_id`), 
  CONSTRAINT `oe_eid_fk` FOREIGN KEY (`expense_id`) 
    REFERENCES `expense` (`expense_id`) 
); 
 
-- 7. SALARY_EXPENSE Table 
CREATE TABLE `salary_expense` ( 
  `expense_id` INTEGER NOT NULL, 
  `trainer_id` INTEGER NOT NULL, 
 
  PRIMARY KEY (`expense_id`), 
  CONSTRAINT `se_eid_fk` FOREIGN KEY (`expense_id`) 
    REFERENCES `expense` (`expense_id`), 
  CONSTRAINT `se_tid_fk` FOREIGN KEY (`trainer_id`) 
    REFERENCES `trainer` (`trainer_id`) 
); 
 
-- 8. MEMBERSHIP Table 
CREATE TABLE `membership` ( 
  `member_id`          INTEGER       NOT NULL, 
  `plan_id`            INTEGER       NOT NULL, 
  `start_date`         DATE          NOT NULL, 
  `status`             VARCHAR(20)   NOT NULL CHECK (`status` IN ('Active', 'Expired', 'Cancelled', 'Upcoming')), 
  `agreed_plan_fee`    DECIMAL(10,2) NOT NULL, 
  `trainer_id`         INTEGER       NULL, 
  `agreed_trainer_fee` DECIMAL(10,2) NULL, 
 
  PRIMARY KEY (`member_id`, `plan_id`, `start_date`), 
  CONSTRAINT `ms_mid_fk` FOREIGN KEY (`member_id`) 
    REFERENCES `member` (`member_id`), 
  CONSTRAINT `ms_pid_fk` FOREIGN KEY (`plan_id`) 
    REFERENCES `membership_plan` (`plan_id`), 
  CONSTRAINT `ms_tid_fk` FOREIGN KEY (`trainer_id`) 
    REFERENCES `trainer` (`trainer_id`) 
); 

-- 9. PAYMENT Table 
CREATE TABLE `payment` ( 
  `member_id`    INTEGER       NOT NULL, 
  `plan_id`      INTEGER       NOT NULL, 
  `start_date`   DATE          NOT NULL, 
  `payment_date` DATE          NOT NULL, 
  `method`       VARCHAR(20)   NOT NULL,  

  PRIMARY KEY (`member_id`, `plan_id`, `start_date`), 
  CONSTRAINT `pay_mem_fk` FOREIGN KEY (`member_id`, `plan_id`, `start_date`) 
    REFERENCES `membership` (`member_id`, `plan_id`, `start_date`) 
); 

-- 10. AUDIT_LOG Table 
CREATE TABLE `audit_log` ( 
  `user_id`     INTEGER      NOT NULL, 
  `timestamp`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP, 
  `action`      VARCHAR(15)  NOT NULL CHECK (`action` IN ('Insert', 'Update', 'Delete')), 
  `table_name`  VARCHAR(30)  NOT NULL,
  `old_value`   VARCHAR(255) NULL, 
  `new_value`   VARCHAR(255) NULL, 

  PRIMARY KEY (`user_id`, `timestamp`), 
  CONSTRAINT `al_uid_fk` FOREIGN KEY (`user_id`) 
    REFERENCES `user` (`user_id`)
);

-- AUDIT_LOG.affected_id removed because it will be shown in old_value and new_value
-- PAYMENT.amount removed because it is a derived attr 


-- INSERTING A DEFAULT USER BECAUSE EVERY ACTION NEEDS A USER_ID IN AUDIT_LOG
use gymdb;
INSERT INTO user(username, password, role, created_at)
VALUES('ALI','1234-345','Admin', sysdate());


-- There will be 2 views but for now there is only 1.

-- View 1: memberships with full detail
-- MEMBERSHIP_VIEW (member_id, member_name, plan_name, start_date, end_date, status, agreed_plan_fee, trainer_name, agreed_trainer_fee)

CREATE VIEW memberships_view AS
SELECT 
    m.member_id,
    m.name AS member_name,
    mp.plan_id,
    mp.plan_name,
    ms.start_date,

    DATE_ADD(ms.start_date, INTERVAL mp.duration_days DAY) AS end_date,

    ms.status,
    ms.agreed_plan_fee,
    t.trainer_id,
    t.name AS trainer_name,
    ms.agreed_trainer_fee

FROM membership ms
INNER JOIN member m 
    ON ms.member_id = m.member_id
INNER JOIN membership_plan mp 
    ON ms.plan_id = mp.plan_id
LEFT JOIN trainer t 
    ON ms.trainer_id = t.trainer_id;

-- View 2: Audit_logs with user details
-- AUDIT_VIEW (user_id, username, timestamp, action, tablename, oldval, newval)

CREATE VIEW audit_view AS
SELECT 
    a.user_id,
    u.username, -- Pulling the human-readable name
    a.timestamp,
    a.action,
    a.table_name,
    a.old_value,
    a.new_value

FROM audit_log a
LEFT JOIN user u
    ON a.user_id = u.user_id;


-- View 3: Payments with Details
-- PAYMENT_VIEW (member_id, member_name, plan_id, plan_name, payment_date, method, amount, payment_status)

CREATE VIEW payment_view AS
SELECT
    mv.member_id,
    mv.member_name,
    mv.plan_id,
    mv.plan_name,
    mv.start_date,
    p.payment_date,
    p.method,

    (mv.agreed_plan_fee + COALESCE(mv.agreed_trainer_fee, 0)) AS amount,

    CASE
        WHEN p.member_id IS NOT NULL THEN 'Paid'
        ELSE 'Unpaid'
    END AS payment_status

FROM memberships_view mv
LEFT JOIN payment p
    ON  mv.member_id  = p.member_id
    AND mv.plan_id    = p.plan_id
    AND mv.start_date = p.start_date;
