import os
from re import match
import subprocess # To run commands in powershell
import shutil # To manage files


class WebBlocker:
    def __init__(self, blocked_sites):
        self._blocked_sites = blocked_sites
        self._hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        self._backup_path = r"C:\Windows\System32\drivers\etc\hosts_backup"
        self.redirect_ip = "127.0.0.1"
        self.show_prints = True
        self.create_backup()
        self.state = "Off"

    # Need to be called after blocking/unblocking.
    # Flushes the DNS cache so changes take effect.
    def flush_dns(self): 
        ip_flusher = subprocess.run(
        ["ipconfig", "/flushdns"],
        capture_output=True, # Capture the output of the command
        text=False, # Get text as bytes to decode later
        shell=True  # Windows compatibility for ipconfig
        )

        print(ip_flusher.stdout.decode("utf-8")) # Prnt the output of the command.
        print(ip_flusher.stderr.decode("utf-8")) # Print the error of the command.
    
    # Function to create a backup of the hosts file before making any changes.
    def create_backup(self):
        if not os.path.exists(self._backup_path):
            shutil.copy(self._hosts_path, self._backup_path)
            if self.show_prints:
                print("Backup created successfully.")
        else:
            if self.show_prints:
                print("Backup already exists.")

    # Function to restore the backup in case of errors during unblocking, ensuring system stability.
    def restore_backup(self):
        if os.path.exists(self._backup_path):
            shutil.copy(self._backup_path, self._hosts_path)
            if self.show_prints:
                print("Backup restored successfully.")
        else:
            if self.show_prints:
                print("No backup found to restore.")

    # Writes to hosts file and adds the blocklist.
    def block_websites(self):
        with open(self._hosts_path, "r+") as file:
            content = file.read()
            for site in self._blocked_sites:
                if site not in content:
                    file.write(self.redirect_ip + " " + site + "\n")

        if self.show_prints:
            print("Websites blocked successfully.")

    # Removes the blocked websites from host file.
    # ---------------- NB needs to be run on program crash, uninstall or close.
    def unblock_websites(self):
        try:
            with open(self._hosts_path, "r") as file:
                lines = file.readlines()
            with open(self._hosts_path, "w") as file:
                for line in lines:
                    if not any(site in line for site in self._blocked_sites):
                        file.write(line)
            

            if self.show_prints:
                print("Websites unblocked successfully.")
        except Exception as e:
            if self.show_prints:
                print(f"An error occurred while unblocking websites: {e}\n")
                print("Restoring backup to ensure system stability.")
                self.restore_backup()
        self.flush_dns()


    # Adds new sites to the hosts file
    def add_blocked_site(self, site):
        if site not in self._blocked_sites:
            format1 = site if site.startswith("www.") else "www." + site
            format2 = site if not site.startswith("www.") else site[4:]
            self._blocked_sites.extend([format1, format2])
            self._blocked_sites = list(set(self._blocked_sites)) # Remove duplicates
            self.block_websites() # Update the hosts file with the new blocked site

            if self.show_prints:
                print(f"{site} added to blocked sites.")
        else:
            if self.show_prints:
                print(f"{site} is already in the blocked sites list.")

    
    def test_menu(self):
        while True:
            try:
                print("\nBlocked Sites:")
                for site in self._blocked_sites:
                    print(f"- {site}")
                print("\nOptions:")
                print("1. Add a blocked site")
                print(f"2. Toggle block/unblock all sites | {self.state}")
                print("3. Exit")
                choice = input("\nEnter your choice: ")

                match choice:
                    case "1":
                        new_site = input("Enter the website to block (e.g., example.com): ")
                        self.add_blocked_site(new_site)
                    case "2":
                        if self.state == "Off":
                            self.block_websites()
                            self.state = "On"
                        else:
                            self.unblock_websites()
                            self.state = "Off"
                    case "3":
                        print("Exiting the program.")
                        break
                    case _:
                        print("Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\nExiting the program. Keyboard interupt\n")
                self.unblock_websites() # Ensure websites are unblocked on exit
                self.flush_dns() # Flush DNS after unblocking sites
                break


if __name__ == "__main__":
    blocked_sites = [
        "www.facebook.com",
        "facebook.com",
        "www.youtube.com",
        "youtube.com",
    ]
    blocker = WebBlocker(blocked_sites)
    blocker.test_menu()
