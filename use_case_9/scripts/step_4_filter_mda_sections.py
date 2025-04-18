import os
import numpy as np
import concurrent.futures
from time import sleep
from multiprocessing import Pool
from typing import List, Dict, Any

from retrieval.embedder import get_embedding
from utils.file_handler import load_json, save_json

max_chunk_length = 8000
search_queries = ["cyber risk"]
embedding_model = "text-embedding-3-small"
embedding_max_workers = 8  


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    return 0.0 if denom == 0 else float(np.dot(v1, v2) / denom)


def segment_text_by_sentence(text: str, max_length: int = max_chunk_length) -> List[str]:
    chunks, remaining = [], text.strip()
    while len(remaining) > max_length:
        idx = remaining.rfind(".", 0, max_length)
        idx = idx + 1 if idx != -1 else max_length
        chunks.append(remaining[:idx].strip())
        remaining = remaining[idx:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def _safe_get_embedding(text: str, model: str) -> Any:
    try:
        return get_embedding(text, model=model)
    except Exception as e:
        print(f"[WARN] embedding failure: {e}")
        return None


def _embed_texts_parallel(
    texts: List[str], model: str, max_workers: int
) -> List[Any]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as exe:
        return list(exe.map(lambda t: _safe_get_embedding(t, model), texts))


def create_and_embed_chunks(
    segmented_file: str,
    *,
    max_length: int = max_chunk_length,
    model: str = embedding_model,
    embedding_workers: int = embedding_max_workers,
) -> List[Dict[str, Any]]:
    """
    Read segmented_file, split sections into chunks, embed them in parallel,
    and return the list of chunk dicts. Does NOT write any chunk JSON to disk.
    """
    if not os.path.isfile(segmented_file):
        print(f"File not found: {segmented_file}")
        return []

    sections = load_json(segmented_file)
    results: List[Dict[str, Any]] = []

    for s_idx, section in enumerate(sections, 1):
        base_id = f"{s_idx:02d}"
        chunks = segment_text_by_sentence(section.get("section_text", ""), max_length)

        embeddings = _embed_texts_parallel(chunks, model=model, max_workers=embedding_workers)

        for c_idx, (chunk, emb) in enumerate(zip(chunks, embeddings), 1):
            chunk_id = f"{base_id}-{c_idx}"
            results.append({
                "chunk_id": chunk_id,
                "section_title": section.get("section_title", "untitled"),
                "chunk_text": chunk,
                "embedding": emb,
            })

        sleep(0.1)

    return results


def section_matches_keywords(chunk: Dict[str, Any], keywords: List[str]) -> bool:
    title = chunk.get("section_title", "").lower()
    text = chunk.get("chunk_text", "").lower()
    return any(kw in title or kw in text for kw in keywords)


def filter_chunks_by_keywords(
    chunks: List[Dict[str, Any]],
    keywords: List[str],
) -> List[Dict[str, Any]]:
    """
    Return the chunks whose title or text contains any of the keywords.
    """
    return [chunk for chunk in chunks if section_matches_keywords(chunk, keywords)]


def semantic_search(
    chunks: List[Dict[str, Any]],
    queries: List[str],
    *,
    top_n: int = 5,
    model: str = embedding_model,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    For each query, compute its embedding and return the top_n most
    similar chunks by cosine similarity.
    """
    output: Dict[str, List[Dict[str, Any]]] = {}
    for q in queries:
        try:
            q_emb = get_embedding(q, model=model)
        except Exception as e:
            print(f"[WARN] embedding failure for query '{q}': {e}")
            output[q] = []
            continue

        sims = []
        for ch in chunks:
            emb = ch.get("embedding")
            if emb is None:
                continue
            sims.append({**ch, "similarity": cosine_similarity(q_emb, emb)})
        output[q] = sorted(sims, key=lambda x: x["similarity"], reverse=True)[:top_n]
        sleep(0.1)
    return output


def process_single_file(args) -> None:
    fname, mda_sections_output_dir = args
    base, _ = os.path.splitext(fname)
    idx = base.replace("mda_sections_segmented_annual_report_", "").strip()

    segmented_path = os.path.join(mda_sections_output_dir, fname)
    filtered_path = os.path.join(
        mda_sections_output_dir,
        f"mda_sections_filtered_annual_report_{idx}.json"
    )

    print(f"\n─── Processing {segmented_path}")

    chunks = create_and_embed_chunks(
        segmented_path,
        model=embedding_model,
        embedding_workers=embedding_max_workers,
    )
    if not chunks:
        return

    keyword_hits = filter_chunks_by_keywords(chunks, search_queries)

    sem_hits = semantic_search(chunks, search_queries, top_n=5, model=embedding_model)

    section_codes = {
        ch["chunk_id"].split("-")[0]
        for ch in keyword_hits
    } | {
        ch["chunk_id"].split("-")[0]
        for hits in sem_hits.values()
        for ch in hits
    }

    original_sections = load_json(segmented_path)
    filtered_sections = [
        sec for i, sec in enumerate(original_sections, 1)
        if f"{i:02d}" in section_codes
    ]

    save_json(filtered_sections, filtered_path)
    print(
        f"{len(filtered_sections)} section(s) matched on '{search_queries[0]}'. "
        f"Full text written to {filtered_path}"
    )


def filter_mda_sections(mda_sections_output_dir: str) -> None:
    segmented_files = sorted(
        f for f in os.listdir(mda_sections_output_dir)
        if f.startswith("mda_sections_segmented_annual_report_")
        and f.endswith(".json")
        and "_chunks" not in f
    )

    if not segmented_files:
        print("[INFO] No segmented annual‑report files found.")
        return

    with Pool(processes=min(5, len(segmented_files))) as pool:
        pool.map(
            process_single_file,
            [(f, mda_sections_output_dir) for f in segmented_files]
        )