#!/usr/bin/env python3

import argparse
import requests
import sys
from urllib.parse import urljoin

def get_args():
    """
    Get command line arguments.
    """
    parser = argparse.ArgumentParser(description="Generate a Rancher RBAC report.")
    parser.add_argument("-u", "--url", required=True, help="Rancher URL")
    parser.add_argument("-t", "--token", required=True, help="Rancher API Bearer Token")
    parser.add_argument("-o", "--output", default="rbac_report.md", help="Output file name (default: rbac_report.md)")
    return parser.parse_args()

def get_authenticated_session(url, token):
    """
    Create an authenticated session for Rancher API.
    """
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    session.verify = False  # Consider using proper certificate validation in a production environment
    # Test connection
    try:
        response = session.get(urljoin(url, "/v3/clusters"))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Rancher API: {e}", file=sys.stderr)
        sys.exit(1)
    return session

def get_all_data(session, url, resource_type):
    """
    Fetch all data for a given resource type, handling pagination.
    """
    all_data = []
    next_url = urljoin(url, f"/v3/{resource_type}")
    while next_url:
        try:
            response = session.get(next_url)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data.get("data", []))
            next_url = data.get("pagination", {}).get("next")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {resource_type}: {e}", file=sys.stderr)
            return []
    return all_data

def generate_report(args, session):
    """
    Generates the RBAC report.
    """
    # Fetch all necessary data
    global_roles = get_all_data(session, args.url, "globalroles")
    global_role_bindings = get_all_data(session, args.url, "globalrolebindings")
    users = get_all_data(session, args.url, "users")
    clusters = get_all_data(session, args.url, "clusters")
    crtbs = get_all_data(session, args.url, "clusterroletemplatebindings")
    prtbs = get_all_data(session, args.url, "projectroletemplatebindings")

    # Create lookups for easier access
    user_lookup = {user["id"]: user for user in users}
    global_role_lookup = {role["id"]: role for role in global_roles}
    cluster_lookup = {cluster["id"]: cluster for cluster in clusters}

    with open(args.output, "w") as f:
        f.write("# Rancher RBAC Report\n\n")

        # Global Permissions
        f.write("## Global Permissions\n\n")
        for grb in global_role_bindings:
            user_id = grb.get("userId")
            group_principal_id = grb.get("groupPrincipalId")
            global_role_id = grb.get("globalRoleId")

            user_name = user_lookup.get(user_id, {}).get("username", "N/A") if user_id else "N/A"
            role_name = global_role_lookup.get(global_role_id, {}).get("name", "N/A")

            if user_id:
                f.write(f"- **User:** {user_name} ({user_id})\n")
            elif group_principal_id:
                f.write(f"- **Group:** {group_principal_id}\n")

            f.write(f"  - **Global Role:** {role_name}\n\n")

        # Cluster and Project Permissions
        f.write("## Cluster and Project Permissions\n\n")
        for cluster in clusters:
            f.write(f"### Cluster: {cluster['name']} ({cluster['id']})\n\n")

            # Cluster-level permissions
            f.write("#### Cluster-Level Roles\n\n")
            for crtb in crtbs:
                if crtb["clusterId"] == cluster["id"]:
                    user_id = crtb.get("userId")
                    group_principal_id = crtb.get("groupPrincipalId")
                    role_template_id = crtb.get("roleTemplateId")

                    user_name = user_lookup.get(user_id, {}).get("username", "N/A") if user_id else "N/A"

                    if user_id:
                        f.write(f"- **User:** {user_name} ({user_id})\n")
                    elif group_principal_id:
                        f.write(f"- **Group:** {group_principal_id}\n")

                    f.write(f"  - **Cluster Role:** {role_template_id}\n\n")

            # Project-level permissions
            f.write("#### Project-Level Roles\n\n")
            cluster_projects = get_all_data(session, args.url, f"clusters/{cluster['id']}/projects")
            project_lookup = {p["id"]: p for p in cluster_projects}

            for prtb in prtbs:
                project_id = prtb.get("projectId")
                if project_id and project_id.startswith(cluster["id"]):
                    project = project_lookup.get(project_id)
                    if project:
                        user_id = prtb.get("userId")
                        group_principal_id = prtb.get("groupPrincipalId")
                        role_template_id = prtb.get("roleTemplateId")

                        user_name = user_lookup.get(user_id, {}).get("username", "N/A") if user_id else "N/A"

                        f.write(f"- **Project:** {project['name']}\n")
                        if user_id:
                            f.write(f"  - **User:** {user_name} ({user_id})\n")
                        elif group_principal_id:
                            f.write(f"  - **Group:** {group_principal_id}\n")

                        f.write(f"  - **Project Role:** {role_template_id}\n\n")

def main():
    """
    Main function.
    """
    args = get_args()
    session = get_authenticated_session(args.url, args.token)
    generate_report(args, session)
    print(f"RBAC report generated successfully: {args.output}")

if __name__ == "__main__":
    main()


