import libtorrent as lt
import os
import sys
import qbittorrentapi

class TorrentCreator:
    def __init__(self, announce_url=None):
        self.announce_url = announce_url or "udp://tracker.openbittorrent.com:80"
    
    def create_torrent(self, file_path, output_dir="./"):
        """Create a torrent file from a file or directory"""
        
        # Create file storage
        fs = lt.file_storage()

        for directory in open("tracked_directories.txt", "r", encoding='utf-8'):
            lt.add_files(fs, directory.strip("\n"))
        torrent_name = os.path.basename(file_path)
        # Show files added to storage
        print(f"\nFiles added to torrent:")
        print(f"Total files: {fs.num_files()}")
        print(f"Total size: {fs.total_size() / (1024*1024):.2f} MB")

        # Create torrent
        t = lt.create_torrent(fs)
        t.add_tracker(self.announce_url)
        t.set_creator("LibTorrent Python Creator")
        t.set_comment("Created with libtorrent-python")
        
        # Calculate piece hashes
        parent_dir = os.path.dirname(os.path.abspath(file_path))
        lt.set_piece_hashes(t, parent_dir)
        
        # Generate torrent data
        torrent_data = lt.bencode(t.generate())
        
        # Save torrent file
        torrent_filename = os.path.join(output_dir, f"{torrent_name}.torrent")
        with open(torrent_filename, 'wb') as f:
            f.write(torrent_data)
        
        print(f"Created torrent: {torrent_filename}")
        return torrent_filename
    
    def create_magnet_link(self, torrent_file):
        """Generate magnet link from torrent file"""
        info = lt.torrent_info(torrent_file)
        magnet = f"magnet:?xt=urn:btih:{info.info_hash()}&dn={info.name()}"
        
        # Add trackers
        for tier in info.trackers():
            magnet += f"&tr={tier.url}"
        
        return magnet

# def add_to_qbittorrent(self, torrent_file, download_path):
#     """Add torrent to qBittorrent and start seeding"""
    
#     with qbittorrentapi.Client(**self.qbt_config) as qbt_client:
#         try:
#             # Add torrent file
#             result = qbt_client.torrents_add(
#                 torrent_files=torrent_file,
#                 save_path=download_path,
#                 is_paused=False  # Start immediately
#             )
            
#             if result == "Ok.":
#                 print(f"Successfully added torrent to qBittorrent")
#                 print(f"Download path: {download_path}")
#                 return True
#             else:
#                 print(f"Failed to add torrent: {result}")
#                 return False
                
#         except Exception as e:
#             print(f"Error adding torrent to qBittorrent: {e}")
#             return False
# Usage example

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python torrent_creator.py <file_or_directory> [tracker_url]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    tracker = sys.argv[2] if len(sys.argv) > 2 else None
    
    creator = TorrentCreator(tracker)
    torrent_file = creator.create_torrent(file_path)
    magnet = creator.create_magnet_link(torrent_file)
    
    print(f"Magnet Link: {magnet}")