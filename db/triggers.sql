-- ============================================================
-- AUDIT TRIGGERS  (20 total)
-- Format: pipe-separated values, no labels → shorter strings
-- Columns per table shown in comment above each group
-- ============================================================
DELIMITER //

-- ============================================================
-- 1. MEMBER  (member_id|name|phone_no|gender|status|join_date)
-- ============================================================

CREATE TRIGGER member_insert
AFTER INSERT ON member FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Insert', 'member', NULL,
        CONCAT('member_id:', NEW.member_id, '|name:', NEW.name, '|phone_no:', COALESCE(NEW.phone_no,''), '|gender:', NEW.gender, '|status:', COALESCE(NEW.status,''), '|join_date:', NEW.join_date));
END //

CREATE TRIGGER member_update
AFTER UPDATE ON member FOR EACH ROW
BEGIN
    -- Create empty strings to hold only the changed data then append PK in it
    DECLARE old_changes VARCHAR(500) DEFAULT '';
    DECLARE new_changes VARCHAR(500) DEFAULT '';
    SET old_changes = CONCAT(old_changes, 'member_id:', OLD.member_id);
    SET new_changes = CONCAT(new_changes, 'member_id:', NEW.member_id);


    -- Check each column one by one. (Using COALESCE handles NULL comparisons safely)
    IF COALESCE(OLD.name,'') != COALESCE(NEW.name,'') THEN
        SET old_changes = CONCAT(old_changes, '|name:', OLD.name);
        SET new_changes = CONCAT(new_changes, '|name:', NEW.name);
    END IF;

    IF COALESCE(OLD.phone_no,'') != COALESCE(NEW.phone_no,'') THEN
        SET old_changes = CONCAT(old_changes, '|phone_no:', OLD.phone_no);
        SET new_changes = CONCAT(new_changes, '|phone_no:', NEW.phone_no);
    END IF;

    IF COALESCE(OLD.gender,'') != COALESCE(NEW.gender,'') THEN
        SET old_changes = CONCAT(old_changes, '|gender:', OLD.gender);
        SET new_changes = CONCAT(new_changes, '|gender:', NEW.gender);
    END IF;

    IF COALESCE(OLD.status,'') != COALESCE(NEW.status,'') THEN
        SET old_changes = CONCAT(old_changes, '|status:', OLD.status);
        SET new_changes = CONCAT(new_changes, '|status:', NEW.status);
    END IF;

    IF COALESCE(OLD.join_date,'') != COALESCE(NEW.join_date,'') THEN
        SET old_changes = CONCAT(old_changes, '|join_date:', OLD.join_date);
        SET new_changes = CONCAT(new_changes, '|join_date:', NEW.join_date);
    END IF;


    IF old_changes != CONCAT('member_id:', OLD.member_id) THEN
        INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
        VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Update', 'member', old_changes, new_changes);
    END IF;
END //


-- ============================================================
-- 2. MEMBERSHIP_PLAN  (plan_id|plan_name|duration_days|fee)
-- ============================================================

CREATE TRIGGER plan_insert
AFTER INSERT ON membership_plan FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Insert', 'membership_plan', NULL,
        CONCAT('plan_id:', NEW.plan_id, '|plan_name:', NEW.plan_name, '|duration_days:', NEW.duration_days, '|status:', NEW.status, '|fee:', NEW.fee));
END //

CREATE TRIGGER plan_update
AFTER UPDATE ON membership_plan FOR EACH ROW
BEGIN
    -- Create empty strings to hold only the changed data then append PK in it
    DECLARE old_changes VARCHAR(500) DEFAULT '';
    DECLARE new_changes VARCHAR(500) DEFAULT '';
    SET old_changes = CONCAT(old_changes, 'plan_id:', OLD.plan_id);
    SET new_changes = CONCAT(new_changes, 'plan_id:', NEW.plan_id);


    -- Check each column one by one. (Using COALESCE handles NULL comparisons safely)
    IF COALESCE(OLD.plan_name,'') != COALESCE(NEW.plan_name,'') THEN
        SET old_changes = CONCAT(old_changes, '|plan_name:', OLD.plan_name);
        SET new_changes = CONCAT(new_changes, '|plan_name:', NEW.plan_name);
    END IF;

    IF COALESCE(OLD.duration_days,'') != COALESCE(NEW.duration_days,'') THEN
        SET old_changes = CONCAT(old_changes, '|duration_days:', OLD.duration_days);
        SET new_changes = CONCAT(new_changes, '|duration_days:', NEW.duration_days);
    END IF;

    IF COALESCE(OLD.status,'') != COALESCE(NEW.status,'') THEN
        SET old_changes = CONCAT(old_changes, '|status:', OLD.status);
        SET new_changes = CONCAT(new_changes, '|status:', NEW.status);
    END IF;

    IF COALESCE(OLD.fee,'') != COALESCE(NEW.fee,'') THEN
        SET old_changes = CONCAT(old_changes, '|fee:', OLD.fee);
        SET new_changes = CONCAT(new_changes, '|fee:', NEW.fee);
    END IF;


    IF old_changes != CONCAT('plan_id:', OLD.plan_id) THEN
        INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
        VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Update', 'membership_plan', old_changes, new_changes);
    END IF;
END //


-- ============================================================
-- 3. TRAINER  (trainer_id|name|phone_no|salary|specialization|status|default_fee)
-- ============================================================

CREATE TRIGGER trainer_insert
AFTER INSERT ON trainer FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Insert', 'trainer', NULL,
        CONCAT('trainer_id:', NEW.trainer_id, '|name:', NEW.name, '|phone_no:', COALESCE(NEW.phone_no,''), '|salary:', NEW.salary, '|specialization:', COALESCE(NEW.specialization,''), '|status:', NEW.status, '|default_fee:', COALESCE(NEW.default_fee,'')));
END //

CREATE TRIGGER trainer_update
AFTER UPDATE ON trainer FOR EACH ROW
BEGIN
    -- Create empty strings to hold only the changed data then append PK in it
    DECLARE old_changes VARCHAR(500) DEFAULT '';
    DECLARE new_changes VARCHAR(500) DEFAULT '';
    SET old_changes = CONCAT(old_changes, 'trainer_id:', OLD.trainer_id);
    SET new_changes = CONCAT(new_changes, 'trainer_id:', NEW.trainer_id);


    -- Check each column one by one. (Using COALESCE handles NULL comparisons safely)
    IF COALESCE(OLD.name,'') != COALESCE(NEW.name,'') THEN
        SET old_changes = CONCAT(old_changes, '|name:', OLD.name);
        SET new_changes = CONCAT(new_changes, '|name:', NEW.name);
    END IF;

    IF COALESCE(OLD.phone_no,'') != COALESCE(NEW.phone_no,'') THEN
        SET old_changes = CONCAT(old_changes, '|phone_no:', OLD.phone_no);
        SET new_changes = CONCAT(new_changes, '|phone_no:', NEW.phone_no);
    END IF;

    IF COALESCE(OLD.salary,'') != COALESCE(NEW.salary,'') THEN
        SET old_changes = CONCAT(old_changes, '|salary:', OLD.salary);
        SET new_changes = CONCAT(new_changes, '|salary:', NEW.salary);
    END IF;

     IF COALESCE(OLD.specialization,'') != COALESCE(NEW.specialization,'') THEN
        SET old_changes = CONCAT(old_changes, '|specialization:', OLD.specialization);
        SET new_changes = CONCAT(new_changes, '|specialization:', NEW.specialization);
    END IF;

    IF COALESCE(OLD.status,'') != COALESCE(NEW.status,'') THEN
        SET old_changes = CONCAT(old_changes, '|status:', OLD.status);
        SET new_changes = CONCAT(new_changes, '|status:', NEW.status);
    END IF;

    IF COALESCE(OLD.default_fee,'') != COALESCE(NEW.default_fee,'') THEN
        SET old_changes = CONCAT(old_changes, '|default_fee:', OLD.default_fee);
        SET new_changes = CONCAT(new_changes, '|default_fee:', NEW.default_fee);
    END IF;


    IF old_changes != CONCAT('trainer_id:', OLD.trainer_id) THEN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Update', 'trainer', old_changes, new_changes);
    END IF;
END //


-- ============================================================
-- 4. USER  (user_id|username|status|role)  — NO PASSWORD
-- ============================================================

CREATE TRIGGER user_insert
AFTER INSERT ON user FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Insert', 'user', NULL,
        CONCAT('user_id:', NEW.user_id, '|username:', NEW.username, '|status:', NEW.status, '|role:', NEW.role));
END //

CREATE TRIGGER user_update
AFTER UPDATE ON user FOR EACH ROW
BEGIN
    -- Create empty strings to hold only the changed data then append PK in it
    DECLARE old_changes VARCHAR(500) DEFAULT '';
    DECLARE new_changes VARCHAR(500) DEFAULT '';
    SET old_changes = CONCAT(old_changes, 'user_id:', OLD.user_id);
    SET new_changes = CONCAT(new_changes, 'user_id:', NEW.user_id);


    -- Check each column one by one. (Using COALESCE handles NULL comparisons safely)
    IF COALESCE(OLD.username,'') != COALESCE(NEW.username,'') THEN
        SET old_changes = CONCAT(old_changes, '|username:', OLD.username);
        SET new_changes = CONCAT(new_changes, '|username:', NEW.username);
    END IF;

    IF COALESCE(OLD.status,'') != COALESCE(NEW.status,'') THEN
        SET old_changes = CONCAT(old_changes, '|status:', OLD.status);
        SET new_changes = CONCAT(new_changes, '|status:', NEW.status);
    END IF;

    IF COALESCE(OLD.role,'') != COALESCE(NEW.role,'') THEN
        SET old_changes = CONCAT(old_changes, '|role:', OLD.role);
        SET new_changes = CONCAT(new_changes, '|role:', NEW.role);
    END IF;


    IF old_changes != CONCAT('user_id:', OLD.user_id) THEN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Update', 'user', old_changes, new_changes);
    END IF;
END //


-- ============================================================
-- 5. EXPENSE  (expense_id|amount|expense_date)
-- ============================================================

CREATE TRIGGER expense_insert
AFTER INSERT ON expense FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Insert', 'expense', NULL,
        CONCAT('expense_id:', NEW.expense_id, '|amount:', NEW.amount, '|expense_date:', NEW.expense_date));
END //

CREATE TRIGGER expense_update
AFTER UPDATE ON expense FOR EACH ROW
BEGIN
    -- Create empty strings to hold only the changed data then append PK in it
    DECLARE old_changes VARCHAR(500) DEFAULT '';
    DECLARE new_changes VARCHAR(500) DEFAULT '';
    SET old_changes = CONCAT(old_changes, 'expense_id:', OLD.expense_id);
    SET new_changes = CONCAT(new_changes, 'expense_id:', NEW.expense_id);


    -- Check each column one by one. (Using COALESCE handles NULL comparisons safely)
    IF COALESCE(OLD.amount,'') != COALESCE(NEW.amount,'') THEN
        SET old_changes = CONCAT(old_changes, '|amount:', OLD.amount);
        SET new_changes = CONCAT(new_changes, '|amount:', NEW.amount);
    END IF;

    IF COALESCE(OLD.expense_date,'') != COALESCE(NEW.expense_date,'') THEN
        SET old_changes = CONCAT(old_changes, '|expense_date:', OLD.expense_date);
        SET new_changes = CONCAT(new_changes, '|expense_date:', NEW.expense_date);
    END IF;


    IF old_changes != CONCAT('expense_id:', OLD.expense_id) THEN
        INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
        VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Update', 'expense', old_changes, new_changes);
    END IF;
END //

CREATE TRIGGER expense_delete
AFTER DELETE ON expense FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Delete', 'expense',
        CONCAT('expense_id:', OLD.expense_id, '|amount:', OLD.amount, '|expense_date:', OLD.expense_date),
        NULL);
END //


-- ============================================================
-- 6. MEMBERSHIP (member_id|plan_id|start_date|status|agreed_plan_fee|trainer_id|agreed_trainer_fee)
-- ============================================================

CREATE TRIGGER membership_insert
AFTER INSERT ON membership FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Insert', 'membership', NULL,
        CONCAT('member_id:', NEW.member_id, '|plan_id:', NEW.plan_id, '|start_date:', NEW.start_date, '|status:', NEW.status, '|agreed_plan_fee:', NEW.agreed_plan_fee, '|trainer_id:', COALESCE(NEW.trainer_id,''), '|agreed_trainer_fee:', COALESCE(NEW.agreed_trainer_fee,'')));
END //

CREATE TRIGGER membership_update
AFTER UPDATE ON membership FOR EACH ROW
trigger_block: BEGIN
    -- Create empty strings to hold only the changed data then append PK in it
    DECLARE old_changes VARCHAR(500) DEFAULT '';
    DECLARE new_changes VARCHAR(500) DEFAULT '';
    SET old_changes = CONCAT(old_changes, 'member_id:', OLD.member_id, '|plan_id:', OLD.plan_id, '|start_date:', OLD.start_date);
    SET new_changes = CONCAT(new_changes, 'member_id:', NEW.member_id, '|plan_id:', NEW.plan_id, '|start_date:', NEW.start_date);


    -- Check each column one by one. (Using COALESCE handles NULL comparisons safely)
    IF NOT ( COALESCE(OLD.status,'') != COALESCE(NEW.status,'') AND NEW.status = 'Cancelled') THEN
            LEAVE trigger_block;
    END IF;

    SET old_changes = CONCAT(old_changes, '|status:', OLD.status);
    SET new_changes = CONCAT(new_changes, '|status:', NEW.status);

    IF COALESCE(OLD.agreed_plan_fee,'') != COALESCE(NEW.agreed_plan_fee,'') THEN
        SET old_changes = CONCAT(old_changes, '|agreed_plan_fee:', OLD.agreed_plan_fee);
        SET new_changes = CONCAT(new_changes, '|agreed_plan_fee:', NEW.agreed_plan_fee);
    END IF;

    IF COALESCE(OLD.trainer_id,'') != COALESCE(NEW.trainer_id,'') THEN
        SET old_changes = CONCAT(old_changes, '|trainer_id:', OLD.trainer_id);
        SET new_changes = CONCAT(new_changes, '|trainer_id:', NEW.trainer_id);
    END IF;

    IF COALESCE(OLD.agreed_trainer_fee,'') != COALESCE(NEW.agreed_trainer_fee,'') THEN
        SET old_changes = CONCAT(old_changes, '|agreed_trainer_fee:', OLD.agreed_trainer_fee);
        SET new_changes = CONCAT(new_changes, '|agreed_trainer_fee:', NEW.agreed_trainer_fee);
    END IF;


    IF old_changes != CONCAT('member_id:', OLD.member_id, '|plan_id:', OLD.plan_id, '|start_date:', OLD.start_date) THEN
        INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
        VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Update', 'membership', old_changes, new_changes);
    END IF;
END //

CREATE TRIGGER membership_delete
AFTER DELETE ON membership FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Delete', 'membership',
        CONCAT('member_id:', OLD.member_id, '|plan_id:', OLD.plan_id, '|start_date:', OLD.start_date, '|status:', OLD.status, '|agreed_plan_fee:', OLD.agreed_plan_fee, '|trainer_id:', COALESCE(OLD.trainer_id,''), '|agreed_trainer_fee:', COALESCE(OLD.agreed_trainer_fee,'')),
        NULL);
END //


-- ============================================================
-- 7. PAYMENT  (member_id|plan_id|start_date|payment_date|method)
--    NOTE: No UPDATE trigger — payment is insert/void only
-- ============================================================

CREATE TRIGGER payment_insert
AFTER INSERT ON payment FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Insert', 'payment', NULL,
        CONCAT('member_id:', NEW.member_id, '|plan_id:', NEW.plan_id, '|start_date:', NEW.start_date, '|payment_date:', NEW.payment_date, '|method:', NEW.method));
END //

CREATE TRIGGER payment_delete
AFTER DELETE ON payment FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, timestamp, action, table_name, old_value, new_value)
    VALUES (@current_user_id, CURRENT_TIMESTAMP, 'Delete', 'payment',
        CONCAT('member_id:', OLD.member_id, '|plan_id:', OLD.plan_id, '|start_date:', OLD.start_date, '|payment_date:', OLD.payment_date, '|method:', OLD.method),
        NULL);
END //

DELIMITER ;
