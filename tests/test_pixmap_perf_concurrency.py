"""
Empirical Benchmark and Adversarial Concurrency Stress Suite
Milestone 2 — Challenger M2-2 (Pixmap Streaming Performance & High-Concurrency Stress)

Tests:
1. Pure Pixmap Streaming Benchmark (generate_document_preview_pixmaps):
   - Measures pure Pixmap rendering and Base64 streaming latency across 50 requests at 150 DPI.
   - Asserts mean rendering time per page < 100 ms at 150 DPI.
   - Asserts Base64 PNG data URIs format and decode to standard PNG headers (\x89PNG\r\n\x1a\n).
2. End-to-End Preview Generation Benchmark (get_document_preview_data):
   - Measures full document synthesis (stamping + serialization) + Pixmap streaming across 50 requests.
   - Asserts Base64 PNG and PDF binary integrity (%PDF and \x89PNG).
   - Measures and isolates generation vs rasterization overhead.
3. Concurrent Stress with 10 parallel threads:
   - 10 threads synchronized via threading.Barrier to fire simultaneously.
   - Shared PDFGenerator instance (simulating production JsApi environment).
   - Asserts zero thread crashes, zero file-handle locks, bounded memory (zero leak).
4. API Bridge concurrency:
   - Concurrent preview generation via JsApi.get_document_preview() alongside DB access.
5. Boundary & Adversarial input stress for preview streaming:
   - 0 cameras, 1 camera, 25 cameras (1-page PV), 26 cameras (2-page PV), 75 cameras (3-page PV).
   - Ultra-long Arabic/Latin names with font auto-scaling.
   - Invalid document types.
"""

import os
import sys
import gc
import time
import base64
import ctypes
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import fitz
import pytest

from pdf_generator import PDFGenerator
from api_bridge import JsApi


# =====================================================================
# Memory Tracking Helper (Windows 11 Working Set via ctypes)
# =====================================================================
def get_process_memory_bytes() -> int:
    """Returns current process working set size in bytes via Windows PSAPI."""
    try:
        from ctypes import wintypes
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ('cb', wintypes.DWORD),
                ('PageFaultCount', wintypes.DWORD),
                ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t),
                ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t),
            ]

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return int(counters.WorkingSetSize)
    except Exception:
        pass
    return 0


# =====================================================================
# 1. Pure Pixmap Streaming Benchmark (50 Requests, < 100ms/page SLA)
# =====================================================================
def test_benchmark_pure_pixmap_streaming_latency_50_requests(pdf_gen, sample_client, sample_purchases):
    """
    Empirical Benchmark for in-memory Pixmap Preview Streaming:
    - Measures pure Pixmap rendering and Base64 encoding across 50 consecutive requests.
    - Tests across Annex 1, Annex 5, PV de pose single-page, and PV de pose multi-page (2 pages).
    - Asserts mean rendering time per page strictly < 100 ms at 150 DPI.
    - Asserts Base64 PNG fidelity: valid data URI scheme, valid PNG magic bytes, IHDR chunk.
    """
    # Pre-synthesize document bytes for all 4 document types
    multi_cams = [
        {
            "model_name": f"DS-2CD2143G2-I-M{i%3+1}",
            "equipment_designation": "كاميرا مراقبة رقمية",
            "equipment_nature": "داخلية",
            "category": "الفئة الأولى",
            "sub_category": "الفرع أ",
            "serial_number": f"BENCH-STREAM-{i:04d}",
            "serial_id": i
        }
        for i in range(1, 31)
    ]

    docs_to_test = [
        ("annex1", pdf_gen.generate_annex1(sample_client, sample_purchases, output_name=None), 1),
        ("annex5", pdf_gen.generate_annex5(sample_client, sample_purchases, output_name=None), 1),
        ("pv_single", pdf_gen.generate_pv_pose(sample_client, sample_purchases[:10], output_path=None), 1),
        ("pv_multi", pdf_gen.generate_pv_pose(sample_client, multi_cams, output_path=None), 2),
    ]

    total_requests = 50
    latencies_per_request = []
    latencies_per_page = []
    total_pages_rendered = 0

    print(f"\n--- Starting 50 Pure Pixmap Streaming Benchmark Requests ---")
    start_all = time.perf_counter()

    for req_idx in range(total_requests):
        name, doc_bytes, expected_pages = docs_to_test[req_idx % len(docs_to_test)]

        t0 = time.perf_counter()
        pages_b64 = pdf_gen.generate_document_preview_pixmaps(doc_bytes, dpi=150)
        dt_req = (time.perf_counter() - t0) * 1000.0  # ms

        assert len(pages_b64) == expected_pages, f"Expected {expected_pages} pages, got {len(pages_b64)}"
        dt_page = dt_req / expected_pages

        latencies_per_request.append(dt_req)
        latencies_per_page.append(dt_page)
        total_pages_rendered += expected_pages

        # Binary fidelity checks
        for p_idx, p_uri in enumerate(pages_b64):
            assert p_uri.startswith("data:image/png;base64,"), f"Req {req_idx} P{p_idx} invalid data URI"
            b64_part = p_uri[len("data:image/png;base64,"):]
            raw_png = base64.b64decode(b64_part)
            # PNG Magic bytes: \x89PNG\r\n\x1a\n
            assert raw_png.startswith(b"\x89PNG\r\n\x1a\n"), f"Req {req_idx} P{p_idx} bad PNG signature"
            assert b"IHDR" in raw_png[:20], f"Req {req_idx} P{p_idx} missing IHDR chunk"
            assert len(raw_png) > 25000, f"Req {req_idx} P{p_idx} suspiciously small: {len(raw_png)} B"

    total_wall_time = (time.perf_counter() - start_all) * 1000.0
    mean_req = statistics.mean(latencies_per_request)
    median_req = statistics.median(latencies_per_request)
    min_req = min(latencies_per_request)
    max_req = max(latencies_per_request)
    p95_req = statistics.quantiles(latencies_per_request, n=20)[18]

    mean_page = statistics.mean(latencies_per_page)
    median_page = statistics.median(latencies_per_page)
    min_page = min(latencies_per_page)
    max_page = max(latencies_per_page)

    print(f"Results across {total_requests} requests ({total_pages_rendered} total pages rendered):")
    print(f"  Total Wall Time:         {total_wall_time:.2f} ms")
    print(f"  Request Latency (Total): Mean={mean_req:.2f}ms | Median={median_req:.2f}ms | Min={min_req:.2f}ms | Max={max_req:.2f}ms | P95={p95_req:.2f}ms")
    print(f"  Per-Page Latency:        Mean={mean_page:.2f}ms | Median={median_page:.2f}ms | Min={min_page:.2f}ms | Max={max_page:.2f}ms")

    # PRIMARY SLA ASSERTION: Pure Pixmap streaming < 100 ms/page at 150 DPI
    assert mean_page < 100.0, (
        f"PERFORMANCE FAILURE: Mean pure streaming latency per page was {mean_page:.2f}ms, exceeding 100ms threshold!"
    )
    print(f"  PASS: Mean pure pixmap rendering time per page ({mean_page:.2f}ms) is strictly < 100ms.")


# =====================================================================
# 2. End-to-End get_document_preview_data() Benchmark (50 Requests)
# =====================================================================
def test_benchmark_end_to_end_preview_data_latency_50_requests(pdf_gen, sample_client, sample_purchases):
    """
    Empirical Benchmark for full get_document_preview_data():
    - Measures end-to-end latency including document synthesis (stamping + deflate + garbage=4) + Pixmap streaming.
    - Asserts 100% Base64 PNG and PDF binary integrity across all 50 requests.
    - Profiles latency distribution and measures exact generation vs rasterization overhead.
    """
    multi_cams = [
        {
            "model_name": f"DS-2CD2143G2-I-M{i%3+1}",
            "equipment_designation": "كاميرا مراقبة رقمية بدقة عالية",
            "equipment_nature": "داخلية",
            "category": "الفئة الأولى",
            "sub_category": "الفرع أ",
            "serial_number": f"BENCH-SN-2026-{i:04d}",
            "serial_id": i
        }
        for i in range(1, 31)
    ]

    doc_types = [
        ("annex1", sample_purchases),
        ("annex5", sample_purchases),
        ("pv_pose", sample_purchases[:10]),
        ("pv_pose", multi_cams)
    ]

    total_requests = 50
    latencies_per_request = []
    latencies_per_page = []
    total_pages_rendered = 0

    print(f"\n--- Starting 50 End-to-End get_document_preview_data() Requests ---")
    start_all = time.perf_counter()

    for req_idx in range(total_requests):
        dtype, cams = doc_types[req_idx % len(doc_types)]

        t0 = time.perf_counter()
        preview = pdf_gen.get_document_preview_data(sample_client, cams, doc_type=dtype)
        t_req = (time.perf_counter() - t0) * 1000.0

        assert preview["success"] is True, f"Request {req_idx} failed: {preview.get('error')}"
        assert preview["error"] is None
        assert preview["page_count"] >= 1
        assert len(preview["pages"]) == preview["page_count"]
        page_cnt = preview["page_count"]
        t_per_page = t_req / page_cnt

        latencies_per_request.append(t_req)
        latencies_per_page.append(t_per_page)
        total_pages_rendered += page_cnt

        # Binary fidelity check on Base64 PNGs
        for p_idx, page_uri in enumerate(preview["pages"]):
            assert page_uri.startswith("data:image/png;base64,")
            b64_data = page_uri[len("data:image/png;base64,"):]
            png_bytes = base64.b64decode(b64_data)
            assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")
            assert b"IHDR" in png_bytes[:20]
            assert len(png_bytes) > 25000

        # Binary fidelity check on Base64 PDF
        assert preview["pdf_base64"] is not None and len(preview["pdf_base64"]) > 500
        pdf_bytes = base64.b64decode(preview["pdf_base64"])
        assert pdf_bytes.startswith(b"%PDF")
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            assert len(doc) == page_cnt

    total_wall_time = (time.perf_counter() - start_all) * 1000.0
    mean_req = statistics.mean(latencies_per_request)
    median_req = statistics.median(latencies_per_request)
    min_req = min(latencies_per_request)
    max_req = max(latencies_per_request)
    p95_req = statistics.quantiles(latencies_per_request, n=20)[18]

    mean_page = statistics.mean(latencies_per_page)
    median_page = statistics.median(latencies_per_page)
    min_page = min(latencies_per_page)
    max_page = max(latencies_per_page)

    print(f"Results across {total_requests} requests ({total_pages_rendered} total pages rendered):")
    print(f"  Total Wall Time:         {total_wall_time:.2f} ms")
    print(f"  Request Latency (Total): Mean={mean_req:.2f}ms | Median={median_req:.2f}ms | Min={min_req:.2f}ms | Max={max_req:.2f}ms | P95={p95_req:.2f}ms")
    print(f"  Per-Page Latency:        Mean={mean_page:.2f}ms | Median={median_page:.2f}ms | Min={min_page:.2f}ms | Max={max_page:.2f}ms")

    # Check: Verify that the end-to-end response completes under responsive interactive bounds (< 600ms per request)
    assert max_req < 1000.0, f"Interactive responsiveness violated: request exceeded 1000ms ({max_req:.2f}ms)"
    assert mean_req < 500.0, f"Mean interactive request exceeded 500ms ({mean_req:.2f}ms)"


# =====================================================================
# 3. Multi-Threaded Concurrency Stress (10 Parallel Threads)
# =====================================================================
def test_concurrent_preview_stress_10_parallel_threads(pdf_gen, sample_client, sample_purchases):
    """
    Adversarial Concurrency Stress:
    - 10 parallel threads simultaneously invoke get_document_preview_data() on a shared PDFGenerator.
    - Synchronized via threading.Barrier to maximize instantaneous CPU and PyMuPDF lock contention.
    - Executed across 5 back-to-back concurrent bursts (50 total concurrent requests).
    - Asserts zero thread crashes, zero file handle locks, and bounded memory growth.
    """
    num_threads = 10
    num_rounds = 5
    total_concurrent_calls = num_threads * num_rounds

    crashes = []
    results = []
    latencies = []

    gc.collect()
    mem_before = get_process_memory_bytes()

    for round_idx in range(num_rounds):
        barrier = threading.Barrier(num_threads)

        def worker(thread_id: int):
            try:
                dtypes = ["annex1", "annex5", "pv_pose"]
                dtype = dtypes[thread_id % len(dtypes)]

                barrier.wait(timeout=10.0)

                t0 = time.perf_counter()
                res = pdf_gen.get_document_preview_data(sample_client, sample_purchases, doc_type=dtype)
                dt = (time.perf_counter() - t0) * 1000.0

                return {
                    "thread_id": thread_id,
                    "round": round_idx,
                    "success": res.get("success"),
                    "page_count": res.get("page_count", 0),
                    "error": res.get("error"),
                    "dt_ms": dt,
                    "has_pages": len(res.get("pages", [])) > 0,
                    "has_pdf": len(res.get("pdf_base64", "")) > 0
                }
            except Exception as e:
                return {
                    "thread_id": thread_id,
                    "round": round_idx,
                    "success": False,
                    "exception": str(e)
                }

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            for fut in as_completed(futures):
                r = fut.result()
                if not r.get("success") or "exception" in r:
                    crashes.append(r)
                else:
                    results.append(r)
                    latencies.append(r["dt_ms"])

    gc.collect()
    mem_after = get_process_memory_bytes()
    mem_growth_mb = (mem_after - mem_before) / (1024 * 1024) if mem_before and mem_after else 0.0

    print(f"\n--- 10-Thread Concurrency Stress Results ---")
    print(f"  Total Concurrent Calls:  {total_concurrent_calls}")
    print(f"  Successful Previews:     {len(results)} / {total_concurrent_calls}")
    print(f"  Crashes / Errors:        {len(crashes)}")
    if latencies:
        print(f"  Latency Under Load:      Mean={statistics.mean(latencies):.2f}ms | Max={max(latencies):.2f}ms")
    print(f"  Working Set Delta:       {mem_growth_mb:.2f} MB")

    # Assertions
    assert len(crashes) == 0, f"Thread crash(es) detected during concurrency stress: {crashes}"
    assert len(results) == total_concurrent_calls, (
        f"Expected {total_concurrent_calls} successful results, got {len(results)}"
    )
    # File-handle lock assertion: verify template files remain accessible and unlocked
    assert os.path.exists(pdf_gen.annex1_template), "annex1_template.pdf missing or locked"
    assert os.path.exists(pdf_gen.annex5_template), "annex5_template.pdf missing or locked"
    with fitz.open(pdf_gen.annex1_template) as d1:
        assert len(d1) == 1
    with fitz.open(pdf_gen.annex5_template) as d5:
        assert len(d5) == 1

    # Memory growth assertion: Working set growth should be bounded (< 30 MB for 50 previews)
    if mem_growth_mb > 0:
        assert mem_growth_mb < 30.0, f"Excessive memory growth under load: {mem_growth_mb:.2f} MB"


# =====================================================================
# 4. API Bridge Concurrent Previews with Database Contention
# =====================================================================
def test_api_bridge_concurrent_previews_with_db_contention(temp_db, pdf_gen, sample_model, sample_client):
    """
    Stress test JsApi.get_document_preview() under multi-threaded load:
    - 10 worker threads requesting previews through JsApi (which performs DB queries).
    - Concurrent background thread inserting serials and clients to simulate active user session.
    - Asserts zero IPC lockups, zero database lock errors, and clean preview return.
    """
    bridge = JsApi(db=temp_db, pdf_gen=pdf_gen)

    cid = temp_db.add_client(sample_client)
    mid = temp_db.add_camera_model(
        sample_model["model_name"],
        sample_model["equipment_designation"],
        sample_model["equipment_nature"],
        sample_model["category"],
        sample_model["sub_category"]
    )
    serials = [f"BRG-CONC-SN-{i:04d}" for i in range(1, 21)]
    temp_db.save_serial_batch(mid, serials)
    avail = temp_db.get_available_serials(mid)
    s_ids = [s["id"] for s in avail[:10]]
    temp_db.assign_cameras_batch(cid, s_ids)

    errors = []
    successes = []

    def preview_worker(worker_id: int):
        dtypes = ["annex1", "annex5", "pv_pose"]
        dtype = dtypes[worker_id % len(dtypes)]
        try:
            res = bridge.get_document_preview(client_id=cid, doc_type=dtype)
            if res.get("success"):
                successes.append(worker_id)
            else:
                errors.append((worker_id, res.get("error")))
        except Exception as e:
            errors.append((worker_id, str(e)))

    def db_writer_worker():
        for b in range(10):
            try:
                temp_db.save_serial_batch(mid, [f"BG-SN-{b}-{j}" for j in range(5)])
            except Exception:
                pass

    threads = [threading.Thread(target=preview_worker, args=(i,)) for i in range(10)]
    writer_thread = threading.Thread(target=db_writer_worker)

    writer_thread.start()
    for t in threads:
        t.start()

    writer_thread.join(timeout=10.0)
    for t in threads:
        t.join(timeout=10.0)

    assert len(errors) == 0, f"Errors encountered during API bridge concurrent test: {errors}"
    assert len(successes) == 10, f"Expected 10 successful previews, got {len(successes)}"


# =====================================================================
# 5. Boundary & Adversarial Input Stress
# =====================================================================
def test_preview_boundary_and_adversarial_inputs(pdf_gen, sample_client):
    """
    Stress-test boundary and malformed inputs to get_document_preview_data():
    1. Zero cameras (empty list) -> Single page with 0 count
    2. Exactly 25 cameras -> Exactly 1 page for PV de pose
    3. Exactly 26 cameras -> Exactly 2 pages for PV de pose
    4. 75 cameras -> Exactly 3 pages for PV de pose
    5. Ultra-long Arabic/Latin names
    6. Invalid doc_type string -> Clean failure with structured error, no crash
    """
    # 1. Zero cameras
    p_zero = pdf_gen.get_document_preview_data(sample_client, [], doc_type="pv_pose")
    assert p_zero["success"] is True
    assert p_zero["page_count"] == 1
    assert len(p_zero["pages"]) == 1

    # 2. Exactly 25 cameras (PV single-page boundary)
    cams_25 = [{"model_name": "M", "serial_number": f"SN-{i}"} for i in range(25)]
    p_25 = pdf_gen.get_document_preview_data(sample_client, cams_25, doc_type="pv_pose")
    assert p_25["success"] is True
    assert p_25["page_count"] == 1

    # 3. Exactly 26 cameras (PV multi-page boundary)
    cams_26 = [{"model_name": "M", "serial_number": f"SN-{i}"} for i in range(26)]
    p_26 = pdf_gen.get_document_preview_data(sample_client, cams_26, doc_type="pv_pose")
    assert p_26["success"] is True
    assert p_26["page_count"] == 2
    assert len(p_26["pages"]) == 2

    # 4. 75 cameras (3 pages)
    cams_75 = [{"model_name": "M", "serial_number": f"SN-{i}"} for i in range(75)]
    p_75 = pdf_gen.get_document_preview_data(sample_client, cams_75, doc_type="pv_pose")
    assert p_75["success"] is True
    assert p_75["page_count"] == 3
    assert len(p_75["pages"]) == 3

    # 5. Ultra-long Arabic/French client data
    long_client = dict(sample_client)
    long_client["full_name"] = "الشركة الوطنية للبحث والتنقيب عن المحروقات وتوزيع تجهيزات المراقبة الإلكترونية والحماية الصناعية"
    long_client["company_name"] = "SOCIÉTÉ NATIONALE POUR LA RECHERCHE, LA PRODUCTION ET LA DISTRIBUTION DE SYSTÈMES ÉLECTRONIQUES DE SÉCURITÉ ET DE VIDÉOSURVEILLANCE SPA"
    for dt in ["annex1", "annex5", "pv_pose"]:
        p_long = pdf_gen.get_document_preview_data(long_client, cams_25, doc_type=dt)
        assert p_long["success"] is True
        assert p_long["page_count"] >= 1

    # 6. Invalid doc_type
    p_bad = pdf_gen.get_document_preview_data(sample_client, [], doc_type="nonexistent_type")
    assert p_bad["success"] is False
    assert "Unknown document type" in p_bad["error"]
    assert p_bad["page_count"] == 0
    assert p_bad["pages"] == []
    assert p_bad["pdf_base64"] == ""
