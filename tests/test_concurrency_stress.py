"""
Adversarial Concurrency & Transaction Stress Test Suite
Milestone 1 — Challenger 1 Verification Harness

Tests:
1. Disk WAL mode pragma & 5000ms busy timeout verification
2. Busy timeout lock resolution under write contention
3. Mid-batch transaction rollback atomicity (zero partial state)
4. Double-assignment race condition (2+ threads competing for same serial)
5. 20 concurrent threads with independent connections (WAL multi-connection stress)
6. 20 concurrent threads on a shared DatabaseManager instance (pywebview runtime model)
7. Concurrent mixed valid/invalid transactions ensuring rollback isolation
"""

import os
import time
import threading
import sqlite3
import pytest
from db_manager import DatabaseManager


# ----------------------------------------------------------------------
# 1. WAL Mode & Busy Timeout Verification
# ----------------------------------------------------------------------
def test_wal_mode_and_busy_timeout_pragmas(temp_dir):
    """Verify that a disk-backed SQLite database runs in WAL mode with 5000ms busy timeout."""
    db_path = os.path.join(temp_dir, "wal_verify.db")
    db = DatabaseManager(db_path)
    db.initialize_db()

    cursor = db.conn.cursor()
    cursor.execute("PRAGMA journal_mode;")
    journal_mode = cursor.fetchone()[0].lower()
    assert journal_mode == "wal", f"Expected WAL journal mode on disk, got: {journal_mode}"

    cursor.execute("PRAGMA busy_timeout;")
    busy_timeout = cursor.fetchone()[0]
    assert busy_timeout >= 5000, f"Expected busy_timeout >= 5000ms, got: {busy_timeout}"

    cursor.execute("PRAGMA synchronous;")
    sync_mode = cursor.fetchone()[0]
    # In SQLite: 1 = NORMAL
    assert sync_mode == 1, f"Expected synchronous = NORMAL (1), got: {sync_mode}"

    cursor.execute("PRAGMA foreign_keys;")
    fk_mode = cursor.fetchone()[0]
    assert fk_mode == 1, f"Expected foreign_keys = ON (1), got: {fk_mode}"

    db.close()


def test_busy_timeout_lock_resolution(temp_dir):
    """
    Adversarial test: Connection 1 holds an exclusive write transaction for 300ms.
    Connection 2 attempts to write during that window.
    Connection 2 must NOT crash with 'database is locked', but wait and succeed.
    """
    db_path = os.path.join(temp_dir, "lock_test.db")
    db1 = DatabaseManager(db_path)
    db1.initialize_db()
    db2 = DatabaseManager(db_path)

    # Insert a model via db1
    mid = db1.add_camera_model("TEST-LOCK", "Lock Test Model", "Nature", "Cat", "Sub")
    assert mid > 0

    outcome = {"db2_started": False, "db2_success": False, "db2_error": None, "duration": 0}

    def writer_db1():
        # Start transaction and hold exclusive lock
        c1 = db1.conn.cursor()
        c1.execute("BEGIN IMMEDIATE;")
        c1.execute("INSERT INTO serial_numbers (model_id, serial_number) VALUES (?, ?);", (mid, "SN-LOCK-DB1"))
        time.sleep(0.4)  # Hold write lock for 400ms
        db1.conn.commit()

    def writer_db2():
        time.sleep(0.1)  # Ensure db1 started transaction
        outcome["db2_started"] = True
        t0 = time.time()
        try:
            # db2 attempts to insert a serial while db1 holds the lock
            count = db2.save_serial_batch(mid, ["SN-LOCK-DB2"])
            outcome["db2_success"] = (count == 1)
        except Exception as e:
            outcome["db2_error"] = str(e)
        finally:
            outcome["duration"] = time.time() - t0

    t1 = threading.Thread(target=writer_db1)
    t2 = threading.Thread(target=writer_db2)

    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)

    assert outcome["db2_started"] is True
    assert outcome["db2_error"] is None, f"db2 failed with error: {outcome['db2_error']}"
    assert outcome["db2_success"] is True, "db2 failed to insert serial after waiting for lock"
    # Duration should be at least ~300ms because it had to wait for db1 to finish
    assert outcome["duration"] >= 0.25, f"Expected db2 to wait for busy timeout, waited {outcome['duration']}s"

    db1.close()
    db2.close()


# ----------------------------------------------------------------------
# 2. Mid-Batch Transaction Rollback Atomicity
# ----------------------------------------------------------------------
def test_assign_cameras_batch_mid_batch_failure_leaves_zero_traces(temp_db, sample_model, sample_client):
    """
    Adversarial rollback test:
    Attempt assigning 5 serials where the 3rd serial ID violates a foreign key constraint.
    Verify:
    1. Method returns 0 (not 2).
    2. NONE of the serials (including the first two) are marked is_used = 1.
    3. client_purchases contains ZERO records.
    """
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    serials = [f"SN-ATOMIC-{i:03d}" for i in range(1, 6)]
    temp_db.save_serial_batch(mid, serials)

    all_serials = temp_db.get_available_serials(mid)
    sids = [s["id"] for s in all_serials]

    # Inject an invalid serial ID into the middle of the batch
    poisoned_batch = [sids[0], sids[1], 99999999, sids[2], sids[3]]

    result = temp_db.assign_cameras_batch(cid, poisoned_batch)
    assert result == 0, f"assign_cameras_batch should return 0 on failure, returned {result}"

    # Verify state in database
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM client_purchases WHERE client_id = ?;", (cid,))
    cp_count = cursor.fetchone()[0]
    assert cp_count == 0, f"Leaked partial client_purchases records: {cp_count} found"

    cursor.execute("SELECT COUNT(*) FROM serial_numbers WHERE is_used = 1;")
    used_count = cursor.fetchone()[0]
    assert used_count == 0, f"Leaked partial is_used flag: {used_count} serials marked used"


def test_return_cameras_batch_rollback_on_failure(temp_db, sample_model, sample_client):
    """
    Adversarial rollback test on return_cameras_batch.
    When returning cameras, if an unexpected database error occurs,
    the transaction must cleanly roll back without corrupting state.
    """
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    serials = ["SN-RET-1", "SN-RET-2", "SN-RET-3"]
    temp_db.save_serial_batch(mid, serials)
    available = temp_db.get_available_serials(mid)
    sids = [s["id"] for s in available]

    assigned = temp_db.assign_cameras_batch(cid, sids)
    assert assigned == 3

    # Returning non-existent serial alongside valid ones
    # Existing behavior: return_cameras_batch skips serials not found, returns count of actually returned
    count = temp_db.return_cameras_batch(["SN-RET-1", "NON-EXISTENT-SN", "SN-RET-2"])
    assert count == 2

    # SN-RET-3 should still be assigned
    avail = temp_db.get_available_serials(mid)
    assert len(avail) == 2
    assert {s["serial_number"] for s in avail} == {"SN-RET-1", "SN-RET-2"}


# ----------------------------------------------------------------------
# 3. Double-Assignment Race Condition
# ----------------------------------------------------------------------
def test_double_assignment_race_condition(temp_dir, sample_model, sample_client):
    """
    Adversarial race condition:
    Two threads, using separate connections to the same database,
    simultaneously attempt to assign the EXACT SAME camera serial to two different clients.
    Because serial_id in client_purchases is UNIQUE, exactly ONE must succeed and ONE must fail.
    Database integrity must remain 100% consistent.
    """
    db_path = os.path.join(temp_dir, "race_assign.db")
    setup_db = DatabaseManager(db_path)
    setup_db.initialize_db()

    mid = setup_db.add_camera_model(**sample_model)
    client1 = dict(sample_client)
    client1["doc_number"] = "DOC-CLIENT-1"
    cid1 = setup_db.add_client(client1)

    client2 = dict(sample_client)
    client2["doc_number"] = "DOC-CLIENT-2"
    cid2 = setup_db.add_client(client2)

    setup_db.save_serial_batch(mid, ["SN-PRIZED-CAMERA"])
    prized_sid = setup_db.get_available_serials(mid)[0]["id"]
    setup_db.close()

    barrier = threading.Barrier(2)
    results = {"thread1": None, "thread2": None, "err1": None, "err2": None}

    def assign_worker_1():
        db = DatabaseManager(db_path)
        barrier.wait()
        try:
            results["thread1"] = db.assign_camera_to_client(cid1, prized_sid)
        except Exception as e:
            results["err1"] = str(e)
        finally:
            db.close()

    def assign_worker_2():
        db = DatabaseManager(db_path)
        barrier.wait()
        try:
            results["thread2"] = db.assign_camera_to_client(cid2, prized_sid)
        except Exception as e:
            results["err2"] = str(e)
        finally:
            db.close()

    t1 = threading.Thread(target=assign_worker_1)
    t2 = threading.Thread(target=assign_worker_2)
    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)

    # Exactly one thread must succeed
    successes = [results["thread1"], results["thread2"]]
    assert successes.count(True) == 1, f"Expected exactly 1 success, got: {successes}"
    assert successes.count(False) == 1, f"Expected exactly 1 failure, got: {successes}"

    # Verify DB state
    verify_db = DatabaseManager(db_path)
    cursor = verify_db.conn.cursor()
    cursor.execute("SELECT client_id FROM client_purchases WHERE serial_id = ?;", (prized_sid,))
    purchases = cursor.fetchall()
    assert len(purchases) == 1, f"Expected exactly 1 purchase record, found: {len(purchases)}"

    cursor.execute("SELECT is_used FROM serial_numbers WHERE id = ?;", (prized_sid,))
    assert cursor.fetchone()[0] == 1, "Serial should be marked as used"
    verify_db.close()


# ----------------------------------------------------------------------
# 4. 20 Concurrent Threads: Multi-Connection WAL Stress Test
# ----------------------------------------------------------------------
def test_20_concurrent_threads_multi_connection_stress(temp_dir, sample_model, sample_client):
    """
    Stress test with 20 concurrent threads running across separate connections:
    - 5 threads querying dashboard analytics repeatedly
    - 5 threads searching serials with filters repeatedly
    - 5 threads inserting new serial numbers
    - 5 threads assigning and returning serials
    Verifies that WAL mode + busy timeout handle concurrent read/write load without deadlocks or crashes.
    """
    db_path = os.path.join(temp_dir, "concurrency_20_multi.db")
    setup_db = DatabaseManager(db_path)
    setup_db.initialize_db()

    mid = setup_db.add_camera_model(**sample_model)
    cids = []
    for i in range(5):
        cl = dict(sample_client)
        cl["doc_number"] = f"DOC-MULTI-{i}"
        cids.append(setup_db.add_client(cl))

    # Pre-populate 50 serials
    pre_serials = [f"SN-PRE-{i:04d}" for i in range(50)]
    setup_db.save_serial_batch(mid, pre_serials)
    setup_db.close()

    thread_errors = []
    start_barrier = threading.Barrier(20)

    # Worker group 1: Analytics Readers (5 threads)
    def analytics_worker(tid):
        try:
            db = DatabaseManager(db_path)
            start_barrier.wait()
            for _ in range(10):
                res = db.get_dashboard_analytics()
                assert "total_stock" in res
                assert "total_assigned" in res
                time.sleep(0.01)
            db.close()
        except Exception as e:
            thread_errors.append((f"analytics-{tid}", str(e)))

    # Worker group 2: Search Readers (5 threads)
    def search_worker(tid):
        try:
            db = DatabaseManager(db_path)
            start_barrier.wait()
            for _ in range(10):
                res = db.search_serials(query="PRE", model_id=mid, status="all")
                assert isinstance(res, list)
                time.sleep(0.01)
            db.close()
        except Exception as e:
            thread_errors.append((f"search-{tid}", str(e)))

    # Worker group 3: Serial Writers (5 threads)
    def writer_worker(tid):
        try:
            db = DatabaseManager(db_path)
            start_barrier.wait()
            for step in range(5):
                batch = [f"SN-T{tid}-S{step}-{k}" for k in range(5)]
                inserted = db.save_serial_batch(mid, batch)
                assert inserted == 5
                time.sleep(0.01)
            db.close()
        except Exception as e:
            thread_errors.append((f"writer-{tid}", str(e)))

    # Worker group 4: Assignment/Return Workers (5 threads)
    def assign_worker(tid):
        try:
            db = DatabaseManager(db_path)
            cid = cids[tid % len(cids)]
            start_barrier.wait()
            for step in range(3):
                # Save batch of unique serials to assign and return
                unique_batch = [f"SN-AR-{tid}-{step}-{k}" for k in range(3)]
                db.save_serial_batch(mid, unique_batch)
                # Find available IDs
                avail = db.get_available_serials(mid)
                target_sids = [s["id"] for s in avail if s["serial_number"] in unique_batch]
                if target_sids:
                    assigned_count = db.assign_cameras_batch(cid, target_sids)
                    assert assigned_count == len(target_sids)
                    # Return them back
                    returned_count = db.return_cameras_batch(unique_batch)
                    assert returned_count == len(unique_batch)
                time.sleep(0.01)
            db.close()
        except Exception as e:
            thread_errors.append((f"assign-{tid}", str(e)))

    threads = []
    for i in range(5):
        threads.append(threading.Thread(target=analytics_worker, args=(i,)))
    for i in range(5):
        threads.append(threading.Thread(target=search_worker, args=(i,)))
    for i in range(5):
        threads.append(threading.Thread(target=writer_worker, args=(i,)))
    for i in range(5):
        threads.append(threading.Thread(target=assign_worker, args=(i,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert len(thread_errors) == 0, f"Thread errors encountered during 20-thread multi-connection stress: {thread_errors}"

    # Final DB integrity validation
    final_db = DatabaseManager(db_path)
    analytics = final_db.get_dashboard_analytics()
    # 50 pre-populated + 5*5*5 (writer) + 5*3*3 (assign/return) = 50 + 125 + 45 = 220 serials total
    cursor = final_db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM serial_numbers;")
    total_sn = cursor.fetchone()[0]
    assert total_sn == 220, f"Expected 220 serials, got {total_sn}"
    assert analytics["total_stock"] == 220
    assert analytics["total_assigned"] == 0
    final_db.close()


# ----------------------------------------------------------------------
# 5. 20 Concurrent Threads: Shared DatabaseManager Instance (pywebview bridge)
# ----------------------------------------------------------------------
def test_20_concurrent_threads_shared_instance_stress(temp_dir, sample_model, sample_client):
    """
    Stress test with 20 concurrent threads calling methods on the SAME DatabaseManager instance.
    This simulates pywebview calling the bridge methods concurrently from its thread pool.
    Tests if sharing self.conn across 20 threads creates race conditions, cursor collisions, or crashes.
    """
    db_path = os.path.join(temp_dir, "concurrency_20_shared.db")
    shared_db = DatabaseManager(db_path)
    shared_db.initialize_db()

    mid = shared_db.add_camera_model(**sample_model)
    cid = shared_db.add_client(sample_client)

    shared_db.save_serial_batch(mid, [f"SN-INIT-{i:03d}" for i in range(20)])

    thread_errors = []
    start_barrier = threading.Barrier(20)

    def shared_worker(tid):
        try:
            start_barrier.wait()
            for step in range(5):
                # Alternate between read and write operations
                if tid % 4 == 0:
                    a = shared_db.get_dashboard_analytics()
                    assert "total_stock" in a
                elif tid % 4 == 1:
                    s = shared_db.search_serials(query="INIT", model_id=mid)
                    assert isinstance(s, list)
                elif tid % 4 == 2:
                    shared_db.save_serial_batch(mid, [f"SN-SH-{tid}-{step}-{k}" for k in range(3)])
                else:
                    shared_db.update_model_threshold(mid, 5 + (step % 3))
        except Exception as e:
            thread_errors.append((f"shared-tid-{tid}", type(e).__name__, str(e)))

    threads = [threading.Thread(target=shared_worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    # Inspect whether SQLite threw ProgrammingError or cursor collisions
    assert len(thread_errors) == 0, (
        f"Shared instance concurrency errors detected ({len(thread_errors)}): {thread_errors[:5]}"
    )
    shared_db.close()


# ----------------------------------------------------------------------
# 6. Concurrent Mixed Valid & Poisoned Transactions (Rollback Isolation)
# ----------------------------------------------------------------------
def test_concurrent_mixed_valid_and_poisoned_transactions(temp_dir, sample_model, sample_client):
    """
    Adversarial test: 10 threads attempt valid operations while 10 threads simultaneously
    attempt poisoned operations that trigger rollbacks (duplicate doc_numbers, FK violations, duplicate serials).
    Asserts:
    1. Poisoned transactions are cleanly rejected and rolled back.
    2. Valid transactions are not corrupted or aborted by peer rollbacks.
    3. Final database state reflects exactly the successful transactions.
    """
    db_path = os.path.join(temp_dir, "mixed_rollback.db")
    db = DatabaseManager(db_path)
    db.initialize_db()

    mid = db.add_camera_model(**sample_model)
    cid = db.add_client(sample_client)
    db.close()

    thread_results = {"valid_success": 0, "poison_rejected": 0, "errors": []}
    lock = threading.Lock()
    barrier = threading.Barrier(20)

    # 10 Valid Workers: add distinct serials
    def valid_worker(tid):
        conn_db = DatabaseManager(db_path)
        barrier.wait()
        try:
            batch = [f"SN-VALID-W{tid}-{i}" for i in range(5)]
            cnt = conn_db.save_serial_batch(mid, batch)
            with lock:
                if cnt == 5:
                    thread_results["valid_success"] += 1
        except Exception as e:
            with lock:
                thread_results["errors"].append((f"valid-{tid}", str(e)))
        finally:
            conn_db.close()

    # 10 Poison Workers: trigger FK violations or duplicate doc_numbers
    def poison_worker(tid):
        conn_db = DatabaseManager(db_path)
        barrier.wait()
        try:
            if tid % 2 == 0:
                # Attempt to insert client with DUPLICATE doc_number
                dup_client = dict(sample_client)  # Same doc_number as initial client
                res = conn_db.add_client(dup_client)
                with lock:
                    if res == 0:
                        thread_results["poison_rejected"] += 1
            else:
                # Attempt to assign non-existent serial IDs (FK violation)
                res = conn_db.assign_cameras_batch(cid, [9999000 + tid, 9999100 + tid])
                with lock:
                    if res == 0:
                        thread_results["poison_rejected"] += 1
        except Exception as e:
            with lock:
                thread_results["errors"].append((f"poison-{tid}", str(e)))
        finally:
            conn_db.close()

    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=valid_worker, args=(i,)))
    for i in range(10):
        threads.append(threading.Thread(target=poison_worker, args=(i,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert len(thread_results["errors"]) == 0, f"Unexpected thread errors: {thread_results['errors']}"
    assert thread_results["valid_success"] == 10, f"Expected 10 valid successes, got {thread_results['valid_success']}"
    assert thread_results["poison_rejected"] == 10, f"Expected 10 poison rejections, got {thread_results['poison_rejected']}"

    # Verify final database state
    verify_db = DatabaseManager(db_path)
    cursor = verify_db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM serial_numbers WHERE serial_number LIKE 'SN-VALID-%';")
    assert cursor.fetchone()[0] == 50  # 10 threads * 5 serials

    cursor.execute("SELECT COUNT(*) FROM clients;")
    assert cursor.fetchone()[0] == 1  # No duplicate client was inserted

    cursor.execute("SELECT COUNT(*) FROM client_purchases;")
    assert cursor.fetchone()[0] == 0  # No poisoned purchases were inserted
    verify_db.close()


# ----------------------------------------------------------------------
# 7. Transaction Rollback Cleanliness on add_client & update_client
# ----------------------------------------------------------------------
def test_add_client_integrity_error_must_rollback_transaction(temp_dir, sample_client):
    """
    CRITICAL TRANSACTION BOUNDARY TEST:
    When add_client encounters an IntegrityError (e.g. duplicate doc_number),
    it MUST execute a clean rollback so the connection does not remain in an uncommitted
    transaction state (in_transaction=True). An uncommitted transaction leaks write locks,
    blocking other threads/connections for 5+ seconds until timeout.
    """
    db_path = os.path.join(temp_dir, "rollback_leak_test.db")
    db1 = DatabaseManager(db_path)
    db1.initialize_db()

    # 1. Insert first client successfully
    cid1 = db1.add_client(sample_client)
    assert cid1 > 0
    assert db1.conn.in_transaction is False, "in_transaction should be False after successful commit"

    # 2. Attempt duplicate insert -> triggers IntegrityError
    cid2 = db1.add_client(sample_client)
    assert cid2 == 0, f"Expected 0 for duplicate client, got {cid2}"

    # Assert that connection is NOT left in an open transaction
    assert db1.conn.in_transaction is False, (
        "Transaction leak bug detected: add_client failed to call self.conn.rollback() on IntegrityError, "
        "leaving db1.conn.in_transaction == True and holding a database lock!"
    )

    # 3. Connection 2 must be able to write immediately without waiting 5000ms
    db2 = DatabaseManager(db_path)
    t0 = time.time()
    mid = db2.add_camera_model("TEST-MODEL", "Des", "Nat", "Cat", "Sub")
    duration = time.time() - t0
    assert mid > 0, "db2 could not write because db1 holds an unrolled transaction lock"
    assert duration < 1.0, f"db2 was blocked for {duration:.2f}s due to unrolled transaction in db1"

    db1.close()
    db2.close()


def test_update_client_error_must_rollback_transaction(temp_dir, sample_client):
    """
    CRITICAL TRANSACTION BOUNDARY TEST:
    When update_client encounters an error (e.g. duplicate doc_number constraint violation),
    it MUST execute self.conn.rollback() so the connection does not hold a lock.
    """
    db_path = os.path.join(temp_dir, "rollback_update_leak.db")
    db1 = DatabaseManager(db_path)
    db1.initialize_db()

    c1 = db1.add_client(sample_client)
    client2 = dict(sample_client)
    client2["doc_number"] = "DOC-SECOND-CLIENT"
    c2 = db1.add_client(client2)

    # Attempt updating c2 to c1's doc_number -> UNIQUE constraint violation
    res = db1.update_client(c2, {"doc_number": sample_client["doc_number"]})
    assert res is False, "update_client should return False on constraint failure"

    assert db1.conn.in_transaction is False, (
        "Transaction leak bug detected: update_client failed to call self.conn.rollback() on sqlite3.Error, "
        "leaving db1.conn.in_transaction == True and holding a database lock!"
    )

    db2 = DatabaseManager(db_path)
    t0 = time.time()
    mid = db2.add_camera_model("TEST-MODEL2", "Des", "Nat", "Cat", "Sub")
    duration = time.time() - t0
    assert mid > 0, "db2 could not write because db1 holds an unrolled transaction lock"
    assert duration < 1.0, f"db2 was blocked for {duration:.2f}s due to unrolled transaction in db1"

    db1.close()
    db2.close()

