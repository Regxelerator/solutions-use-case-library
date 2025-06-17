import os, sys
from dotenv import load_dotenv

from services.graph_client import MSGraphClient
from processors.extraction_pipeline import run_document_extraction_pipeline
from processors.validation_pipeline import run_validation_pipeline

load_dotenv()

def print_help() -> None:
    print(
        "\nUsage:\n"
        "  python main.py run '<entity_name>'   # end-to-end for one entity\n"
        "  python main.py help                  # this message\n"
    )

def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1].lower() == "help":
        print_help();  sys.exit(0)

    if sys.argv[1].lower() != "run" or len(sys.argv) != 3:
        print("Incorrect arguments.");  print_help();  sys.exit(1)

    entity = sys.argv[2].strip()
    if not entity:
        print("<entity_name> must be non-empty.");  sys.exit(1)

    graph = MSGraphClient(
        tenant_id     = os.getenv("TENANT_ID"),
        client_id     = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
    )
    site_id  = graph.get_site_id(os.getenv("HOSTNAME"), os.getenv("SITE_PATH_1"))
    drive_id = graph.get_drive_id(site_id, os.getenv("LIBRARY_NAME_SITE_PATH_1"))

    run_document_extraction_pipeline(graph, site_id, drive_id, entity_name=entity)

    run_validation_pipeline(graph, entity_name=entity)

    print("\nEnd-to-end pipeline finished successfully.")


if __name__ == "__main__":
    main()