import os
import json
import sys
import logging
import traceback
import shutil
import subprocess
from mcp.server.fastmcp import FastMCP
import socket
import threading

DATA_DIR = "/data"
PROJECTS_INDEX_PATH = os.path.join(DATA_DIR, "projects_index.json")
LOG_PATH = os.path.join(DATA_DIR, "mcp_debug.log")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)

def load_projects():
    print(f"Loading projects index from {PROJECTS_INDEX_PATH}", file=sys.stderr)
    if os.path.exists(PROJECTS_INDEX_PATH):
        try:
            with open(PROJECTS_INDEX_PATH, "r") as f:
                projects = json.load(f)
                print(f"Loaded {len(projects)} projects from index", file=sys.stderr)
                return projects
        except Exception as e:
            print(f"Error loading projects index: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    print("Using default projects", file=sys.stderr)
    return [
        {"id": "project1", "name": "Sample Project 1", "path": "/path/to/sample1"},
        {"id": "project2", "name": "Sample Project 2", "path": "/path/to/sample2"},
    ]

def save_projects(projects):
    print(f"Saving {len(projects)} projects to index", file=sys.stderr)
    try:
        with open(PROJECTS_INDEX_PATH, "w") as f:
            json.dump(projects, f)
        print(f"Projects index saved successfully", file=sys.stderr)
    except Exception as e:
        print(f"Error saving projects index: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

def create_project_folder(project_id, project_data):
    """Create a folder for the project and store its metadata."""
    project_dir = os.path.join(DATA_DIR, project_id)
    metadata_path = os.path.join(project_dir, "metadata.json")
    
    print(f"Creating project folder: {project_dir}", file=sys.stderr)
    try:
        os.makedirs(project_dir, exist_ok=True)
        
        with open(metadata_path, "w") as f:
            json.dump(project_data, f)
        
        print(f"Project metadata saved to {metadata_path}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error creating project folder: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

def remove_project_folder(project_id):
    """Remove a project folder and all its contents."""
    project_dir = os.path.join(DATA_DIR, project_id)
    
    print(f"Removing project folder: {project_dir}", file=sys.stderr)
    try:
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
            print(f"Project folder {project_dir} removed successfully", file=sys.stderr)
            return True
        else:
            print(f"Project folder {project_dir} not found", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Error removing project folder: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

def get_host_ip():
    # Try to get the default gateway IP (host IP from container's perspective)
    try:
        route = subprocess.check_output(['ip', 'route']).decode()
        for line in route.splitlines():
            if line.startswith('default'):
                parts = line.split()
                gw_index = parts.index('via') + 1
                return parts[gw_index]
    except Exception as e:
        logging.error(f"Failed to auto-detect host IP: {e}")
    return 'localhost'

mcp = FastMCP("Dependency Analyzer")
projects = load_projects()

@mcp.tool()
def list_projects() -> list:
    logging.debug(f"list_projects called, returning {len(projects)} projects")
    print(f"list_projects called, returning {len(projects)} projects", file=sys.stderr)
    return projects

@mcp.tool()
def add_project(name: str, path: str) -> dict:
    logging.debug(f"add_project called with name={name}, path={path}")
    print(f"add_project called with name={name}, path={path}", file=sys.stderr)

    # Path validation
    if not os.path.exists(path):
        error_msg = f"Provided path does not exist: {path}"
        logging.error(error_msg)
        return {"success": False, "error": error_msg, "path_verified": False}
    if not os.path.isdir(path):
        error_msg = f"Provided path is not a directory: {path}"
        logging.error(error_msg)
        return {"success": False, "error": error_msg, "path_verified": False}

    new_id = f"project{len(projects)+1}"
    project = {"id": new_id, "name": name, "path": path}

    # Create project folder and store metadata
    if create_project_folder(new_id, project):
        # Add to projects list
        projects.append(project)
        logging.debug(f"Current projects: {projects}")
        print(f"Current projects after adding: {len(projects)} projects", file=sys.stderr)
        # Save updated projects index
        try:
            save_projects(projects)
            logging.debug(f"Saved projects index")
        except Exception as e:
            logging.error(f"Failed to save projects index: {str(e)}")
            print(f"Failed to save projects index: {str(e)}", file=sys.stderr)
    else:
        logging.error(f"Failed to create project folder for {new_id}")

    # Start dependency analysis in the background
    def run_analysis():
        try:
            analyze_dependencies(new_id)
        except Exception as e:
            logging.error(f"Background analysis failed for {new_id}: {e}")
    threading.Thread(target=run_analysis, daemon=True).start()

    return {
        "success": True,
        "project": project,
        "path_verified": True,
        "message": "Dependency analysis is running in the background."
    }

@mcp.tool()
def forget_project(project_id: str) -> dict:
    logging.debug(f"forget_project called for project_id={project_id}")
    print(f"forget_project called for project_id={project_id}", file=sys.stderr)
    
    # Find the project in the list
    project = next((p for p in projects if p["id"] == project_id), None)
    
    if not project:
        error_msg = f"Project not found: {project_id}"
        logging.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Store project data for return value
    removed_project = project.copy()
    
    # Remove from projects list
    projects[:] = [p for p in projects if p["id"] != project_id]
    logging.debug(f"Removed project {project_id} from projects list")
    print(f"Removed project {project_id} from projects list", file=sys.stderr)
    
    # Save updated projects index
    try:
        save_projects(projects)
        logging.debug(f"Saved updated projects index")
    except Exception as e:
        error_msg = f"Failed to save projects index: {str(e)}"
        logging.error(error_msg)
        print(error_msg, file=sys.stderr)
        # Continue anyway to try to remove the folder
    
    # Remove project folder and metadata
    project_dir = os.path.join(DATA_DIR, project_id)
    metadata_path = os.path.join(project_dir, "metadata.json")
    folder_removed = False
    try:
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
            folder_removed = True
            print(f"Project folder {project_dir} removed successfully", file=sys.stderr)
        else:
            print(f"Project folder {project_dir} not found", file=sys.stderr)
        # Remove metadata file if it exists (should be in the folder, but just in case)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            print(f"Metadata file {metadata_path} removed", file=sys.stderr)
    except Exception as e:
        print(f"Error removing project folder or metadata: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    
    return {
        "success": True,
        "project": removed_project,
        "folder_removed": folder_removed
    }

def get_web_url_for_output(file_path):
    """Convert a local output file path to a web-accessible URL."""
    if not os.path.exists(file_path):
        return None
    WEB_BASE_URL = os.environ.get("WEB_BASE_URL")
    if not WEB_BASE_URL:
        host_ip = get_host_ip()
        WEB_BASE_URL = f"http://{host_ip}:8000/output/"
    filename = os.path.basename(file_path)
    return WEB_BASE_URL.rstrip("/") + f"/{filename}"

@mcp.tool()
def analyze_dependencies(project_id: str) -> dict:
    logging.debug(f"analyze_dependencies called for project_id={project_id}")
    print(f"analyze_dependencies called for project_id={project_id}", file=sys.stderr)

    # Check if project exists
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        logging.error(f"Project not found: {project_id}")
        return {"error": f"Project not found: {project_id}"}

    project_dir = project["path"]
    script_path = os.path.join(os.getcwd(), "scripts", "dependency-workflow.cjs")
    cmd = ["node", script_path, "--root-dir", project_dir, "--skip-build"]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        output = result.stdout
        # Save output to analysis_results.json
        analysis_path = os.path.join(DATA_DIR, project_id, "analysis_results.json")
        with open(analysis_path, "w") as f:
            f.write(output)
        logging.debug(f"Saved analysis results to {analysis_path}")
        print(f"Saved analysis results to {analysis_path}", file=sys.stderr)

        # Attempt to extract summary from workflow output or report files
        summary = {}
        summary_url = None
        try:
            # Look for workflow-summary.md in the project
            summary_path = os.path.join(project_dir, "output", "workflow-summary.md")
            if os.path.exists(summary_path):
                with open(summary_path, "r") as f:
                    summary_content = f.read()
                import re
                files_analyzed = re.search(r"Initial orphaned file candidates: (\d+)", summary_content)
                enhanced_orphans = re.search(r"Enhanced orphaned file candidates: (\d+)", summary_content)
                confirmed_orphans = re.search(r"Confirmed orphaned files: (\d+)", summary_content)
                summary = {
                    "files_analyzed": int(files_analyzed.group(1)) if files_analyzed else None,
                    "enhanced_orphaned_files": int(enhanced_orphans.group(1)) if enhanced_orphans else None,
                    "confirmed_orphaned_files": int(confirmed_orphans.group(1)) if confirmed_orphans else None,
                    "summary_path": summary_path
                }
                summary_url = get_web_url_for_output(summary_path)
            else:
                summary = {"info": "workflow-summary.md not found"}
        except Exception as e:
            summary = {"error": f"Failed to extract summary: {str(e)}"}

        # Also include paths to key reports if they exist, as web URLs
        report_dir = os.path.join(project_dir, "output")
        key_reports = [
            "enhanced-orphaned-files.md",
            "dependency-graph.json",
            "duplicate-files.md",
            "final-orphaned-files.md",
            "confirmed-orphaned-files.md",
            "build-dependencies.md",
            "dynamic-references.md",
            "route-component-verification.md",
            "FILE_CLEANUP_REPORT.md"
        ]
        report_urls = {}
        for report in key_reports:
            report_path = os.path.join(report_dir, report)
            url = get_web_url_for_output(report_path)
            if url:
                report_urls[report] = url
        return {
            "success": True,
            "project_id": project_id,
            "output": output,
            "analysis_path": analysis_path,
            "summary": summary,
            "summary_url": summary_url,
            "report_urls": report_urls
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"Dependency analysis failed: {e.stderr}")
        return {
            "success": False,
            "error": "Dependency analysis failed",
            "details": e.stderr
        }

@mcp.tool()
def get_dependency_graph(project_id: str) -> dict:
    logging.debug(f"get_dependency_graph called for project_id={project_id}")
    print(f"get_dependency_graph called for project_id={project_id}", file=sys.stderr)
    
    # Check if project exists
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        logging.error(f"Project not found: {project_id}")
        return {"graph": {"nodes": [], "edges": []}}
    
    # Check if analysis results exist
    analysis_path = os.path.join(DATA_DIR, project_id, "analysis_results.json")
    if os.path.exists(analysis_path):
        try:
            with open(analysis_path, "r") as f:
                analysis = json.load(f)
            return {"graph": analysis.get("graph", {"nodes": [], "edges": []})}
        except Exception as e:
            logging.error(f"Error loading analysis results: {str(e)}")
    
    # Return empty graph if no analysis exists
    return {"graph": {"nodes": [], "edges": []}}

@mcp.tool()
def find_orphaned_files(project_id: str) -> dict:
    logging.debug(f"find_orphaned_files called for project_id={project_id}")
    print(f"find_orphaned_files called for project_id={project_id}", file=sys.stderr)
    
    # Check if project exists
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        logging.error(f"Project not found: {project_id}")
        return {"orphaned_files": []}
    
    # Return mock orphaned files
    orphaned_files = [
        {"path": "unused.js", "type": "JavaScript"},
        {"path": "old_utils.js", "type": "JavaScript"}
    ]
    
    # Save orphaned files list to project folder
    project_dir = os.path.join(DATA_DIR, project_id)
    orphaned_path = os.path.join(project_dir, "orphaned_files.json")
    
    try:
        with open(orphaned_path, "w") as f:
            json.dump({"orphaned_files": orphaned_files}, f)
        logging.debug(f"Saved orphaned files to {orphaned_path}")
        print(f"Saved orphaned files to {orphaned_path}", file=sys.stderr)
    except Exception as e:
        logging.error(f"Failed to save orphaned files: {str(e)}")
        print(f"Failed to save orphaned files: {str(e)}", file=sys.stderr)
    
    return {"orphaned_files": orphaned_files}

@mcp.tool()
def check_circular_dependencies(project_id: str) -> dict:
    logging.debug(f"check_circular_dependencies called for project_id={project_id}")
    print(f"check_circular_dependencies called for project_id={project_id}", file=sys.stderr)
    
    # Check if project exists
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        logging.error(f"Project not found: {project_id}")
        return {"circular_dependencies": []}
    
    # Return mock circular dependencies
    circular_deps = [
        {
            "cycle": ["moduleA.js", "moduleB.js", "moduleC.js", "moduleA.js"],
            "severity": "high"
        }
    ]
    
    # Save circular dependencies to project folder
    project_dir = os.path.join(DATA_DIR, project_id)
    circular_path = os.path.join(project_dir, "circular_dependencies.json")
    
    try:
        with open(circular_path, "w") as f:
            json.dump({"circular_dependencies": circular_deps}, f)
        logging.debug(f"Saved circular dependencies to {circular_path}")
        print(f"Saved circular dependencies to {circular_path}", file=sys.stderr)
    except Exception as e:
        logging.error(f"Failed to save circular dependencies: {str(e)}")
        print(f"Failed to save circular dependencies: {str(e)}", file=sys.stderr)
    
    return {"circular_dependencies": circular_deps}

@mcp.tool()
def archive_orphaned_files(project_id: str) -> dict:
    logging.debug(f"archive_orphaned_files called for project_id={project_id}")
    print(f"archive_orphaned_files called for project_id={project_id}", file=sys.stderr)

    # Check if project exists
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        logging.error(f"Project not found: {project_id}")
        return {"success": False, "error": f"Project not found: {project_id}"}

    project_dir = project["path"]
    script_path = os.path.join(os.getcwd(), "scripts", "batch-archive-orphaned.cjs")
    output_dir = os.path.join(project_dir, "output")
    report_path = os.path.join(output_dir, "FILE_CLEANUP_REPORT.md")

    try:
        result = subprocess.run([
            "node", script_path
        ], check=True, capture_output=True, text=True, cwd=project_dir)
        output = result.stdout
        # Check if the report was generated
        report_url = get_web_url_for_output(report_path)
        return {
            "success": True,
            "output": output,
            "report_url": report_url
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"Archival failed: {e.stderr}")
        return {
            "success": False,
            "error": "Archival failed",
            "details": e.stderr
        }

# Check /data volume is accessible
print(f"Starting server...", file=sys.stderr)
print(f"Checking /data directory:", file=sys.stderr)
print(f"  Exists: {os.path.exists(DATA_DIR)}", file=sys.stderr)
print(f"  Writable: {os.access(DATA_DIR, os.W_OK)}", file=sys.stderr)
print(f"  Contents: {os.listdir(DATA_DIR)}", file=sys.stderr)

# Create default project folders for existing projects
for project in projects:
    project_dir = os.path.join(DATA_DIR, project["id"])
    if not os.path.exists(project_dir):
        create_project_folder(project["id"], project)

if __name__ == "__main__":
    mcp.run() 