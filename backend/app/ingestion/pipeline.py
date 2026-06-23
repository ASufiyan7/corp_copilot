import json
import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.database import documents
from app.ingestion.parser import strip_html, chunk_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "AMZN": "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc."
}

def get_manifest_path() -> Path:
    """
    Resolve the absolute path to the data manifest.
    Navigates up from app/ingestion/pipeline.py to project root, then to data/downloads/manifest.json.
    """
    # parents[0] = app/ingestion
    # parents[1] = app
    # parents[2] = backend
    # parents[3] = Doc_Copilot (project root)
    return Path(__file__).resolve().parents[3] / "data" / "downloads" / "manifest.json"

def ingest_all_filings():
    manifest_path = get_manifest_path()
    if not manifest_path.exists():
        logger.error(f"Manifest file not found at {manifest_path}. Please run download script first.")
        return

    logger.info(f"Loading manifest from {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    filings = manifest.get("filings", [])
    logger.info(f"Found {len(filings)} filings to process.")

    db: Session = SessionLocal()
    try:
        for idx, filing in enumerate(filings, start=1):
            ticker = filing["ticker"]
            form = filing["form"]
            filing_date_str = filing["filing_date"]
            filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d").date()
            local_path_str = filing["local_path"]
            source_url = filing.get("source_url")
            
            # Resolve filing local path
            downloads_dir = manifest_path.parent
            local_file_path = downloads_dir / local_path_str

            if not local_file_path.exists():
                logger.warning(f"[{idx}/{len(filings)}] Filing file not found at {local_file_path}. Skipping.")
                continue

            logger.info(f"[{idx}/{len(filings)}] Processing {ticker} {form} ({filing_date_str})...")

            # Read HTML content
            with open(local_file_path, "r", encoding="utf-8") as html_file:
                html_content = html_file.read()

            # Clean and strip HTML
            clean_text = strip_html(html_content)
            logger.info(f"Stripped HTML. Text length: {len(clean_text)} characters.")

            # Make ingestion idempotent: delete existing document and chunks if they already exist
            existing_doc = documents.get_document_by_ticker_and_type(
                db=db,
                ticker=ticker,
                filing_type=form,
                filing_date=filing_date
            )
            if existing_doc:
                logger.info(f"Filing already exists in database. Deleting old document (ID: {existing_doc.id}) for clean overwrite.")
                documents.delete_document(db, existing_doc.id)

            # Store the SourceDocument in the database
            company_name = COMPANY_NAMES.get(ticker, f"{ticker} Corp")
            doc = documents.create_document(
                db=db,
                ticker=ticker,
                company_name=company_name,
                filing_type=form,
                filing_date=filing_date,
                content=clean_text,
                source_url=source_url
            )

            # Chunk the content
            chunks = chunk_text(clean_text)
            logger.info(f"Generated {len(chunks)} chunks.")

            # Store DocumentChunks in bulk
            # In Phase 5, embeddings are mocked as a 384-dimensional zeros vector
            mock_embedding = [0.0] * 384
            chunks_data = [
                {
                    "document_id": doc.id,
                    "chunk_index": chunk_idx,
                    "chunk_text": chunk_content,
                    "embedding": mock_embedding,
                    "chunk_metadata": {
                        "ticker": ticker,
                        "form": form,
                        "filing_date": filing_date_str,
                        "chunk_length": len(chunk_content)
                    }
                }
                for chunk_idx, chunk_content in enumerate(chunks)
            ]

            documents.create_document_chunks_bulk(db, chunks_data)
            logger.info(f"Successfully stored document and {len(chunks_data)} chunks in database.")

        logger.info("Ingestion pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Error during ingestion pipeline execution: {e}", exc_info=True)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    ingest_all_filings()
