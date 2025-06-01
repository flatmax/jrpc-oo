import os
import subprocess
import sys
import platform


class Cert:
    """Class to manage SSL certificates for WSS connections using mkcert.
    
    This class provides functionality to generate and manage trusted SSL certificates
    for secure WebSocket connections to browsers using the mkcert tool.
    """
    
    def __init__(self, domain="localhost", cert_dir=None):
        """Initialize the Cert class.
        
        Args:
            domain (str): Domain or hostname for the certificate
            cert_dir (str): Directory to store certificates, defaults to a 'certs' folder
        """
        self.domain = domain
        if cert_dir is None:
            # Default to a 'certs' directory in the current directory
            self.cert_dir = os.path.join(os.getcwd(), "certs")
        else:
            self.cert_dir = cert_dir
            
        # Ensure the certificate directory exists
        os.makedirs(self.cert_dir, exist_ok=True)
        
        # Certificate paths
        self.cert_path = os.path.join(self.cert_dir, f"{domain}.pem")
        self.key_path = os.path.join(self.cert_dir, f"{domain}-key.pem")
    
    def check_mkcert(self):
        """Check if mkcert is installed and available.
        
        Returns:
            bool: True if mkcert is installed, False otherwise
        """
        try:
            subprocess.run(["mkcert", "-version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=False)
            return True
        except FileNotFoundError:
            return False
    
    def install_mkcert(self):
        """Provide instructions on how to install mkcert based on the platform.
        
        Returns:
            str: Installation instructions
        """
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return ("Install mkcert using Homebrew:\n"
                   "brew install mkcert\n"
                   "mkcert -install")
        elif system == "linux":
            return ("Install mkcert using one of these methods:\n"
                   "1. Using Homebrew: brew install mkcert\n"
                   "2. Using Linuxbrew: brew install mkcert\n"
                   "3. Download from GitHub: https://github.com/FiloSottile/mkcert/releases\n"
                   "Then run: mkcert -install")
        elif system == "windows":
            return ("Install mkcert using one of these methods:\n"
                   "1. Using Chocolatey: choco install mkcert\n"
                   "2. Using Scoop: scoop bucket add extras && scoop install mkcert\n"
                   "3. Download from GitHub: https://github.com/FiloSottile/mkcert/releases\n"
                   "Then run: mkcert -install")
        else:
            return "Please visit https://github.com/FiloSottile/mkcert for installation instructions."
    
    def generate_cert(self):
        """Generate SSL certificates for the specified domain.
        
        Returns:
            tuple: (success, message)
                success (bool): True if certificates were generated successfully
                message (str): Information about the operation
        """
        if not self.check_mkcert():
            instructions = self.install_mkcert()
            return False, f"mkcert is not installed. {instructions}"
        
        try:
            # Install the local CA if not already done
            subprocess.run(["mkcert", "-install"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            
            # Generate certificate for the domain
            subprocess.run(
                ["mkcert", "-cert-file", self.cert_path, "-key-file", self.key_path, 
                 self.domain, f"*.{self.domain}", "localhost", "127.0.0.1", "::1"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=True
            )
            
            return True, f"Certificates generated successfully:\nCertificate: {self.cert_path}\nKey: {self.key_path}"
        except subprocess.CalledProcessError as e:
            return False, f"Error generating certificates: {e.stderr.decode('utf-8') if e.stderr else str(e)}"
    
    def get_cert_paths(self):
        """Get the paths to the certificate and key files.
        
        Returns:
            tuple: (cert_path, key_path)
        """
        return self.cert_path, self.key_path


if __name__ == "__main__":
    # Example usage when the script is run directly
    domain = "localhost"
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    
    cert_manager = Cert(domain)
    success, message = cert_manager.generate_cert()
    print(message)
    
    if success:
        cert_path, key_path = cert_manager.get_cert_paths()
        print(f"\nUse these paths in your WebSocket server configuration:")
        print(f"Certificate: {cert_path}")
        print(f"Key: {key_path}")
