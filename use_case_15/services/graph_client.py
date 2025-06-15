import requests
import msal
import time


class MSGraphClient:
    """
    A client to authenticate and interact with Microsoft Graph API.
    Supports acquiring site and drive IDs.
    """

    def __init__(self, tenant_id, client_id, client_secret):
        """
        Initialize the MSGraphClient and authenticate with Microsoft identity platform.
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = 0
        self.headers = None
        self.authenticate()

    def authenticate(self):
        """
        Authenticate using client credentials flow and obtain an access token.
        """
        try:
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=authority,
                client_credential=self.client_secret,
            )
            token_response = app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )

            if "access_token" not in token_response:
                raise Exception(
                    "Authentication failed: "
                    + token_response.get("error_description", "Unknown error")
                )

            self.access_token = token_response["access_token"]
            self.token_expires_at = (
                time.time() + token_response.get("expires_in", 3600) - 300
            )
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
            print("Authenticated successfully")

        except Exception as e:
            print(f"Authentication error: {e}")
            raise

    def ensure_valid_token(self):
        """
        Ensures the access token is valid, refreshing if necessary.
        """
        if not self.access_token or time.time() >= self.token_expires_at:
            print("Token expired or missing, refreshing...")
            self.authenticate()

    def get(self, url):
        """
        Perform a GET request to the specified Graph API URL with auth headers.
        """
        self.ensure_valid_token()
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self.authenticate()
            response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def post(self, url, json=None):
        """
        Perform a POST request to the specified Graph API URL with auth headers.
        """
        self.ensure_valid_token()
        response = requests.post(url, headers=self.headers, json=json)
        if response.status_code == 401:
            self.authenticate()
            response = requests.post(url, headers=self.headers, json=json)
        response.raise_for_status()
        return response

    def put(self, url, data=None):
        """
        Perform a PUT request to the specified Graph API URL with auth headers.
        """
        self.ensure_valid_token()
        response = requests.put(url, headers=self.headers, data=data)
        if response.status_code == 401:
            self.authenticate()
            response = requests.put(url, headers=self.headers, data=data)
        response.raise_for_status()
        return response

    def get_site_id(self, hostname, site_name):
        """
        Retrieve the site ID for a given SharePoint hostname and site name.
        """
        site_path = f"/sites/{site_name.replace(' ', '')}"
        url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:{site_path}"
        res = self.get(url)
        site_data = res.json()
        site_id = site_data.get("id")
        if not site_id:
            raise Exception("Could not resolve site ID.")
        return site_id

    def get_drive_id(self, site_id, drive_name="Documents"):
        """
        Retrieve the drive ID by name (default is 'Documents') for a given site.
        """
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        res = self.get(url)
        drives = res.json().get("value", [])
        drive = next(
            (drive for drive in drives if drive.get("name") == drive_name), None
        )
        if not drive:
            raise Exception(f"Drive {drive_name} not found.")
        return drive["id"]

    def get_folder_by_name(self, drive_id, folder_name, parent_id=None):
        """
        Check if a folder exists and return its ID if found.

        Args:
            drive_id: The ID of the drive
            folder_name: The name of the folder to find
            parent_id: Optional parent folder ID (for subfolders)

        Returns:
            str: Folder ID if found, None otherwise
        """
        try:
            if parent_id:
                url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{parent_id}/children"
            else:
                url = (
                    f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
                )
            response = self.get(url)
            items = response.json().get("value", [])
            for item in items:
                if item.get("folder") and item.get("name") == folder_name:
                    return item.get("id")
            return None
        except Exception as e:
            print(f"Error checking folder existence: {e}")
            return None

    def create_root_folder(self, drive_id, folder_name):
        """
        Create a folder at the root level of the specified drive.
        If folder already exists, return its ID.

        Args:
            drive_id: The ID of the drive
            folder_name: The name of the folder to create

        Returns:
            str: The ID of the created or existing folder
        """
        try:
            existing_folder_id = self.get_folder_by_name(drive_id, folder_name)
            if existing_folder_id:
                return existing_folder_id
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
            payload = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename",
            }
            response = self.post(url, payload)
            return response.json().get("id")
        except requests.exceptions.HTTPError as e:
            print(f"Error creating root folder '{folder_name}': {e}")
            if e.response.status_code == 409:
                existing_folder_id = self.get_folder_by_name(drive_id, folder_name)
                if existing_folder_id:
                    return existing_folder_id
            raise

    def create_subfolder(self, drive_id, parent_folder_id, folder_name):
        """
        Create a subfolder within an existing folder.
        If folder already exists, return its ID.

        Args:
            drive_id: The ID of the drive
            parent_folder_id: The ID of the parent folder
            folder_name: The name of the subfolder to create

        Returns:
            str: The ID of the created or existing subfolder
        """
        try:
            existing_folder_id = self.get_folder_by_name(
                drive_id, folder_name, parent_folder_id
            )
            if existing_folder_id:
                return existing_folder_id
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{parent_folder_id}/children"
            payload = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename",
            }
            response = self.post(url, payload)
            return response.json().get("id")

        except requests.exceptions.HTTPError as e:
            print(f"Error creating subfolder '{folder_name}': {e}")
            if e.response.status_code == 409:
                existing_folder_id = self.get_folder_by_name(
                    drive_id, folder_name, parent_folder_id
                )
                if existing_folder_id:
                    return existing_folder_id
            raise

    def upload_file_to_folder(self, drive_id, folder_id, file_name, content):
        """
        Upload a file directly to a specific folder using its ID.

        Args:
            drive_id: The ID of the drive
            folder_id: The ID of the target folder
            file_name: The name of the file to create
            content: The content of the file
        """
        try:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}:/{file_name}:/content"
            response = self.put(url, data=content)
            return response.json().get("id")
        except requests.exceptions.HTTPError as e:
            print(f"Error uploading file '{file_name}' to folder: {e}")
            raise

    def upload_file_to_drive(self, file_path, file_data):
        try:
            requests.put(file_path, headers=self.headers, data=file_data)
        except Exception as e:
            print("Could not upload file to drive.", e)

    def delete_file(self, url):
        """
        Delete a file or folder from SharePoint using its URL.

        Args:
            url (str): The full URL of the file/folder to delete

        Returns:
            bool: True if deletion was successful
        """
        try:
            self.ensure_valid_token()
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 401:
                self.authenticate()
                response = requests.delete(url, headers=self.headers)
            if response.status_code in [404]:
                return False
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            print(f"Error deleting file: {e}")
            raise

    def list_files(self, drive_id, folder_id=None):
        """
        List all files in a SharePoint drive or specific folder.

        Args:
            drive_id (str): The ID of the drive to list files from
            folder_id (str, optional): The ID of the folder to list files from. If None, lists from root.

        Returns:
            list: List of file items with their metadata
        """
        try:
            if folder_id:
                url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"
            else:
                url = (
                    f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
                )

            response = self.get(url)
            items = response.json().get("value", [])

            while "@odata.nextLink" in response.json():
                next_link = response.json()["@odata.nextLink"]
                response = self.get(next_link)
                items.extend(response.json().get("value", []))

            return items
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def download_file(self, drive_id, file_id):
        """
        Download a file from SharePoint by its ID.

        Args:
            drive_id (str): The ID of the drive containing the file
            file_id (str): The ID of the file to download

        Returns:
            bytes: The file content as bytes, or None if download fails
        """
        try:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}"
            response = self.get(url)
            download_url = response.json().get("@microsoft.graph.downloadUrl")

            if not download_url:
                print(f"Could not get download URL for file {file_id}")
                return None

            response = requests.get(download_url)
            response.raise_for_status()
            return response

        except Exception as e:
            print(f"Error downloading file: {e}")
            return None

    def _list_folder_contents(self, drive_id, folder_id=None, path=""):
        """
        Helper method to recursively list contents of a folder.

        Args:
            drive_id (str): The ID of the drive
            folder_id (str, optional): The ID of the folder to list contents from
            path (str): Current path in the folder structure

        Returns:
            list: List of all items (files and folders) with their metadata and paths
        """
        try:
            if folder_id:
                url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"
            else:
                url = (
                    f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
                )

            response = self.get(url)
            items = response.json().get("value", [])
            while "@odata.nextLink" in response.json():
                next_link = response.json()["@odata.nextLink"]
                response = self.get(next_link)
                items.extend(response.json().get("value", []))
            all_items = []
            for item in items:
                item["folder_path"] = path
                if "folder" in item:
                    folder_path = f"{path}/{item['name']}" if path else item["name"]
                    folder_items = self._list_folder_contents(
                        drive_id, item["id"], folder_path
                    )
                    all_items.extend(folder_items)
                all_items.append(item)
            return all_items

        except Exception as e:
            print(f"Error listing folder contents: {e}")
            return []

    def list_all_files_recursive(self, drive_id):
        """
        List all files and folders in a SharePoint drive recursively.

        Args:
            drive_id (str): The ID of the drive to list files from

        Returns:
            list: List of all items (files and folders) with their metadata and paths
        """
        print("Fetching all files and folders recursively...")
        items = self._list_folder_contents(drive_id)
        items = [item for item in items if item.get("name") != "document_list.json"]
        file_count = sum(1 for item in items if "file" in item)
        folder_count = sum(1 for item in items if "folder" in item)
        print(f"Found {file_count} files in {folder_count} folders")
        return items
